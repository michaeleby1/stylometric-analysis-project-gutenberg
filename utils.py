import os
import glob
import re
from gutenberg.cleanup import strip_headers
import wikipedia
PageError = wikipedia.exceptions.PageError
DisambiguationError = wikipedia.DisambiguationError
WikipediaException = wikipedia.exceptions.WikipediaException
import pymongo
import time
import pandas as pd
from sklearn import preprocessing, metrics
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process

# ----------------------
# ETL PIPELINE
# ----------------------

client = pymongo.MongoClient('mongodb://localhost/')
db = client['gutenberg_db']
collection = db['gutenberg_collection']


def author_title_year(file):
    with open(file, 'r') as f:
        text = f.read()
    author = re.findall(r'(?:Author: )(.*)(?:\n)', text)[0].strip()
    title = re.findall(r'(?:Title: )(.*)(?:\n)', text)[0].strip()
    
    ## queries wikipedia summaries for year; books without without 
    ## summaries will throw an error later and won't enter the database
    summary = str(wikipedia.summary(title))
    year = re.search(r'(\s\d{4})', summary).group().strip()
    return author, title, year


def clean_text(file):
    with open(file, 'r') as f:
        text = strip_headers(f.read())
        
    ## removes newline characters, underscores, other misc characters/words
    chars = ['\n', '_', '\*+', '\[', '\]', 'Illustration: ', 'ILLUSTRATION: ',
             'Footnote: ', 'FOOTNOTE: ', 'Project Gutenberg', 'PROJECT GUTENBERG']
    text = re.compile('|'.join(chars)).sub(' ', text)
    
    ## removes text from title page
    author, title, year = author_title_year(file)
    titlePage = [title, title.upper(), ' by ', ' By ', ' BY ', author, 
                 author.upper(), year, 'Translated ', 'TRANSLATED ', 
                 'Illustrated ', 'ILLUSTRATED ', 'ILLUSTRATIONS ', 
                 'Edited ', 'EDITED ', 'published '
                 'Table of Contents ', 'TABLE OF CONTENTS', 'CONTENTS'
                 'Author of ', 'Online Distributed Proofreading Team',  
                 'Distributed Proofreading Online Team'
                 'Proofreading ', 'Proofreaders ', 'Distributed Proofreaders', 
                 'Distributed Proofreading ']
    text =  re.compile('|'.join(titlePage)).sub(' ', text[:1000])+text[1000:]  
    
    ## removes chapter headings 
    chapterHeadings = ['CHAPTER \d+', 'Chapter \d+', 'CHAPTER \w+',
                       'Chapter \w+','BOOK \d+', 'Book \d+', 'BOOK \w+', 
                       'Book \w+', 'VOLUME \d+', 'Volume \d+', 'VOLUME \w+', 
                       'Volume \w+', 'ACT \d+', 'Act \d+', 'ACT \w+', 
                       'Act \w+', 'PART \d+', 'Part \d+', 'PART \w+', 
                       'Part \w+','I\.', 'II\.', 'III\.', 'IV\.', 'V\.', 
                       'VI\.', 'VII\.', 'VIII\.', 'IX\.', 'X\.', 'XI\.',
                       'XII', 'XII\.', 'XIII\.', 'XIV\.', 'XV\.', 'XVI\.',
                       'XVII\.', 'XVIII\.', 'XIX\.', 'XX\.', 'XXI\.', 'XXII\.',
                       'XXIII\.', 'XXIV\.', 'XXV\.']
    text = re.compile('|'.join(chapterHeadings)).sub(' ', text)
    
    ## truncates multiple spaces into one; will make analysis at the character level easier
    text = re.compile('\s+').sub(' ', text)               
    return text.strip()


## Process a file and upload to mongo
def mongo_upload(file, collection=collection):  
    ## these errors will correspond to missing metadata; if a file doesn't
    ## have all the metadata I want, it will not load into Mongo
    
        
    dict_ = {'file': '', 'author': '', 'title': '', 'year': '', 'text': ''}

    try:
        s = time.time()
        author, title, year = author_title_year(file)
        print(title)
        dict_['file'] = file
        dict_['author'] = author
        dict_['title'] = title
        dict_['year'] = year
        dict_['text'] = clean_text(file)
        print(f'Took {time.time() - s} to process')
        
        collection.insert_one(dict_)
        
    ## quality filtering; if a text doesn't have both author and title 
    ## python will throw KeyError, IndexError, and the text it will 
    ## not enter the database
    except (KeyError, IndexError) as e:
        pass

    ## this removes duplicate encodings from the dict; all filenames throwing 
    ## this error end in "-8" or "-0", and there seems to be ASCII versions of them
    except UnicodeDecodeError as e2:
        pass

    ## more quality filtering; if the book is not first wikipedia search result
    ## or doesn't have a wikipedia page it will not enter the database
    except (AttributeError, PageError, DisambiguationError, WikipediaException) as e3:
        pass

# ----------------------
#  CLUSTERS
# ----------------------

def cluster_names(row):
    if row == 0:
        return 'High complexity prose'
    elif row == 1:
        return 'Moderate complexity prose'
    elif row == 2:
        return 'History'
    elif row == 3:
        return 'Manuals'
    elif row == 4:
        return 'Rhetorical works'
    elif row == 5:
        return 'Belles-lettres'
    elif row == 6:
        return 'Drama'

# ----------------------
#  RECOMMENDATION ENGINE
# ----------------------

df = pd.read_csv('metrics/metrics_clusters.csv')

## Standard scaling style metics
style_metrics = df.iloc[:, 4:-1].values
scaler = preprocessing.StandardScaler()
metrics_scaled = scaler.fit_transform(style_metrics)
df_scaled = pd.DataFrame(metrics_scaled, columns=df.columns[4:-1])
df_scaled = pd.concat([df.iloc[:,:4], df_scaled], axis=1)

df_scaled_subset = df_scaled[['sttr', 'hapax_legomenon', 'yules_k',
                              'avg_sentence_length_word', 'avg_sentence_length_chars', 
                              'avg_syllables_per_word', 'punctuation_sentence', 'shannon_entropy', 
                              'simpsons_d', 'average_nps', 'noun_to_verb', 'noun_to_adj', 
                              'verb_to_adv','avg_dependency_distance']]

## gets cosine similarity between titles
cosine_sim = cosine_similarity(df_scaled_subset)
## reerse mapping titles to indices
indices = pd.Series(df.index, index=df['title'])

def book_lookup(input_title, cosine_sim=cosine_sim):
    ## fuzzy matching title
    title = process.extractOne(input_title, list(df['title']))

    if title[1] >= 85:

        # gets index that matches title
        idx = indices[title[0]]

        # gets pairwise similarity scores of all titles with that title
        sim_scores = list(enumerate(cosine_sim[idx]))

        # sorts titles based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # gets scores of the 10 most similar titles
        sim_scores = sim_scores[1:11]

        # gets title indices
        book_indices = [i[0] for i in sim_scores]

        # returns book bibliographic info (w/ cluster), style metrics, and top 10 most similar titles
        input_title = df[df['title'] == title[0]][['author', 'title', 'year', 'cluster']]
        input_metrics = df[df['title'] == title[0]].iloc[:,4:-1]
        closest = df[['author', 'title']].iloc[book_indices]
        
        return input_title, input_metrics, closest
    
    else:
        print(f'{input_title} not found.')