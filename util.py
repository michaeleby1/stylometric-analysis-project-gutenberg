import re
import glob
import numpy as np
from gutenberg.cleanup import strip_headers

def author_title(file):
    with open(file, 'r') as f:
        text = f.read()
    author = re.findall(r'(?:Author: )(.*)(?:\n)', text)[0]
    title = re.findall(r'(?:Title: )(.*)(?:\n)', text)[0]
    return author, title

def clean_text(file):
    with open(file, 'r') as f:
        text = strip_headers(f.read())
    
    ## removes newline characters and underscores
    r = re.compile(r'[\n _]')
    text = r.sub(' ', text)
    
    ## deals with many spaces which will make analysis at the character level easier
    s = re.compile('\s+')
    text = s.sub(' ', text)               
    return text

path = 'project_gutenberg'
filelist = sorted(glob.glob(path + "/*.txt"), reverse=True)

def mongo_upload(filelist):
    
    dict_ = {'file': [], 'author': [], 'title': [], 'text': []}
    
    KeyErrorIndexError_count = 0
    UnicodeError_count = 0 
    
    for file in filelist:
        
        try:
            author, title = author_title(file)
            dict_['file'] = file
            dict_['author'] = author
            dict_['title'] = title
            dict_['text'] = clean_text(file)
            
        ## quality filtering; if a text doesn't have both author and title 
        ## python will throw KeyError and/or IndexError, and the text will 
        ## not append to the dict
        except (KeyError, IndexError) as e:
            KeyErrorIndexError_count += 1
            continue

        ## this removes duplicate encodings from the dict; all filenames throwing 
        ## this error end in "-8" or "-0", and there seems to be ASCII versions of them
        except UnicodeDecodeError as e2:
            UnicodeError_count += 1
            continue
            
#     collection.insert_one(dict_)    

    print(f'KeyError/IndexError count: {KeyErrorIndexError_count}')
    print(f'UnicodeDecodeError count: {UnicodeError_count}')
    
    return dict_