import gradio as gr

interface = gr.Interface(
    fn=lambda x: x, inputs=None,
    outputs=gr.Markdown("""
        |a|b|c|
        |-|-|-|
        |x|y|z|
    """)
)
interface.launch(debug=True)
