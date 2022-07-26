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
DEMO_MDESC_SRC = "fixed pentameter, iambic"
DEMO_MDESC_REF = "fixed pentameter, iambic"
DEMO_MDESC_HYP = "hexameter + pentameter, iambic (irregular)"
DEMO_RHYME_SRC = "ABAAB"
DEMO_RHYME_REF = "ABAAB"
DEMO_RHYME_HYP = "ABABC"

def translate_poem(poem):
    return DEMO_POEM_HYP

def meter_regularity(meter):
    """
    Output is bounded [0, 1]
    """
    score = 0
    for i in range(1, len(meter)):
        if meter[i-1]==meter[i]:
            score += 2
        elif abs(meter[i-1]-meter[i]) < 1:
            score += 1
    return score/(len(meter)-1)/2

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

def evaluate_vs_hyp(poem, poem_hyp):
    # stress_count = [[px.meterVal for px in p.positions] for p in parsed.bestParses()]
    # print(stress_count)
    import prosodic

    if poem == DEMO_POEM_SRC:
        # debug todo
        regularity_xxx = meter_regularity(DEMO_METER_SRC)
        meter_xxx = ", ".join([str(x) for x in DEMO_METER_SRC])
    else:
        parsed_xxx = prosodic.Text(poem, lang="en", printout=False)
        parsed_xxx.parse()
        meter_xxx = [p.str_meter().count("s") for p in parsed_xxx.bestParses()]
        regularity_xxx = meter_regularity(meter_xxx)
        meter_xxx = ", ".join([str(x) for x in meter_xxx])


    # TODO: this computation is duplicated
    parsed_hyp = prosodic.Text(poem_hyp, lang="en", printout=False)
    parsed_hyp.parse()
    meter_hyp = [p.str_meter().count("s") for p in parsed_hyp.bestParses()]
    regularity_hyp = meter_regularity(meter_hyp)
    meter_hyp = ", ".join([str(x) for x in meter_hyp])

    meter_sim = meter_regularity_sim(regularity_xxx, regularity_hyp)
    line_sim = line_count_sim(poem.count("\n"), poem_hyp.count("\n"))
    print(line_sim, poem.count("\n"), poem_hyp.count("\n"))

    return {
        "meter_sim": meter_sim,
        "line_sim": line_sim,
        "meter_xxx": meter_xxx,
        "meter_hyp": meter_hyp,
    }

def evaluate_translation(poem_src, poem_ref, poem_hyp):
    eval_src = evaluate_vs_hyp(poem_src, poem_hyp)
    eval_ref = evaluate_vs_hyp(poem_ref, poem_hyp)
    
    meter_sim_best = max(eval_src["meter_sim"], eval_ref["meter_sim"])
    line_sim_best = max(eval_ref["line_sim"], eval_ref["line_sim"])

    score = 0.9 * meter_sim_best + 0.1 * line_sim_best
    return (
        f"{score:.3f}",
        f"""### Explanation (sum):
        
        TODO: change this to a table

        |Σ|Meter similarity|Line similarity|TODO|
        |-|-|-|-|
        |{score:.2f} |0.9 × **{meter_sim_best:.2f}** | 0.1 × **{line_sim_best:.2f}** | TODO |
        """,
        eval_src["meter_xxx"], eval_ref["meter_xxx"], eval_src["meter_xxx"],
        DEMO_MDESC_SRC, DEMO_MDESC_REF, DEMO_MDESC_HYP,
        DEMO_RHYME_SRC, DEMO_RHYME_REF, DEMO_RHYME_HYP,
    )