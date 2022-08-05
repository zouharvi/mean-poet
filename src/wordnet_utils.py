from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag

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

POS_ADJ = {"JJ", "JJR", "JJS"}
POS_NOUN = {"NN", "NNS", "NNP", "NNPS"}
POS_ADV = {"RB", "RBR", "RBS"}
POS_VERB = {"VB", "VBG", "VBD", "VBN", "VBP", "VBZ"}
POS_CONTENT = POS_ADJ | POS_NOUN | POS_ADV | POS_VERB

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


def abstract_concrete_ratio(poem):
    count_abs = 0
    count_con = 0
    for word in word_tokenize(poem):
        ontology = wordnet.root_hypernyms(word)
        print(ontology)