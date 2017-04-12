import codecs, nltk, sys, time
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.corpus import stopwords
from googletrans import Translator

entity_list = []
entity_f = 'entities.txt'
for line in codecs.open(entity_f, encoding='utf-8'):
    entity_list.append(line.strip())

def is_ignored(w):
    return len(w) < 3 \
        or any(ch.isdigit() for ch in w) \
        or w.lower() in entity_list

class PhraseExtractor(object):
    def __init__(self):
        # input text
        self.words = []
        
        # collocation finder and scorer
        self.finder = None
        self.scorer = None
        self.min_score = 0.0

    def add_sentence(self, sent):
        self.words += sent.strip().split()

    def get_phrases(self, min_freq=2, min_score=None):
        if not self.finder:
            # create a bigram collocation finder
            self.finder = BigramCollocationFinder.from_words(self.words)
            self.scorer = BigramAssocMeasures.raw_freq
            self.min_score = 1.0 / len(tuple(nltk.bigrams(self.words)))
        self.finder.apply_freq_filter(min_freq)
        self.finder.apply_word_filter(is_ignored)
        if min_score == None:
            min_score = self.min_score
        phrases = sorted(self.finder.above_score(self.scorer, min_score))
        phrases = [" ".join(phr) for phr in phrases]
        return phrases

    def get_keywords(self, min_freq=1):
        word_fd = self.finder.word_fd
        return filter(lambda w: word_fd[w] >= min_freq and not is_ignored(w), word_fd.keys())

if __name__ == "__main__":
    sample_f = sys.argv[1]
    test_f = sys.argv[2]
    categories = ['Mobile & Gadget','Fashion Accessories']
    for cate in categories:
        print "Processing", cate
        extractor = PhraseExtractor()
        for f in [sample_f, test_f]:
            for line in codecs.open(f,encoding='utf-8'):
                cur_cate, sent = line.split('\t')
                if cur_cate == cate:
                    extractor.add_sentence(sent)
        phrases = extractor.get_phrases()
        keywords = extractor.get_keywords()
        print ">> Found %d phrases and %d keywords" % (len(phrases), len(keywords))

        translator = Translator()
        batch_size = 20
        output_f = "lexicon_%s.txt" % cate.replace(" ","_")
        with codecs.open(output_f,'w',encoding='utf-8') as f:
            input_phrases = [phr.lower() for phr in phrases+keywords]
            for i in range(0,len(input_phrases),batch_size):
                print ">> Translating phrase %d-%d" % (i+1, i+batch_size)
                while True:
                    try:
                        translations = translator.translate(input_phrases[i:i+batch_size], src='en', dest='th')
                        break
                    except ValueError:
                        print >> sys.stderr, "Retrying translation"
                        time.sleep(2)

                for translation in translations:
                    if translation.origin.lower() != translation.text.lower():
                        f.write(translation.origin+'\t'+translation.text+'\n')
