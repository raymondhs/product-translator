#!/bin/bash

#### Set your hyper-parameters here ####
############## START ###################
KENLM_BIN=kenlm/build/bin
lcode="th" # ISO 639-1 code of target language.
max_corpus_size=1000000000 # the maximum size of the corpus. Feel free to adjust it according to your computing power.
############## END #####################

echo "step 0. Make `data` directory and move there."
mkdir data; cd data

echo "step 1. Download the stored wikipedia file to your disk."
wget "https://dumps.wikimedia.org/${lcode}wiki/20170401/${lcode}wiki-20170401-pages-articles-multistream.xml.bz2"

echo "step 2. Extract the bz2 file."
bzip2 -d "${lcode}wiki-20170401-pages-articles-multistream.xml.bz2"

cd ..
echo "step 3. Build Corpus."
python build_corpus.py --lcode=${lcode} --max_corpus_size=${max_corpus_size}

echo "step 4. Train language model."
$KENLM_BIN/lmplz -o 3 < data/th.txt > th.txt.arpa
