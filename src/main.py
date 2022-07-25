#!/usr/bin/env python3

import gradio as gr
from torch import full
from workers import translate_poem, evaluate_translation
from workers import DEMO_POEM_ORIGINAL, DEMO_POEM_TRANSLATION

interface = gr.Blocks()

with interface:
    gr.Markdown("Translate a poem or evaluate a translation using this demo.")
    with gr.Tabs(selected=1) as tabs:
        with gr.TabItem("Evaluate translation", id=1):
            with gr.Row():
                with gr.Column():
                    inputs_evaluate_1 = gr.Textbox(
                        lines=10, max_lines=20, label="Original poem",
                        value=DEMO_POEM_ORIGINAL,

                    )
                with gr.Column():
                    inputs_evaluate_2 = gr.Textbox(
                        lines=10, max_lines=20, label="Translated poem",
                        value=DEMO_POEM_TRANSLATION,
                    )

            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        with gr.Column():
                            outputs_analysis_meter_1 = gr.Textbox(
                                label="Original meter"
                            )
                            outputs_analysis_mdesc_1 = gr.Textbox(
                                label="Original meter description"
                            )
                            outputs_analysis_rhyme_1 = gr.Textbox(
                                label="Original rhyme"
                            )
                        with gr.Column():
                            outputs_analysis_meter_2 = gr.Textbox(
                                label="New meter"
                            )
                            outputs_analysis_mdesc_2 = gr.Textbox(
                                label="New meter description"
                            )
                            outputs_analysis_rhyme_2 = gr.Textbox(
                                label="New rhyme"
                            )

                with gr.Column():
                    outputs_evaluate_1 = gr.Label(
                        label="Score",
                    )

            with gr.Row():
                button_evaluate = gr.Button("Evaluate",)
                button_evaluate_translate = gr.Button("Translate")


        with gr.TabItem("Translate poem", id=2):
            with gr.Row():
                with gr.Column():
                    inputs_translate_1 = gr.Textbox(
                        lines=10, max_lines=20, label="Original poem",
                        value=DEMO_POEM_ORIGINAL,
                    )
                    with gr.Row():
                        button_translate = gr.Button("Translate")
                with gr.Column():
                    outputs_translate_1 = gr.Textbox(
                        lines=10, max_lines=20, label="Translated poem"
                    )
                    with gr.Row():
                        button_copy_to_eval = gr.Button("Translate & evaluate")

        with gr.TabItem("Recite poem", id=3):
            with gr.Row():
                with gr.Column():
                    inputs_recite_1 = gr.Textbox(
                        lines=10, max_lines=20, label="Original poem",
                        value=DEMO_POEM_ORIGINAL,
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
        inputs=[inputs_translate_1],
        outputs=[outputs_translate_1]
    )
    button_evaluate.click(
        evaluate_translation,
        inputs=[inputs_evaluate_1, inputs_evaluate_2],
        outputs=[
            outputs_evaluate_1,
            outputs_analysis_meter_1, outputs_analysis_meter_2,
            outputs_analysis_mdesc_1, outputs_analysis_mdesc_2,
            outputs_analysis_rhyme_1, outputs_analysis_rhyme_2,
        ],
    )

    # pass data
    button_copy_to_eval.click(
        lambda poem: (poem, translate_poem(poem)),
        inputs=[inputs_translate_1],
        outputs=[inputs_evaluate_1, inputs_evaluate_2]
    )

    # switch tabs
    button_copy_to_eval.click(inputs=None, outputs=tabs, fn=lambda: gr.Tabs.update(selected=1))


# interface.launch(daemon=True)
interface.launch()
