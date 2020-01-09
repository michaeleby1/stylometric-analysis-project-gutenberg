import os
import glob
import re
from gutenberg.cleanup import strip_headers
import wikipedia
PageError = wikipedia.exceptions.PageError
DisambiguationError = wikipedia.DisambiguationError


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


def mongo_upload(filelist):  
    ## these errors will correspond to missing metadata; if a file doesn't
    ## have all the metadata I want, it will not load into Mongo
    KeyErrorIndexError_count = 0
    UnicodeError_count = 0 
    Disambiguation_count = 0
        
    for file in filelist:
        dict_ = {'file': '', 'author': '', 'title': '', 'year': '', 'text': ''}

        try:
            author, title, year = author_title_year(file)
            dict_['file'] = file
            dict_['author'] = author
            dict_['title'] = title
            dict_['year'] = year
            dict_['text'] = clean_text(file)
            
        ## quality filtering; if a text doesn't have both author and title 
        ## python will throw KeyError, IndexError, and the text it will 
        ## not enter the database
        except (KeyError, IndexError) as e:
            KeyErrorIndexError_count += 1
            continue

        ## this removes duplicate encodings from the dict; all filenames throwing 
        ## this error end in "-8" or "-0", and there seems to be ASCII versions of them
        except UnicodeDecodeError as e2:
            UnicodeError_count += 1
            continue
        
        ## more quality filtering; if the book is not first wikipedia search result
        ## or doesn't have a wikipedia page it will not enter the database
        except (AttributeError, PageError, DisambiguationError) as e3:
            Disambiguation_count += 1
            continue

        collection.insert_one(dict_)

    print(f'Number of missing authors and/or titles: {KeyErrorIndexError_count}')
    print(f'Number of duplicate encodings: {UnicodeError_count}')
    print(f'Number missing from wikipedia: {Disambiguation_count}')
