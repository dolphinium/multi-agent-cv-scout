import gradio as gr
from src.graph import create_workflow
import json

# Create the compiled workflow app
graph_app = create_workflow()

def process_resume(file):
    if file is None:
        return "Please upload a resume."
    
    # The input to the graph is a dictionary with the file path
    inputs = {"file_path": file.name}
    
    # Invoke the graph
    try:
        result_state = graph_app.invoke(inputs)
        final_report = result_state.get("final_report", {})
        
        # Return the JSON formatted nicely
        return json.dumps(final_report, indent=2)
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Define the Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# CV-Scout: Multi-Agent Resume Intelligence System")
    gr.Markdown("Upload a resume PDF to extract structured information.")
    
    with gr.Row():
        file_input = gr.File(label="Upload Resume PDF", file_types=[".pdf"])
        json_output = gr.JSON(label="Extracted Information")
        
    process_button = gr.Button("Process Resume")
    process_button.click(fn=process_resume, inputs=file_input, outputs=json_output)

if __name__ == "__main__":
    demo.launch(share=True)