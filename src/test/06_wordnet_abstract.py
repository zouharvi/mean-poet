from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet

POS_ADJ = {"JJ", "JJR", "JJS"}
POS_NOUN = {"NN", "NNS", "NNP", "NNPS"}
POS_ADV = {"RB", "RBR", "RBS"}
POS_VERB = {"VB", "VBG", "VBD", "VBN", "VBP", "VBZ"}
POS_CONTENT = POS_ADJ | POS_NOUN | POS_ADV | POS_VERB

SYNSET_ABS = wordnet.synset("abstraction.n.06")
SYNSET_PHS = wordnet.synset("physical_entity.n.01")
SYNSET_THG = wordnet.synset("thing.n.08")
SYNSET_ENT = wordnet.synset("entity.n.1")


def classify_word_abs(synset):
    if type(synset) is list:
        if len(synset) == 0:
            return []
        result = [classify_word_abs(x) for x in synset]
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
        return classify_word_abs(synset.hypernyms())



def abstract_concrete_ratio(poem, latex=False):
    count_abs = 0
    count_con = 0
    for word, pos in pos_tag(word_tokenize(poem)):
        if pos in POS_CONTENT:
            # add even partials
            result_abs_con = classify_word_abs(wordnet.synsets(word))
            if len(result_abs_con) == 0:
                continue
            result_abs = sum(result_abs_con)
            result_con = len(result_abs_con) - result_abs
            count_abs += result_abs / (result_abs + result_con)
            count_con += result_con / (result_abs + result_con)

            if latex:
                local_abs = result_abs / (result_abs + result_con)
                print("\hlc[pink!" + str(int(local_abs*100)) + "]{" + word + "}", end=" ")
        else:
            if latex:
                print(word, end=" ")

    return count_abs / (count_abs + count_con)



print(abstract_concrete_ratio("I sit on a chair."))
print(abstract_concrete_ratio("I love you. I love you."))

print(abstract_concrete_ratio(
    "oh the skein of raggle-taggle village dogs: trickly tails, stubbly legs, tough teeth fletching at the fence ",
    latex=True
))
print()
print(abstract_concrete_ratio(
    "o the village dogs small spotted crowd: cheating tails stubby legs tough snouts on the fence",
    latex=True
))
