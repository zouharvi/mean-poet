
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
And since alone I was, I stood for long
and examined how far one of them went
until it disappeared in the bushes;
""".strip()

DEMO_POEM_SRC = """
Sbohem a kdybychom se nikdy nesetkali
bylo to překrásné a bylo toho dost
Sbohem a kdybychom si spolu schůzku dali
možná že nepřijdem že přijde jiný host

Es war schön, aber alles hat ein Ende
Sei stumm, Kirchenglocke, ich kenne diese Traurigkeit schon
Kuss, Taschentuch, Sirene, Schiffsglocke
drei- oder viermal lächeln und dann in Ruhe gelassen werden

Żegnaj i jeśli już nie będziemy rozmawiać
niech mała pamięć pozostanie za nami
zwiewna jak chusteczka prostsza niż pocztówka
i trochę odurzający jak zapach blichtru
""".strip()

# Roman Kostovski
# https://web-p-ebscohost-com.ezproxy.is.cuni.cz/ehost/ebookviewer/ebook/ZTAwMHh3d19fMjY5MzAwNV9fQU41?sid=dfba09c8-1bc4-4e09-a5ac-389601708be8%40redis&vid=0&format=EB&lpid=lp_161&rid=0
DEMO_POEM_REF = """
Farewell, and if we no longer meet
Our time was marvelous - we've shared enough
Farewell, and soon our dates will be
With someone new, someone else's love

Our time was marvelous but all things end
Be silent knell your sorrow is quite clear
A kiss, a handkerchief, a ship's bell, a siren
One last smile as we part from here

Farewell and if we never speak again
Let a small memory of us unfold
Lighter than a handkerchief fluttering in the wind
Tempting as the scent of gleaming gold
""".strip()

# Václav Z. J. Pinkava
# https://www.babelmatrix.org/works/cz/Nezval%2C_V%C3%ADt%C4%9Bzslav-1900/Sbohem_a_%C5%A1%C3%A1te%C4%8Dek/en/63830-Goodbye_and_a_wave
DEMO_POEM_HYP = """
Goodbye and if we should not ever meet anew
it really was delightful and quite enough for some
Goodbye and if we should yet make a rendezvous
maybe instead of us another guest will come

It really was delightful but everything has an end
Hush tolling bell I know that sadness from before
A kiss a napkin siren ship's bell to portend
three or four smiles and then to be alone once more

Goodbye and if we should not ever speak again
let there be something left a keepsake what we meant
as airy as a napkin more than a postcard plain
with a supposed scent of gilded ornament
""".strip()

LABEL_SRC_REF = "Source & Reference"
LABEL_SRC = "Source"
LABEL_REF = "Reference"

EXPLANATION_HEADERS = [
    "Variable", "Coefficient",
    "Value", "Multiplied value"
]

