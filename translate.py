import codecs, sys
import kenlm

REORDER_LIMIT = 2

def permute(indices, prev, start_end_idx):
    if len(indices) == 1:
        if abs(start_end_idx[indices[0]][0]-prev-1) <= REORDER_LIMIT:
            return [indices]
        return []

    perm_list = []
    for i in indices:
        if abs(start_end_idx[i][0]-prev-1) <= REORDER_LIMIT:
            remaining = [j for j in indices if i != j]
            for other_perm_list in permute(remaining, start_end_idx[i][1], start_end_idx):
                perm_list.append([i]+other_perm_list)
    return perm_list

class Translator(object):
    def __init__(self, lexicon_f, lm_f):
        self.dic = {}
        for line in codecs.open(lexicon_f,encoding='utf-8'):
            src, trg = line.strip().split('\t')
            self.dic[src] = trg
        self.language_model = kenlm.Model(lm_f)

    def translate(self, sent):
        words = sent.split()
        words_translated = {}
        initial_translation = []
        start_end_idx = []
        
        i = 0
        while i < len(words)-1:
            phrase = (words[i]+" "+words[i+1]).lower()
            word = words[i].lower()
            if phrase in self.dic: # first attempt: translate bigrams
                initial_translation.append(self.dic[phrase])
                words_translated[i] = True
                words_translated[i+1] = True
                start_end_idx.append((i,i+1))
                i += 1 # skip next word since already translated
            elif word in self.dic: # second attempt: translate single words
                initial_translation.append(self.dic[word])
                words_translated[i] = True
                start_end_idx.append((i,i))
            else: # keep as-is
                initial_translation.append(words[i])
                start_end_idx.append((i,i))
            i += 1

        candidate_idx_list = permute(range(len(initial_translation)), -1, start_end_idx)
        candidates = []
        for candidate_idx in candidate_idx_list:
            candidates.append([initial_translation[i] for i in candidate_idx])
        best_translation = sorted(candidates, key=self.language_model.score, reverse=True)[0]
        return " ".join(best_translation)

if __name__ == "__main__":
    test_f = sys.argv[1]
    categories = ['Mobile & Gadget','Fashion Accessories']
    for cate in categories:
        print "Processing", cate
        lexicon_f = 'lexicon_%s.txt' % cate.replace(' ','_')
        translator = Translator(lexicon_f)
        for line in codecs.open(test_f,encoding='utf-8'):
            cur_cate, sent = line.strip().split('\t')
            
            if cur_cate == "Category": # print header
                print line.strip()
            
            if cur_cate == cate:
                translation = translator.translate(sent)
                print "\t".join(cur_cate, sent, translation).encode('utf-8')
