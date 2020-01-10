import pymongo
import numpy as np
from nltk.corpus import cmudict
cmudict = cmudict.dict()
import spacy
import en_core_web_lg
nlp = en_core_web_lg.load()
import time


client = pymongo.MongoClient('mongodb://localhost/')
db = client['example_database']
collection = db['example_collection']

nlp = en_core_web_md.load()
doc = nlp(text)
tokens = [token.orth_.lower() for token in doc if not token.is_punct and token if not token.is_stop]
sentences = [sent.string.strip() for sent in doc.sents]


def ttr(tokens):
    return len(set(tokens))/len(tokens)


def avg_sentence_length_word(sentences):
    return np.mean([len(sentence.split()) for sentence in sentences])


def avg_sentence_length_chars(sentences):
    return np.mean([len(sentence) for sentence in sentences])


def n_syllables(token):
    try:
        n = [len(list(y for y in x if y[-1].isdigit())) for x in cmudict[token]][0]
    except:
        n = n_syllables_except(token) 
    return n


def n_syllables_except(token):
    vowels = 'aeiouy'
    count = 0
    if token[0] in vowels:
        count += 1
    for index in range(1, len(token)):
        if token[index] in vowels and token[index-1] not in vowels:
            count += 1
            if token[-1] == 'e':
                count -= 1
    if count == 0:
        count += 1
    return count


def avg_syllables_per_word(tokens):
    syllables_list = [n_syllables(token) for token in tokens]
    avg_syllables = sum(syllables_list) / max(1, len(tokens))
    return avg_syllables
