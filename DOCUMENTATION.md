# Product Title Translation
This document describes the steps, data and algorithms for automatic product title translation from English to Thai.

## Methodology
The task of interest can be regarded as a domain-specific machine translation. Two popular approaches for machine translation are based on phrase-based machine translation (e.g., [Moses](http://www.statmt.org/moses/)) and neural machine translation (e.g., the recently released [OpenNMT](http://opennmt.net/)). However, such approaches typically require a large amount of parallel corpora in order to work well.

I opted for a hybrid approach based on dictionary-based translation and statistical language modeling (LM). The work flow consists of two steps: 1) automatic creation of an English-Thai lexicon and 2) dictionary-based translation with LM-based reordering. I will explain these in the following sections.

## Bilingual Lexicon
Two domains are given in this project: *Mobile & Gadget* and *Fashion Accessories*. To my finding, an English-Thai lexicon specific for each domain is not available. On the other hand, a dictionary from the general domain would have poor coverage as many phrases in the product titles will not be found.

I propose to automatically build a lexicon with respect to each domain leveraging on a popular translation service, [Google Translate](https://translate.google.com/). In the first step, I created a list of English words and phrases to be translated. In my experiments, only bigram phrases (a phrase containing two words) are considered. Not every word and phrase is useful, so this list is filtered according to their number of occurrences in the data. This is done by using NLTK's `BigramCollocationFinder` [module](http://www.nltk.org/howto/collocations.html).

After creating this list, we translate them using Google Translate. I used a Python library for this, [googletrans](https://github.com/ssut/py-googletrans). The library basically performs translation by scraping the Google Translate's web interface. Alternatively, we can use [Google Cloud Translation API](https://cloud.google.com/translate/docs/) (paid service).
 
