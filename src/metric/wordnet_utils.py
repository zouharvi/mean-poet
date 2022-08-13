from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag
from .pos_utils import POS_CONTENT

def get_synonyms(word):
    synsets = wordnet.synsets(word)
    # flatten
    return {word for synset in synsets for word in synset.lemma_names()}

def get_hypernyms(word):
    # flatten
    synsets = [synset_hyp for synset in wordnet.synsets(word) for synset_hyp in synset.hypernyms()]
    # flatten
    return {word for synset in synsets for word in synset.lemma_names()}

def get_hyponyms(word):
    # flatten
    synsets = [synset_hyp for synset in wordnet.synsets(word) for synset_hyp in synset.hyponyms()]
    # flatten
    return {word for synset in synsets for word in synset.lemma_names()}

def meaning_overlap(poem1, poem2, hypo_hype=False):
    """
    Uses only content words to determine meaning intersection.
    """
    meaning1 = set()
    for word, pos in pos_tag(word_tokenize(poem1)):
        if pos in POS_CONTENT:
            meaning1 |= get_synonyms(word)
            if hypo_hype:
                meaning1 |= get_hyponyms(word) | get_hypernyms(word)

    meaning2 = set()
    for word, pos in pos_tag(word_tokenize(poem2)):
        if pos in POS_CONTENT:
            meaning2 |= get_synonyms(word)
            if hypo_hype:
                meaning2 |= get_hyponyms(word) | get_hypernyms(word)
        
    # arbitrary similarity of two sets
    return len(meaning1 & meaning2)/(len(meaning1) + len(meaning2))


def meaning_overlap_all(poem1, poem2, hypo_hype=False):
    """
    Uses all word classes.
    """
    meaning1 = set()
    for word in word_tokenize(poem1):
        meaning1 |= get_synonyms(word)
        if hypo_hype:
            meaning1 |= get_hyponyms(word) | get_hypernyms(word)

    meaning2 = set()
    for word in word_tokenize(poem2):
        meaning2 |= get_synonyms(word)
        if hypo_hype:
            meaning2 |= get_hyponyms(word) | get_hypernyms(word)
    
    # arbitrary similarity of two sets
    return len(meaning1 & meaning2)/(len(meaning1) + len(meaning2))

# desc: corr
# ==========
# content-only, syn: 0.31
# content-only, syn+hypo+hype: 0.30
# all, syn: 0.30
# all, syn+hypo+hype: 0.29


SYNSET_ABS = wordnet.synset("abstraction.n.06")
SYNSET_PHS = wordnet.synset("physical_entity.n.01")
SYNSET_THG = wordnet.synset("thing.n.08")
SYNSET_ENT = wordnet.synset("entity.n.1")

def abstractness_synset(synset):
    if type(synset) is list:
        if len(synset) == 0:
            return []
        result = [abstractness_synset(x) for x in synset]
        result = [x for y in result for x in y if x is not None]
        if len(result) == 0:
            return []
        else:
            return result
    if synset == SYNSET_ABS:
        return [True]
    elif synset == SYNSET_PHS:
        return [False]
    elif synset == SYNSET_THG:
        return [False]
    elif synset == SYNSET_ENT:
        return []
    else:
        # go up
        return abstractness_synset(synset.hypernyms())

def abstratness_poem(poem):
    count_abs = 0
    count_con = 0
    for word, pos in pos_tag(word_tokenize(poem)):
        if pos in POS_CONTENT:
            # add even partials
            result_abs_con = abstractness_synset(wordnet.synsets(word))
            if len(result_abs_con) == 0:
                continue
            result_abs = sum(result_abs_con)
            result_con = len(result_abs_con) - result_abs
            count_abs += result_abs / (result_abs + result_con)
            count_con += result_con / (result_abs + result_con)

    if count_abs+count_con == 0:
        return None
    return count_abs/(count_abs+count_con)