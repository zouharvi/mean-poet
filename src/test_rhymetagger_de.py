import rhymetagger


poem = """
Zwei Straßen gingen ab im gelben Wald,
Und leider konnte ich nicht beide reisen,
Da ich nur einer war; ich stand noch lang
Und sah noch nach, so weit es ging, der einen
Bis sie im Unterholz verschwand;
""".strip()


rt = rhymetagger.RhymeTagger()
rt.load_model(model="de")
print(rt.tag(poem.split("\n"), output_format=3))