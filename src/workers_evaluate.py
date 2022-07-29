import langdetect
from rhymetagger import RhymeTagger
import poesy
import pandas as pd
from sacrebleu.metrics import BLEU
from constants import *
from wordnet_utils import meaning_overlap

bleu = BLEU(lowercase=True, effective_order=True)


def meter_regularity(meter):
    """
    Output is bounded [0, 1]
    """
    score = 0
    # look at patterns
    # TODO: replace with smarter Poesy
    for i in range(1, len(meter)):
        if meter[i - 1] == meter[i]:
            score += 2
        elif abs(meter[i - 1] - meter[i]) < 1:
            score += 1
    return score / (max(len(meter) - 1, 1)) / 2


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
    return [y for x, y in parsed.linelengths_bybeat.items()]


def evaluate_vs_hyp(poem_xxx, poem_hyp, lang_xxx, lang_hyp, eval_hyp=None):
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
        rhyme_hyp = "".join(parsed_hyp.rhyme_ids).replace("-", "?").upper()
        rhyme_acc_hyp = parsed_hyp.rhymed["rhyme_scheme_accuracy"]

    parsed_xxx = poesy.Poem(poem_xxx)
    parsed_xxx.parse()

    meter_xxx = get_meter(parsed_xxx)

    # TODO: there are more features in parsed_xxx
    # print(parsed_xxx.meterd["ambiguity"], scheme_xxx["scheme"], scheme_xxx["scheme_type"])
    meter_reg_xxx = meter_regularity(meter_xxx)

    rhyme_xxx = "".join(parsed_xxx.rhyme_ids).replace("-", "?").upper()
    rhyme_acc_xxx = parsed_xxx.rhymed["rhyme_scheme_accuracy"]

    # parsed_hyp.rhymed["rhyme_scheme_accuracy"] could also be used for fixed rhymes
    # parsed_hyp.rhyme_ids intensity could also be used for fixed rhymes

    meter_sim = meter_regularity_sim(meter_reg_xxx, meter_reg_hyp)
    line_sim = line_count_sim(
        poem_xxx.count("\n") + 1,
        poem_hyp.count("\n") + 1
    )
    rhyme_sim = rhyme_intensity_sim(rhyme_acc_xxx, rhyme_acc_hyp)

    # this assumes that poem_xxx is reference
    # will yield random results on source (probably)
    bleu_xxx_hyp = bleu.sentence_score(
        " ".join(poem_hyp),
        [" ".join(poem_xxx)],
    )

    return {
        "meter_sim": meter_sim,
        "line_sim": line_sim,
        "rhyme_sim": rhyme_sim,

        "meter_xxx": meter_xxx,
        "meter_hyp": meter_hyp,
        "meter_reg_xxx": meter_reg_xxx,
        "meter_reg_hyp": meter_reg_hyp,

        "rhyme_xxx": rhyme_xxx,
        "rhyme_hyp": rhyme_hyp,
        "rhyme_acc_xxx": rhyme_acc_xxx,
        "rhyme_acc_hyp": rhyme_acc_hyp,
        "rhyme_form_xxx": parsed_xxx.rhymed["rhyme_scheme_form"],
        "rhyme_form_hyp": parsed_hyp.rhymed["rhyme_scheme_form"],

        "bleu_xxx_hyp": bleu_xxx_hyp.score / 100,
        "meaning_overlap": meaning_overlap(poem_xxx, poem_hyp),
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


def evaluate_translation(radio_choice, poem_src, poem_ref, poem_hyp):
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

    eval_ref = evaluate_vs_hyp(poem_ref, poem_hyp, lang_ref, lang_hyp)

    meter_sim_best = eval_ref["meter_sim"]
    line_sim_best = eval_ref["line_sim"]
    rhyme_sim_best = eval_ref["rhyme_sim"]
    bleu_best = eval_ref["bleu_xxx_hyp"]
    meaning_overlap_best = eval_ref["meaning_overlap"]

    score, rules = score_rules([
        ("Meter similarity", 0.5, meter_sim_best),
        ("Line similarity", 0.1, line_sim_best),
        ("Rhyme similarity", 0.2, rhyme_sim_best),
        ("BLEU", 0.1, bleu_best),
        ("Meaning", 0.1, meaning_overlap_best),
    ])

    meter_str_xxx = "".join([str(x) for x in eval_ref["meter_xxx"]])
    meter_str_hyp = "".join([str(x) for x in eval_ref["meter_hyp"]])

    return (
        f"{score:.3f}", rules, "\n".join(log_str),

        # meter
        "N/A",
        meter_str_xxx + f' ({eval_ref["meter_reg_xxx"]:.2})',
        meter_str_hyp + f' ({eval_ref["meter_reg_hyp"]:.2})',

        # rhyme
        "N/A",
        f'{eval_ref["rhyme_xxx"]} ({eval_ref["rhyme_acc_xxx"]:.2f}, {eval_ref["rhyme_form_xxx"]})',
        f'{eval_ref["rhyme_hyp"]} ({eval_ref["rhyme_acc_hyp"]:.2f}, {eval_ref["rhyme_form_hyp"]})',
    )
