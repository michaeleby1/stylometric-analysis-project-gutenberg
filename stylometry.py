import pymongo
import numpy as np
import math
import collections
from collections import Counter
from nltk.corpus import cmudict
cmudict = cmudict.dict()
import spacy
import en_core_web_lg
nlp = en_core_web_lg.load()


# client = pymongo.MongoClient('mongodb://localhost/')
# db = client['gutenberg_db']
# collection = db['gutenberg_collection']


# doc = nlp(text)
# tokens = [token.orth_.lower() for token in doc if not token.is_punct and token if not token.is_stop]
# sentences = [sent.string.strip() for sent in doc.sents]

## type-to-token ratio
def ttr(tokens):
    return len(set(tokens))/len(tokens)


## percentage of words only used once
def hapax_legomenon(tokens):
    t1 = 0
    n = len(tokens)
    token_freq = dict(Counter(tokens))
    for token in token_freq:
        if token_freq[token] == 1:
            t1 += 1
    return t1 / n        


## measures the likelihood that two randomly chosen words will be the same
def yules_K(tokens):
    token_freq = collections.Counter()
    token_freq.update(tokens)
    vi = collections.Counter()
    vi.update(token_freq.values())
    print(token_freq)
    M = sum([(value * value) * vi[value] for key, value in token_freq.items()])
    K = 10000 * (M - N) / math.pow(N, 2)
    return K


## average length of sentence by word count
def avg_sentence_length_word(sentences):
    return np.mean([len(sentence.split()) for sentence in sentences])


## average length of sentence by character count
def avg_sentence_length_chars(sentences):
    return np.mean([len(sentence) for sentence in sentences])


## number of syllables per word (via CMU Pronouncing Dictionary)
def n_syllables(token):
    try:
        n = [len(list(y for y in x if y[-1].isdigit())) for x in cmudict[token]][0]
    except:
        n = n_syllables_except(token) 
    return n


## number of syllables per word (via the "written method," vowel counts)
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


## average number of syllables per word (via previous two functions)
def avg_syllables_per_word(tokens):
    syllables_list = [n_syllables(token) for token in tokens]
    avg_syllables = sum(syllables_list) / max(1, len(tokens))
    return avg_syllables
