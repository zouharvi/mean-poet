DEMO_POEM_TRANSLATION = """
Zwei Straßen gingen ab im gelben Wald,
Und leider konnte ich nicht beide reisen,
Da ich nur einer war; ich stand noch lang
Und sah noch nach, so weit es ging, der einen
Bis sie im Unterholz verschwand;
""".strip()

DEMO_POEM_ORIGINAL = """
Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;
""".strip()

DEMO_METER_ORIGINAL = "4, 4, 4, 4, 4"
DEMO_METER_TRANSLATION = "6, 6, 5, 5, 5"
DEMO_MDESC_ORIGINAL = "fixed pentameter, iambic"
DEMO_MDESC_TRANSLATION = "hexameter + pentameter, iambic (irregular)"
DEMO_RHYME_ORIGINAL = "ABAAB"
DEMO_RHYME_TRANSLATION = "ABABC"


def translate_poem(poem):
    return DEMO_POEM_TRANSLATION

def evaluate_translation(poem_1, poem_2):
    return (
        "0.799 (0.998 × 0.801)",
        DEMO_METER_ORIGINAL, DEMO_METER_TRANSLATION,
        DEMO_MDESC_ORIGINAL, DEMO_MDESC_TRANSLATION,
        DEMO_RHYME_ORIGINAL, DEMO_RHYME_TRANSLATION,
    )
