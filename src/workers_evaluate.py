import langdetect
import poesy
import pandas as pd
from sacrebleu.metrics import BLEU
import bert_score
from constants import *
from wordnet_utils import meaning_overlap
from evaluate import load

bleu_metric = BLEU(lowercase=True, effective_order=True)
comet_metric = load('comet')
bertscore_metric = load("bertscore")


def meter_regularity(meter):
    """
    Output is bounded [0, 1]
    """
    score = 0
    max_score = 0
    # look at patterns, make sure to not penalize across stanza boundaries
    # TODO: replace with smarter Poesy
    last_meter = " "
    for i in range(0, len(meter)):
        if meter[i] == " ":
            last_meter = " "
            continue
        if last_meter != " ":
            max_score += 2
            if last_meter == meter[i]:
                score += 2
            elif abs(last_meter - meter[i]) < 1:
                score += 1
        last_meter = meter[i]
    return score / max(max_score, 1)


def meter_regularity_sim(reg_1, reg_2):
    """
    Output is bounded [0, 1]
    """
    # TODO: not the best function
    return 1 - abs(reg_1 - reg_2)


def line_count_sim(count_1, count_2):
    """
    Output is bounded [0, 1]
    """
    # TODO: not the best function
    return min(count_1, count_2) / max(count_1, count_2)


def rhyme_intensity(rhyme):
    if all([x == "?" for x in rhyme]):
        return 0

    # TODO: currently penalizing diverse rhymes
    return 1 / len(set(rhyme))


def rhyme_intensity_sim(acc_xxx, acc_hyp):
    """
    Output is bounded [0, 1]
    """
    acc_xxx = max(0, acc_xxx)
    acc_hyp = max(0, acc_hyp)
    # TODO: not the best function
    return min(1, 1 - (acc_xxx - acc_hyp))


def get_meter(parsed):
    meter = []
    prev_stanza = None

    fallback_syllabes = any(
        [line.bestParses()[0] is None for line in parsed.prosodic.values()])

    linelenghts_iterator = parsed.linelengths if fallback_syllabes else parsed.linelengths_bybeat

    for (_line_i, stanza_i), val in linelenghts_iterator.items():
        if prev_stanza is not None and prev_stanza != stanza_i:
            # insert stanza separator to meter
            meter.append(" ")
        meter.append(val)
        prev_stanza = stanza_i

    # print("Fallback", fallback_syllabes, meter)
    return meter


def get_rhyme(parsed):
    rhyme = []
    prev_stanza = None
    for (_line_i, stanza_i), val in parsed.rhymes.items():
        if prev_stanza is not None and prev_stanza != stanza_i:
            # insert stanza separator to rhyme
            rhyme.append(" ")
        rhyme.append(val)
        prev_stanza = stanza_i
    return "".join(rhyme).replace("-", "?").upper()

def evaluate_ref_hyp(poem_ref, poem_hyp, lang_ref, lang_hyp, eval_hyp=None):
    """
    Complex evaluation of all aspects. Is expected to be run once against the src and once against ref.
    """
    # reuse previous computation
    if eval_hyp is not None:
        # TODO add rest
        rhyme_hyp = eval_hyp["rhyme_hyp"]
        meter_hyp = eval_hyp["meter_hyp"]
    else:
        parsed_hyp = poesy.Poem(poem_hyp)
        parsed_hyp.parse()

        # TODO: there are more features in parsed_hyp
        # print(parsed_hyp.meterd["ambiguity"], scheme_hyp["scheme"], scheme_hyp["scheme_type"])
        meter_hyp = get_meter(parsed_hyp)
        meter_reg_hyp = meter_regularity(meter_hyp)
        rhyme_hyp = get_rhyme(parsed_hyp)
        rhyme_acc_hyp = parsed_hyp.rhymed["rhyme_scheme_accuracy"]

    parsed_ref = poesy.Poem(poem_ref)
    parsed_ref.parse()

    meter_ref = get_meter(parsed_ref)

    # TODO: there are more features in parsed_ref
    # print(parsed_ref.meterd["ambiguity"], scheme_ref["scheme"], scheme_ref["scheme_type"])
    meter_reg_ref = meter_regularity(meter_ref)
    rhyme_ref = get_rhyme(parsed_ref)
    try:
        rhyme_acc_ref = parsed_ref.rhymed["rhyme_scheme_accuracy"]
    except:
        # sometimes the stresses are unavailable
        # go with 0 in that case
        rhyme_acc_ref = 0

    # parsed_hyp.rhymed["rhyme_scheme_accuracy"] could also be used for fixed rhymes
    # parsed_hyp.rhyme_ids intensity could also be used for fixed rhymes

    meter_sim = meter_regularity_sim(meter_reg_ref, meter_reg_hyp)
    line_sim = line_count_sim(
        poem_ref.count("\n") + 1,
        poem_hyp.count("\n") + 1
    )
    rhyme_sim = rhyme_intensity_sim(rhyme_acc_ref, rhyme_acc_hyp)

    # this assumes that poem_ref is reference
    # will yield random results on source (probably)
    bleu_ref_hyp = bleu_metric.sentence_score(
        " ".join(poem_hyp),
        [" ".join(poem_ref)],
    )

    # take f1 score
    bertscore_ref_hyp = bertscore_metric.compute(
        predictions=[" ".join(poem_hyp)], references=[[" ".join(poem_ref)]],
        lang=lang_hyp,
    )["f1"][0]
    
    return {
        "meter_sim": meter_sim,
        "line_sim": line_sim,
        "rhyme_sim": rhyme_sim,

        "meter_ref": meter_ref,
        "meter_hyp": meter_hyp,
        "meter_reg_ref": meter_reg_ref,
        "meter_reg_hyp": meter_reg_hyp,

        "rhyme_ref": rhyme_ref,
        "rhyme_hyp": rhyme_hyp,
        "rhyme_acc_ref": rhyme_acc_ref,
        "rhyme_acc_hyp": rhyme_acc_hyp,
        "rhyme_form_ref": parsed_ref.rhymed["rhyme_scheme_form"].upper(),
        "rhyme_form_hyp": parsed_hyp.rhymed["rhyme_scheme_form"].upper(),

        "bleu": bleu_ref_hyp.score / 100,
        "bertscore": bertscore_ref_hyp,
        "meaning_overlap": meaning_overlap(poem_ref, poem_hyp),
    }


def detect_languages(poem_src, poem_ref, poem_hyp, log_str=[]):
    """
    Detects languages and throws adequate errors.
    """
    try:
        lang_src = langdetect.detect(poem_src)
    except:
        log_str.append("Unable to recognize src language")
        lang_src = "unk"

    try:
        lang_ref = langdetect.detect(poem_ref)
    except:
        log_str.append("Unable to recognize ref language")
        lang_ref = "unk"

    try:
        lang_hyp = langdetect.detect(poem_hyp)
    except:
        log_str.append("Unable to recognize hyp language")
        lang_hyp = "unk"

    log_str.append(
        f"Recognized languages: {lang_src} -> {lang_ref} & {lang_hyp}"
    )

    if lang_ref != lang_hyp:
        log_str.append(
            "WARNING: Reference and translate version languages do not match"
        )
    if lang_src == lang_ref:
        log_str.append(
            "WARNING: Source and reference version languages are the same (not a translation)"
        )
    if lang_src == lang_hyp:
        log_str.append(
            "WARNING: Source and translated version languages are the same (not a translation)"
        )

    return lang_src, lang_ref, lang_hyp


def score_rules(rules):
    """
    Formats the rules and computes the final score.
    """
    rules = [(x[0], x[1], x[2], x[1] * x[2]) for x in rules]
    score = sum([x[3] for x in rules])
    rules = [(x[0], *[f"{y:.2f}" for y in x[1:]]) for x in rules]
    rules = pd.DataFrame(rules, columns=EXPLANATION_HEADERS)
    return score, rules


def evaluate_translation(radio_choice, poem_src, poem_ref, poem_hyp, return_dict=False):
    log_str = []

    lang_src, lang_ref, lang_hyp = detect_languages(
        poem_src, poem_ref, poem_hyp,
        log_str=log_str
    )

    if radio_choice != LABEL_REF or lang_hyp != "en" or lang_ref != "en":
        log_str.append(
            "ERROR: Only reference-based translation to English allowed currently."
        )
        log_str.append(
            "     - Continuing by disregarding this option."
        )

    eval_ref = evaluate_ref_hyp(poem_ref, poem_hyp, lang_ref, lang_hyp)

    meter_sim_best = eval_ref["meter_sim"]
    line_sim_best = eval_ref["line_sim"]
    rhyme_sim_best = eval_ref["rhyme_sim"]
    meaning_overlap_best = eval_ref["meaning_overlap"]

    # This is outside because it requires all three poem versions
    comet_score = comet_metric.compute(
        predictions=[" ".join(poem_hyp)], references=[" ".join(poem_ref)], sources=[" ".join(poem_src)]
    )["mean_score"]

    score, rules = score_rules([
        ("Meter similarity", 0.2, meter_sim_best),
        ("Line similarity", 0.1, line_sim_best),
        ("Rhyme similarity", 0.3, rhyme_sim_best),
        ("BERTScore", 0.05, eval_ref["bertscore"]),
        ("Comet", 0.1, comet_score),
        ("BLEU", 0.1, eval_ref["bleu"]),
        ("Meaning", 0.05, meaning_overlap_best),
    ])

    meter_str_ref = "".join([str(x) for x in eval_ref["meter_ref"]])
    meter_str_hyp = "".join([str(x) for x in eval_ref["meter_hyp"]])

    output = {
        "meanpoet": score,
        "explanation": rules,
        "log": "\n".join(log_str),

        # meter
        "meter_str_src": "N/A",
        "meter_str_ref": meter_str_ref + f' ({eval_ref["meter_reg_ref"]:.2})',
        "meter_str_tgt": meter_str_hyp + f' ({eval_ref["meter_reg_hyp"]:.2})',

        # rhyme
        "rhyme_str_src": "N/A",
        "rhyme_str_ref": f'{eval_ref["rhyme_ref"]} ({eval_ref["rhyme_acc_ref"]:.2f}, {eval_ref["rhyme_form_ref"]})',
        "rhyme_str_tgt": f'{eval_ref["rhyme_hyp"]} ({eval_ref["rhyme_acc_hyp"]:.2f}, {eval_ref["rhyme_form_hyp"]})',
    }

    if not return_dict:
        return tuple(output.values())

    # otherwise add extra stuff
    output |= {
        "meter_reg_src": None,
        "meter_reg_ref": eval_ref["meter_reg_ref"],
        "meter_reg_tgt": eval_ref["meter_reg_hyp"],

        "rhyme_acc_src": None,
        "rhyme_acc_ref": eval_ref["rhyme_acc_ref"],
        "rhyme_acc_tgt": eval_ref["rhyme_acc_hyp"],

        "meter_sim_ref": eval_ref["meter_sim"],
        "line_sim_ref": eval_ref["line_sim"],
        "rhyme_sim_ref": eval_ref["rhyme_sim"],

        "bleu": eval_ref["bleu"],
        "bertscore": eval_ref["bertscore"],
        "comet": comet_score,
        "meaning_overlap_ref": eval_ref["meaning_overlap"],
    }

    return output
