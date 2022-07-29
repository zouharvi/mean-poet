from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize

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

def meaning_overlap(poem1, poem2):
    # TODO: restrict only to content words like nouns, adjectives & verbs?
    meaning1 = set()
    for word in word_tokenize(poem1):
        meaning1 |= get_synonyms(word) | get_hyponyms(word) | get_hypernyms(word)

    meaning2 = set()
    for word in word_tokenize(poem2):
        meaning2 |= get_synonyms(word) | get_hyponyms(word) | get_hypernyms(word)
    
    # arbitrary similarity of two sets
    return len(meaning1 & meaning2)/(len(meaning1) | len(meaning2))