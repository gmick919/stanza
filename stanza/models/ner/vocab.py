from collections import Counter, OrderedDict

from stanza.models.common.vocab import BaseVocab, BaseMultiVocab, CharVocab
from stanza.models.common.vocab import VOCAB_PREFIX
from stanza.models.common.pretrain import PretrainedWordVocab

class TagVocab(BaseVocab):
    """ A vocab for the output tag sequence. """
    def build_vocab(self):
        counter = Counter([w[self.idx][i]
                           for sent in self.data
                           for w in sent
                           for i in range(len(w[1]))])
        self._id2unit = VOCAB_PREFIX + list(sorted(list(counter.keys()), key=lambda k: counter[k], reverse=True))
        self._unit2id = {w:i for i, w in enumerate(self._id2unit)}

class MultiVocab(BaseMultiVocab):
    def state_dict(self):
        """ Also save a vocab name to class name mapping in state dict. """
        state = OrderedDict()
        key2class = OrderedDict()
        for k, v in self._vocabs.items():
            state[k] = v.state_dict()
            key2class[k] = type(v).__name__
        state['_key2class'] = key2class
        return state

    @classmethod
    def load_state_dict(cls, state_dict):
        class_dict = {'CharVocab': CharVocab,
                'PretrainedWordVocab': PretrainedWordVocab,
                'TagVocab': TagVocab}
        new = cls()
        assert '_key2class' in state_dict, "Cannot find class name mapping in state dict!"
        key2class = state_dict.pop('_key2class')
        for k,v in state_dict.items():
            classname = key2class[k]
            new[k] = class_dict[classname].load_state_dict(v)
        return new

class CharVocab(BaseVocab):
    def build_vocab(self):
        if type(self.data[0][0]) is list: # general data from DataLoader
            count_list = []
            for sent in self.data:
                for w in sent:
                    for tag in w[1]:
                        count_list.append((w[0], tag))
            counter = Counter(count_list)
            for k in list(counter.keys()):
                if counter[k] < self.cutoff:
                    del counter[k]
        else: # special data from Char LM
            count_list = []
            for sent in self.data:
                for w in sent:
                    for tag in w[1]:
                        count_list.append((w[0], tag))
            counter = Counter(count_list)
        self._id2unit = VOCAB_PREFIX + list(sorted(list(counter.keys()), key=lambda k: (counter[k], k), reverse=True))
        self._unit2id = {w:i for i, w in enumerate(self._id2unit)}