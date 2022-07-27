import langdetect
from rhymetagger import RhymeTagger
import prosodic

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

DEMO_METER_SRC = [4, 4, 4, 4, 4]
DEMO_MDESC_SRC = "TODO"
DEMO_MDESC_REF = "TODO"
DEMO_MDESC_HYP = "TODO"
DEMO_RHYME_SRC = "ABAAB"
DEMO_RHYME_REF = "ABAAB"
DEMO_RHYME_HYP = "ABABC"

LABEL_SRC_REF = "Source & Reference"
LABEL_SRC = "Source"
LABEL_REF = "Reference"

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
        if meter[i-1] == meter[i]:
            score += 2
        elif abs(meter[i-1]-meter[i]) < 1:
            score += 1
    return score/(max(len(meter)-1, 1))/2


def meter_regularity_sim(reg_1, reg_2):
    """
    Output is bounded [0, 1]
    """
    return 1-abs(reg_1 - reg_2)


def line_count_sim(count_1, count_2):
    """
    Output is bounded [0, 1]
    """
    return min(count_1, count_2)/max(count_1, count_2)


def evaluate_vs_hyp(poem_xxx, poem_hyp, lang_xxx, lang_hyp, eval_hyp=None):

    # reuse previous computation
    if eval_hyp is not None:
        rhyme_hyp = eval_hyp["rhyme_hyp"]
        meter_hyp = eval_hyp["meter_hyp"]
    else:
        rhyme_hyp = rhymetag_poem(poem_hyp, lang_hyp)
        parsed_hyp = prosodic.Text(poem_hyp, lang=lang_hyp, printout=False)
        parsed_hyp.parse()
        meter_hyp = [p.str_meter().count("s") for p in parsed_hyp.bestParses()]

    if poem_xxx == DEMO_POEM_SRC:
        # debug TODO
        meter_xxx = DEMO_METER_SRC
    else:
        # TODO: this will fail because prosodic does not support german out of the box
        parsed_xxx = prosodic.Text(poem_xxx, lang=lang_xxx, printout=False)
        parsed_xxx.parse()
        meter_xxx = [p.str_meter().count("s") for p in parsed_xxx.bestParses()]

    rhyme_xxx = rhymetag_poem(poem_xxx, lang_xxx)

    regularity_hyp = meter_regularity(meter_hyp)
    regularity_xxx = meter_regularity(meter_xxx)

    meter_sim = meter_regularity_sim(regularity_xxx, regularity_hyp)
    line_sim = line_count_sim(poem_xxx.count("\n")+1, poem_hyp.count("\n")+1)

    return {
        "meter_sim": meter_sim,
        "line_sim": line_sim,
        "rhyme_sim": 0,
        "meter_xxx": meter_xxx,
        "meter_hyp": meter_hyp,
        "rhyme_xxx": rhyme_xxx,
        "rhyme_hyp": rhyme_hyp,
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
            "WARNING: Reference and translate version languages do not match")
    if lang_src == lang_ref:
        log_str.append(
            "WARNING: Source and reference version languages are the same (not a translation)")
    if lang_src == lang_hyp:
        log_str.append(
            "WARNING: Source and translated version languages are the same (not a translation)")

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


def evaluate_translation(radio_choice, poem_src, poem_ref, poem_hyp):
    log_str = []

    lang_src, lang_ref, lang_hyp = detect_languages(
        poem_src, poem_ref, poem_hyp,
        log_str=log_str
    )

    if radio_choice == LABEL_SRC_REF:
        eval_src = evaluate_vs_hyp(poem_src, poem_hyp, lang_src, lang_hyp)
        # reuse computed parts from eval_src
        eval_ref = evaluate_vs_hyp(
            poem_ref, poem_hyp, lang_ref, lang_hyp, eval_hyp=eval_src
        )
    elif radio_choice == LABEL_SRC:
        eval_src = evaluate_vs_hyp(poem_src, poem_hyp, lang_src, lang_hyp,)
        eval_ref = EVAL_DUMMY
    elif radio_choice == LABEL_REF:
        eval_ref = evaluate_vs_hyp(poem_ref, poem_hyp, lang_ref, lang_hyp,)
        eval_src = EVAL_DUMMY

    meter_sim_best = max(eval_src["meter_sim"], eval_ref["meter_sim"])
    line_sim_best = max(eval_src["line_sim"], eval_ref["line_sim"])

    score = 0.9 * meter_sim_best + 0.1 * line_sim_best
    return (
        f"{score:.3f}",
        [
            ["Meter similarity", 0.9, meter_sim_best, 0.9 * meter_sim_best],
            ["Line similarity", 0.1, line_sim_best, 0.1 * line_sim_best],
        ],
        "\n".join(log_str),
        "".join([str(x) for x in eval_src["meter_xxx"]]),
        "".join([str(x) for x in eval_ref["meter_xxx"]]),
        "".join([str(x) for x in eval_src["meter_hyp"]]),
        DEMO_MDESC_SRC, DEMO_MDESC_REF, DEMO_MDESC_HYP,
        eval_src["rhyme_xxx"],
        eval_ref["rhyme_xxx"],
        eval_src["rhyme_hyp"],
    )
