import poesy
import sacrebleu

POEM_R = """
Who rides so late through the night and wind?
It is the father with his child.
He has the boy in his arms;
he holds him safely, he keeps him warm.
""".strip()

POEM_1 = """
Who rides so late on a night so wild?
A father, through darkness and wind, with his child.
He holds the youngster. His arm is tight
To keep him warm in the cold of the night.
""".strip()

POEM_2 = """
Who is riding so late, with his child,
through night and wind? It is the father who
In his arms he holds the boy,
He holds him safely, warm he keeps him.
""".strip()

score_chrf_1 = sacrebleu.metrics.CHRF().sentence_score(POEM_1, [POEM_R]).score
score_chrf_2 = sacrebleu.metrics.CHRF().sentence_score(POEM_2, [POEM_R]).score
score_bleu_1 = sacrebleu.metrics.BLEU().sentence_score(POEM_1, [POEM_R]).score
score_bleu_2 = sacrebleu.metrics.BLEU().sentence_score(POEM_2, [POEM_R]).score

print("ChrF", score_chrf_1, score_chrf_2)
print("BLEU", score_bleu_1, score_bleu_2)

parsed_r = poesy.Poem(POEM_R)
parsed_1 = poesy.Poem(POEM_1)
parsed_2 = poesy.Poem(POEM_2)
print()
parsed_r.summary()
print()
parsed_1.summary()
print()
parsed_2.summary()