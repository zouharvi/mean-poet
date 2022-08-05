from nltk.corpus import wordnet

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

print(get_synonyms("path"))
print(get_synonyms("route"))

print(get_hypernyms("route"))