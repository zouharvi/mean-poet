from nltk import word_tokenize, pos_tag
import numpy as np

POS_ADJ = {"JJ", "JJR", "JJS"}
POS_NOUN = {"NN", "NNS", "NNP", "NNPS"}
POS_ADVB = {"RB", "RBR", "RBS"}
POS_VERB = {"VB", "VBG", "VBD", "VBN", "VBP", "VBZ", "MD"}
POS_PREP = {"IN", "EX", "RP", "TO", "CC"}
POS_PRON = {"PDT", "POS", "PRP", "PRP$", "WP", "WRB"}
POS_EXTRA = {"CD", "FW", "LS", "UH"}
POS_CONTENT = POS_ADJ | POS_NOUN | POS_ADVB | POS_VERB

def get_pos_distribution(poem, epsilon=1):
    """
    Returns vector of distribution (adjectives, nouns, adverbs, verbs, determiner, prepositions*, pronouns, extra).
    For stability smoothed by adding epsilon to each.
    """
    output = [epsilon]*8
    for _word, pos in pos_tag(word_tokenize(poem)):
        if pos in POS_ADJ:
            output[0] += 1
        if pos in POS_NOUN:
            output[1] += 1
        if pos in POS_ADVB:
            output[2] += 1
        if pos in POS_VERB:
            output[3] += 1
        if pos == "DT":
            output[4] += 1
        if pos in POS_PREP:
            output[5] += 1
        if pos in POS_PRON:
            output[6] += 1
        if pos in POS_EXTRA:
            output[7] += 1
    
    total = sum(output)
    return [x/total for x in output]

def kl_divergence(dist1, dist2):
    return sum([x*np.log2(x/y) for x,y in zip(dist1, dist2)])

def get_pos_sim(poem1, poem2):
    """
    Compute Jensen Shannon Divergence on POS distribution of poems.
    It's a simple symmetrification of the KL divergence.
    Bounded [0, 1] when log2 is used.
    """
    dist1 = get_pos_distribution(poem1)
    dist2 = get_pos_distribution(poem2)

    dist_mixed = [1/2*(x+y) for x,y in zip(dist1, dist2)]
    divergence = 1/2*(kl_divergence(dist1, dist_mixed)+kl_divergence(dist2, dist_mixed))

    return 1-divergence