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

def capitalize(translation, src):
    output = []
    src_words = src.split()
    for w in translation.split():
        if w.isalpha() and w.islower() and w.capitalize() in src_words:
            output.append(w.capitalize())
        else:
            output.append(w)
    return " ".join(output)

class Translator(object):
    def __init__(self, lexicon_f, lm):
        self.dic = {}
        for line in codecs.open(lexicon_f,encoding='utf-8'):
            src, trg = line.strip().split('\t')
            self.dic[src] = trg
        self.language_model = lm

    def translate(self, sent):
        words = sent.split()
        initial_translation = []
        start_end_idx = []
        
        i = 0
        is_prev_unk = False
        while i < len(words):
            phrase = None
            if i < len(words)-1:
                phrase = (words[i]+" "+words[i+1]).lower()
            word = words[i].lower()
            if phrase and phrase in self.dic: # first attempt: translate bigrams
                initial_translation.append(self.dic[phrase])
                start_end_idx.append((i,i+1))
                i += 1 # skip next word since already translated
                is_prev_unk = False
            elif word in self.dic: # second attempt: translate single words
                initial_translation.append(self.dic[word])
                start_end_idx.append((i,i))
                is_prev_unk = False
            else: # keep as-is
                if is_prev_unk: # merge consecutive unknown words as a single phrase
                    initial_translation[-1] += " "+words[i]
                    prev_start, prev_end = start_end_idx[-1]
                    new_start_end = (prev_start, prev_end+1)
                    start_end_idx[-1] = new_start_end
                else:
                    initial_translation.append(words[i])
                    start_end_idx.append((i,i))
                is_prev_unk = True
            i += 1

        candidate_idx_list = permute(range(len(initial_translation)), -1, start_end_idx)
        candidates = []
        for candidate_idx in candidate_idx_list:
            candidates.append(" ".join([initial_translation[i] for i in candidate_idx]))
        best_translation = sorted(candidates, key=self.language_model.score, reverse=True)[0]
        return best_translation

if __name__ == "__main__":
    test_f = sys.argv[1]
    lm_f = sys.argv[2]
    lm = kenlm.Model(lm_f)
    output_f = codecs.open(sys.argv[3],'w',encoding='utf-8')
    output_f.write('\t'.join(["Category","Product name","Translated"])+"\n")
    categories = ['Mobile & Gadget','Fashion Accessories']
    for cate in categories:
        print "Processing", cate
        lexicon_f = 'lexicon_%s.txt' % cate.replace(' ','_')
        translator = Translator(lexicon_f, lm)
        for line in codecs.open(test_f,encoding='utf-8'):
            cur_cate, sent = line.strip().split('\t')
            if cur_cate == cate:
                translation = translator.translate(sent)
                output_f.write('\t'.join([cur_cate, sent, capitalize(translation, sent)])+'\n')
    output_f.close()
