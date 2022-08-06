import poesy
import pandas as pd
from sacrebleu.metrics import BLEU
from .constants import *
from .wordnet_utils import meaning_overlap, abstratness_poem
from .meter_rhyme_utils import *
from .language_detect_utils import langdetect_safe
from evaluate import load


def score_rules(rules):
    """
    Formats the rules and computes the final score.
    """
    rules = [(x[0], x[1], x[2], x[1] * x[2]) for x in rules]
    score = sum([x[3] for x in rules])
    rules = [(x[0], *[f"{y:.2f}" for y in x[1:]]) for x in rules]
    rules = pd.DataFrame(rules, columns=EXPLANATION_HEADERS)
    return score, rules


class MeanPoet:
    def __init__(self, heavy=True):
        self.heavy = heavy

        self.bleu_metric = BLEU(lowercase=True, effective_order=True)

        if heavy:
            self.comet_metric = load('comet')
            self.bertscore_metric = load("bertscore")

    def evaluate_translation(self, radio_choice, poem_src, poem_ref, poem_hyp, return_dict=False):
        log_str = []

        lang_src, lang_ref, lang_hyp = langdetect_safe(
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

        eval_ref = self.evaluate_ref_hyp(
            poem_ref, poem_hyp, lang_ref, lang_hyp
        )

        meter_sim_best = eval_ref["meter_sim_ref"]
        line_sim_best = eval_ref["line_sim_ref"]
        rhyme_sim_best = eval_ref["rhyme_sim_ref"]
        meaning_overlap_best = eval_ref["meaning_overlap"]

        if self.heavy:
            # This is outside because it requires all three poem versions
            comet_score = self.comet_metric.compute(
                predictions=[" ".join(poem_hyp)], references=[" ".join(poem_ref)], sources=[" ".join(poem_src)]
            )["mean_score"]
        else:
            comet_score = None

        if self.heavy:
            score, rules = score_rules([
                ("Meter similarity", 0.2, meter_sim_best),
                ("Line similarity", 0.1, line_sim_best),
                ("Rhyme similarity", 0.3, rhyme_sim_best),
                ("BERTScore", 0.05, eval_ref["bertscore"]),
                ("Comet", 0.1, comet_score),
                ("BLEU", 0.1, eval_ref["bleu"]),
                ("Meaning", 0.05, meaning_overlap_best),
            ])
        else:
            score, rules = score_rules([
                ("Meter similarity", 0.2, meter_sim_best),
                ("Line similarity", 0.1, line_sim_best),
                ("Rhyme similarity", 0.45, rhyme_sim_best),
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

        # start with eval_ref but overwrite some
        output |= eval_ref

        # otherwise add extra stuff
        output |= {
            "meaning_overlap_ref": eval_ref["meaning_overlap"],
            "bleu": eval_ref["bleu"],
        }
        
        # add stuff that's heavy to compute but only sometime
        if self.heavy:
            output |= {
                "bertscore": eval_ref["bertscore"],
                "comet": comet_score,
            }

        return output

    def evaluate_ref_hyp(self, poem_ref, poem_hyp, lang_ref, lang_hyp):
        """
        Complex evaluation of all aspects. Is expected to be run once against the src and once against ref.
        """
        parsed_hyp = poesy.Poem(poem_hyp)
        parsed_hyp.parse()

        # TODO: there are more features in parsed_hyp
        # print(parsed_hyp.meterd["ambiguity"], scheme_hyp["scheme"], scheme_hyp["scheme_type"])
        meter_hyp = get_meter(parsed_hyp)
        meter_reg_hyp = meter_regularity(meter_hyp)
        rhyme_hyp = get_rhyme(parsed_hyp)
        rhyme_acc_hyp = get_rhyme_acc_safe(parsed_hyp)
        
        parsed_ref = poesy.Poem(poem_ref)
        parsed_ref.parse()

        meter_ref = get_meter(parsed_ref)

        # TODO: there are more features in parsed_ref
        # print(parsed_ref.meterd["ambiguity"], scheme_ref["scheme"], scheme_ref["scheme_type"])
        meter_reg_ref = meter_regularity(meter_ref)
        rhyme_ref = get_rhyme(parsed_ref)
        rhyme_acc_ref = get_rhyme_acc_safe(parsed_ref)

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
        bleu_ref_hyp = self.bleu_metric.sentence_score(
            " ".join(poem_hyp),
            [" ".join(poem_ref)],
        )

        if self.heavy:
            # take f1 score
            bertscore_ref_hyp = self.bertscore_metric.compute(
                predictions=[" ".join(poem_hyp)], references=[[" ".join(poem_ref)]],
                lang=lang_hyp,
            )["f1"][0]
        else:
            bertscore_ref_hyp = None

        abstractness_ref = abstratness_poem(poem_ref)
        abstractness_hyp = abstratness_poem(poem_hyp)
        abstractness_sim = 1- abs(abstractness_ref-abstractness_hyp)
        
        return {
            "abstractness_sim": abstractness_sim,
            "abstractness_ref": abstractness_ref,
            "abstractness_hyp": abstractness_hyp,

            "meter_sim_ref": meter_sim,
            "line_sim_ref": line_sim,
            "rhyme_sim_ref": rhyme_sim,

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
