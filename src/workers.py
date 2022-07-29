import langdetect
from rhymetagger import RhymeTagger
import poesy
import pandas as pd

DEMO_POEM_SRC = """
Zwei Straßen gingen ab im gelben Wald,
Und leider konnte ich nicht beide reisen,
Da ich nur einer war; ich stand noch lang
Und sah noch nach, so weit es ging, der einen
Bis sie im Unterholz verschwand;
""".strip()

DEMO_POEM_REF = """
Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;
""".strip()

DEMO_POEM_HYP = """
Two reads went the other way in a yellow wood
and sorry I could not go both ways
and since alone I was, I stood for long
and examined how far one of them went
until it disappeared in the bushes;
""".strip()

LABEL_SRC_REF = "Source & Reference"
LABEL_SRC = "Source"
LABEL_REF = "Reference"

EXPLANATION_HEADERS = [
    "Variable", "Coefficient",
    "Value", "Multiplied value"
]

EVAL_DUMMY = {
    "meter_sim": float("-inf"),
    "line_sim": float("-inf"),
    "meter_xxx": "4444",
    "meter_hyp": "4444",
}


def translate_poem(poem):
    return DEMO_POEM_HYP


def meter_regularity(meter):
    """
    Output is bounded [0, 1]
    """
    score = 0
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
    return [y for x,y in parsed.linelengths_bybeat.items()]

def evaluate_vs_hyp(poem_xxx, poem_hyp, lang_xxx, lang_hyp, eval_hyp=None):
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
    }


def detect_languages(poem_src, poem_ref, poem_hyp, log_str=[]):
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


def rhymetag_poem(poem, lang):
    rt = RhymeTagger()
    rt.load_model(model=lang)
    rhyme = rt.tag(poem.split("\n"), output_format=3)
    rhyme = [
        "ABCDEFGHIJKL"[i] if i is not None else "?"
        for i in rhyme
    ]
    return "".join(rhyme)


def score_rules(rules):
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

    score, rules = score_rules([
        ["Meter similarity", 0.6, meter_sim_best, 0.6 * meter_sim_best],
        ["Line similarity", 0.1, line_sim_best, 0.1 * line_sim_best],
        ["Rhyme similarity", 0.3, rhyme_sim_best, 0.3 * rhyme_sim_best],
    ])

    meter_str_xxx = "".join([str(x) for x in eval_ref["meter_xxx"]])
    meter_str_hyp = "".join([str(x) for x in eval_ref["meter_hyp"]])

    return (
        f"{score:.3f}", rules, "\n".join(log_str),

        # meter
        "N/A",
        meter_str_xxx + f' ({eval_ref["meter_reg_xxx"]})',
        meter_str_hyp + f' ({eval_ref["meter_reg_hyp"]})',

        # rhyme
        "N/A",
        f'{eval_ref["rhyme_xxx"]} ({eval_ref["rhyme_acc_xxx"]:.2f}, {eval_ref["rhyme_form_xxx"]})',
        f'{eval_ref["rhyme_hyp"]} ({eval_ref["rhyme_acc_hyp"]:.2f}, {eval_ref["rhyme_form_hyp"]})',
    )
