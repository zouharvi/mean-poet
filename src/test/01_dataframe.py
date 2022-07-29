import gradio as gr
import numpy as np

interface = gr.Interface(
    fn=lambda: [
        ["x1", "y1"],
        ["x2", "y2"],
        ["x3", "y3"],
    ],
    inputs=None,
    outputs=gr.Dataframe(
        col_count=2,
        row_count=3,
        type="array",
        headers=["A", "B"],
        interactive=False,
    )
)
interface.launch(debug=True)
