#!/usr/bin/env python3

from code import interact
import gradio as gr
from workers_evaluate import evaluate_translation
from workers_translate import translate_poem
from constants import *

interface = gr.Blocks()

with interface:
    gr.Markdown("Translate a poem or evaluate a translation using this demo.")
    with gr.Tabs(selected=1) as tabs:
        with gr.TabItem("Evaluate translation", id=1):
            with gr.Row():
                with gr.Column():
                    evaluate_src = gr.Textbox(
                        lines=10, max_lines=20, label="Source poem",
                        value=DEMO_POEM_SRC,
                    )

                with gr.Column():
                    evaluate_ref = gr.Textbox(
                        lines=10, max_lines=20, label="Reference translation",
                        value=DEMO_POEM_REF,

                    )

                with gr.Column():
                    evaluate_hyp = gr.Textbox(
                        lines=10, max_lines=20, label="Hypothesis translation",
                        value=DEMO_POEM_HYP,
                    )

            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        with gr.Column():
                            analysis_meter_src = gr.Textbox(
                                label="Source meter (regularity)"
                            )
                            analysis_rhyme_src = gr.Textbox(
                                label="Source rhyme (accuracy, target)"
                            )
                        with gr.Column():
                            analysis_meter_ref = gr.Textbox(
                                label="Reference meter (regularity)"
                            )
                            analysis_rhyme_ref = gr.Textbox(
                                label="Reference rhyme (accuracy, target)"
                            )
                        with gr.Column():
                            analysis_meter_hyp = gr.Textbox(
                                label="New meter (regularity)"
                            )
                            analysis_rhyme_hyp = gr.Textbox(
                                label="New rhyme (accuracy, target)"
                            )
                    with gr.Row():
                        with gr.Column():
                            evaluate_score = gr.Label(
                                label="Score",
                            )
                            radio_evaluate = gr.Radio(
                                choices=[
                                    LABEL_SRC_REF,
                                    LABEL_SRC,
                                    LABEL_REF,
                                ],
                                value=LABEL_REF,
                                label="What to evaluate translation against?",
                                interactive=True,
                            )
                            with gr.Row():
                                button_evaluate = gr.Button("Evaluate",)
                            log_evaluate = gr.Textbox(
                                label="Log",
                                interactive=False,
                                lines=4,
                            )

                        with gr.Column():
                            evaluate_explanation = gr.Dataframe(
                                headers=EXPLANATION_HEADERS,
                                label="Explanation (sum of last column)",
                                row_count=2,
                                col_count=4,
                                type="pandas",
                                interactive=False,
                            )
        with gr.TabItem("Translate poem", id=2):
            with gr.Row():
                with gr.Column():
                    translate_src = gr.Textbox(
                        lines=10, max_lines=20, label="Source poem",
                        value=DEMO_POEM_SRC,
                    )
                    with gr.Row():
                        button_translate = gr.Button("Translate")
                with gr.Column():
                    translate_hyp = gr.Textbox(
                        lines=10, max_lines=20, label="Translated poem"
                    )
                    with gr.Row():
                        button_copy_to_eval = gr.Button("Translate & evaluate")

        with gr.TabItem("Recite poem", id=3):
            with gr.Row():
                with gr.Column():
                    recite_src = gr.Textbox(
                        lines=10, max_lines=20, label="Source poem",
                        value=DEMO_POEM_HYP,
                    )
                    with gr.Row():
                        button_recite = gr.Button("Compile recitation")
                with gr.Column():
                    outputs_recite_1 = gr.Audio(
                        interactive=False, label="Recited poem"
                    )

    # set up events

    button_translate.click(
        translate_poem,
        inputs=[translate_src],
        outputs=[translate_hyp]
    )
    button_evaluate.click(
        evaluate_translation,
        inputs=[
            radio_evaluate,
            evaluate_src, evaluate_ref, evaluate_hyp
        ],
        outputs=[
            evaluate_score, evaluate_explanation, log_evaluate,
            analysis_meter_src, analysis_meter_ref, analysis_meter_hyp,
            analysis_rhyme_src, analysis_rhyme_ref, analysis_rhyme_hyp,
        ],
    )

    # pass data
    button_copy_to_eval.click(
        lambda poem: (poem, translate_poem(poem)),
        inputs=[translate_src],
        outputs=[evaluate_ref, evaluate_hyp]
    )

    # switch tabs
    button_copy_to_eval.click(
        inputs=None, outputs=tabs, fn=lambda: gr.Tabs.update(selected=1)
    )

# interface.launch(daemon=True)
interface.launch(server_port=None, prevent_thread_lock=True)
# gr.close_all()
input()
interface.close()
