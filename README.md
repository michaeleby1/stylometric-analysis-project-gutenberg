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


• Standardized Type-Token Ratio

• Hapax Legomenon

• Yule’s K Characteristic

• Function Words Percentage

• Average Sentence Length in Words

• Average Sentence Length in Characters 

• Average Number of Syllables Per Word

• Punctuation Per Sentence
