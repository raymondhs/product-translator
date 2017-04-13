# product-translator

This is a project on product title translation from English to Thai. See the [documentation](DOCUMENTATION.md) for the description of steps, data and algorithms used.

## Requirements
Install the following Python libraries:

* nltk (http://www.nltk.org/install.html)
* googletrans (https://github.com/ssut/py-googletrans)
* kenlm (https://github.com/kpu/kenlm) (install both C++ and Python wrapper)

Additionally, the following are required for pre-processing Wikipedia corpus:

* regex >= 2016.6.24
* lxml >= 3.3.3
* pythai >= 0.1.3 

## Data
Take the first two columns (`Category` and `Product name`) of the provided sample and test data and convert them into tab-separated files. Put them in a directory named `data`.

## Language Model
Train a 3-gram language model based on Thai Wikipedia:
```bash
cd lm
bash prepro.sh
```

## Bilingual lexicon
```bash
python build_lexicon.py data/sample.txt data/test.txt
```

## Translate
```bash
python translate.py data/test.txt lm/th.txt.arpa test.output
```
