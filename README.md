# Stylometric Analysis of Project Gutenberg

## Project Gutenberg

Project Gutenberg is a volunteer effort to digitize and archive cultural works, to "encourage the creation and distribution of eBooks.” It was founded in 1971 by American writer Michael S. Hart and is the oldest digital library. Most of the items in its collection are the full texts of public domain books. A majority of the titles were originally published before 1950, as these titles do not fall under copyright protections.

## Summary

My goal for this project was to build a recommendation engine for books that is based on author style as opposed to bibliographic metadata or reader reviews, as many other book recommenders are. I also sought to cluster all English books in Project Gutenberg into stylistic types. I did this by engineering numerical style metrics for the full text of every English book in Project Gutenberg, approximately 30,000 titles. 

Based on these style metrics, I produced two things:

1. A recommendation engine using cosine similarity between titles
2. An identification of 7 stylistic types in Project Gutenberg using k-means clustering

## ETL Pipeline

## Style Metrics

I engineered 16 style metrics indicative of vocabulary richness, lexical complexity, sentence and word length, part-of-speech ratios, and readibility scores:

**Standardized Type-Token Ratio:** Type-token ratio (TTR) is a measure of vocabulary richness. It is calculated by dividing the number of unique tokens used in a text by the total number of tokens. _Standardized_ TTR calculates the running average of TTRs for every 1,000 word window of a text.

**Hapax Legomenon:** This measure is somewhat correlated with the TTR. It measures the percentage of words used only once. I calculated the running average for every 1,000 word window of each text. 

**Yule’s K Characteristic:** Yule's K measures the likeihood that two words randomly chosen from the same document will be the same word. 

**Function Words:** This metric is the percentage of a document comprised of function words, including articles, prepositions, and conjunctions. 

**Average Sentence Length in Words:** Including stop words, the average sentence length of a document in word count.

**Average Sentence Length in Characters:** Including stop words, the average sentence length of a document in character count.

**Average Number of Syllables Per Word:** Determined via a function that, where available, references the CMU Pronouncing Dictionary for the number of syllables in a word. When not available, the function calculates the number of syllables according to the so-called "written method." I then took the average number of syllables for the whole document. 

**Punctuation Per Sentence:** 

**Shannon’s Entropy:** 

**Simpson’s D:** 
 
**Number of Noun Phrases:**

**Average Sentence Length in Words:**

**Noun to Verb Ratio:**

**Noun to Adjective Ratio:** 

**Verb to Adverb Ratio:** 

**Average Dependency Distance:**

## Exploratory Data Analysis 

Several of the style metrics varied widely over time. For example, show marked decrease  

## Clusters

## Metric Space

t-SNE

## Recommendation Engine