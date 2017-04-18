# Product Title Translation
This document describes the steps, data and algorithms for automatic product title translation from English to Thai.

## Methodology
The task of interest can be regarded as a domain-specific machine translation. Two popular approaches for machine translation are based on phrase-based machine translation (e.g., [Moses](http://www.statmt.org/moses/)) and neural machine translation (e.g., the recently released [OpenNMT](http://opennmt.net/)). However, such approaches typically require a large amount of parallel corpora in order to work well.

I opted for a hybrid approach based on dictionary-based translation and statistical language modeling (LM). The work flow consists of two steps: 1) automatic creation of an English-Thai lexicon and 2) dictionary-based translation with LM-based reordering. I will explain these in the following sections.

## Bilingual Lexicon
Two domains are given in this project: *Mobile & Gadget* and *Fashion Accessories*. To my finding, an English-Thai lexicon specific for each domain is not available. On the other hand, a dictionary from the general domain would have poor coverage as many phrases in the product titles will not be found.

I propose to automatically build a lexicon with respect to each domain leveraging on a popular translation service, [Google Translate](https://translate.google.com/). In the first step, I created a list of English words and phrases to be translated. In my experiments, only bigram phrases (a phrase containing two words) are considered. Not every word and phrase is useful, so this list is filtered according to their number of occurrences in the data. This is done by using NLTK's `BigramCollocationFinder` module (http://www.nltk.org/howto/collocations.html).

After creating this list, we translate them using Google Translate. I used a Python library for this, [googletrans](https://github.com/ssut/py-googletrans). The library basically performs translation by scraping the Google Translate's web interface. Alternatively, we can use [Google Cloud Translation API](https://cloud.google.com/translate/docs/) (paid service). This step is done individually for both domains, so we will end up with two different bilingual lexicons.

One thought is whether we can use Google Translate directly for translating the product titles. This won't work well in practice because Google Translate is not trained on such text domains.

## Translation

After having the bilingual lexicon, we are ready to translate the English product titles into Thai. My translation algorithm is as follows. It proceeds by going through the input words from left to right. First it attempts to translate bigram phrases. If such bigrams are not found in the bilingual lexicon, it considers the first word in the bigram instead. If this word is also unknown, it is copied verbatim to the translation output.

As pointed out in the task description, English and Thai have different grammars. Therefore, it is important to consider their differences in word ordering. Again I decided to go for a corpus-driven approach based on language modeling. First, we generate a list of permutation of the word ordering in the initial translation output. As there are exponentially many ways to reorder the words, we need to make the computation tractable. This is done by imposing a reordering limit, i.e., abs( last word position of previously translated phrase + 1 - first word position of newly translated phrase ) <= D, where we set D = 2.

I rank the above list according to a language model (LM) score, and select the output translation with the highest score. The language model is an unpruned 3-gram LM with modified Kneser-Ney smoothing as implemented in [KenLM](https://kheafield.com/code/kenlm/). The LM is trained on [Thai Wikipedia](https://dumps.wikimedia.org/thwiki/20170401/thwiki-20170401-pages-articles-multistream.xml.bz2). 

## Thoughts on this approach

There is definitely room for improvement for this approach. The bilingual lexicon can be improved by adding a manually-curated bilingual translations specific to the domain. The language model can be trained on a collection of Thai product titles (if it is available). In addition to language model, we can rely on the Web for scoring the translation quality. For instance, we can enter the translation as a query to a search engine and score it based on the result counts returned by the engine.
