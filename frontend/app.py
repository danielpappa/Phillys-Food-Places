import gradio as gr
import backend.TextGenerator as rag

ragger = rag.TextGenerator("google/gemma-2b-it", "danielpappa/philly_restaurants")

gr.ChatInterface(ragger.generate_response, title = "🌭🍗 philly's food places 🍣🍔".capitalize(), examples = ["Where could I get some good Mexican food?", "What is the best pizza in town?", "Give me some healthy dining options nearby."], theme="freddyaboulton/test-blue", submit_btn = None, stop_btn = None, retry_btn = None, undo_btn = None, clear_btn = None).launch()