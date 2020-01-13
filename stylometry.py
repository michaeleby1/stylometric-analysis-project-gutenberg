import string
import numpy as np
import scipy as sc
import collections
from collections import Counter
import pymongo
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

## standardized type-token ratio (average of ttrs over 1000 word chunks)
def sttr(tokens, window_size=1000):
    ttrs = []
    for i in range(int(len(tokens) / window_size)):  # ignore last partial chunk
        ttrs.append(ttr(tokens[i * window_size:(i * window_size) + window_size]))
    return np.mean(ttrs)


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
def yules_k(tokens):
    token_freq = collections.Counter()
    token_freq.update(tokens)
    vi = collections.Counter()
    vi.update(token_freq.values())
    N = len(tokens)
    M = sum([(value * value) * vi[value] for key, value in token_freq.items()])
    K = 10000 * (M - N) / np.power(N, 2)
    return K

## percentage of document comprised of function words
def function_words(doc):
    function_words = """a between in nor some upon
    about both including nothing somebody us
    above but inside of someone used
    after by into off something via
    all can is on such we
    although cos it once than what
    am do its one that whatever
    among down latter onto the when
    an each less opposite their where
    and either like or them whether
    another enough little our these which
    any every lots outside they while
    anybody everybody many over this who
    anyone everyone me own those whoever
    anything everything more past though whom
    are few most per through whose
    around following much plenty till will
    as for must plus to with
    at from my regarding toward within
    be have near same towards without
    because he need several under worth
    before her neither she unless would
    behind him no should unlike yes
    below i nobody since until you
    beside if none so up your
    """
    function_words = function_words.split()
    count = 0
    for token in doc:
        if token.orth_.lower() in function_words:
            count += 1
    return count / len(doc)


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


## average number of punctuation characters per sentence
def punctuation_sentence(sentences):
    count = 0
    for sentence in sentences:
        for char in sentence:
            if char in string.punctuation:
                count += 1
    return float(count) / float(len(sentences))


## Shannon's Entropy for readability score
def shannon_entropy(tokens):
    token_freq = collections.Counter()
    token_freq.update(tokens)
    arr = np.array(list(token_freq.values()))
    distribution = 1. * arr
    distribution /= max(1, len(tokens))
    H = sc.stats.entropy(distribution, base=2)
    return H


## Simpson's Diversity Index (Simpson's D)
def simpsons_d(tokens):
    token_freq = collections.Counter()
    token_freq.update(tokens)
    N = len(tokens)
    n = sum([1.0 * i * (i - 1) for i in token_freq.values()])
    D = 1 - (n / (N * (N - 1)))
    return D


## average number of noun phrases per 1000 words
def average_nps(doc, window_size=1000):    
    counts = []
    for i in range(int(len(doc) / window_size)):  # ignore last partial chunk
        count = 0
        for chunk in (doc[i * window_size:(i * window_size) + window_size]).noun_chunks:
            count += 1
        counts.append(count)
    return np.mean(counts)


## noun-to-verb ratio; over .50 indicates noun bias, under .50 indicates verb bias
def noun_to_verb(doc):
    n_nouns = 0
    n_verbs = 0 
    for token in doc:
        if token.pos_ == 'NOUN' or token.pos_ == 'PROPN':
            n_nouns += 1
        elif token.pos_ == 'VERB':
            n_verbs += 1
    return n_nouns / (n_nouns + n_verbs)


## noun-to-adjective ratio; over .50 indicates noun bias, under .50 indicates adjective bias
def noun_to_adj(doc): 
    n_nouns = 0
    n_adjs = 0
    for token in doc:
        if token.pos_ == 'NOUN' or token.pos_ == 'PROPN':
            n_nouns += 1
        elif token.pos_ == 'ADJ':
            n_adjs += 1
    return n_nouns / (n_nouns + n_adjs)


## verb to adverb ratio; over .50 indicates verb bias, under .50 indicates adverb bias
def verb_to_adv(doc): 
    n_verbs = 0
    n_advs = 0
    for token in doc:
        if token.pos_ == 'VERB':
            n_verbs += 1
        elif token.pos_ == 'ADV':
            n_advs += 1
    return n_verbs / (n_verbs + n_advs)
    

## average dependency distance between head and children (connected by a single arc)
def average_dependency_distance(doc):   
    dep_distances = []
    for token in doc:
        children_distances = []
        for child in token.children:
            children_distances.append(abs(child.i - token.i))
        dep_distances.append(np.mean(children_distances))
    return np.mean([value for value in dep_distances if ~np.isnan(value)])