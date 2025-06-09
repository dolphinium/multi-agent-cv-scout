import gradio as gr
from src.graph import create_workflow
import json
import logging

# Import custom exceptions
from src.schemas import PDFParsingError, ExtractionError, StandardizationError, RelevancyAnalysisError, CVScoutError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create the compiled workflow app
graph_app = create_workflow()

def process_resume(file, job_description):
    if file is None:
        return "Please upload a resume.", ""
    
    # The input to the graph is a dictionary with the file path and job description
    inputs = {
        "file_path": file.name,
        "job_description": job_description
    }
    
    analysis_report = "Analysis not run (no job description provided)."
    
    # Invoke the graph
    try:
        result_state = graph_app.invoke(inputs)
        
        # Extract the final report JSON
        final_report = result_state.get("final_report", {})
        report_json = json.dumps(final_report, indent=2)

        # Extract the analysis if it exists
        if result_state.get("match_score") is not None:
            score = result_state["match_score"]
            summary = result_state["match_summary"]
            analysis_report = (
                f"## Job Match Analysis\n"
                f"**Compatibility Score:** {score}/100\n\n"
                f"**Summary:**\n{summary}"
            )

        return report_json, analysis_report

    except PDFParsingError as e:
        error_message = f"Error during PDF parsing: {e}"
        logging.error(error_message)
        return error_message, error_message
    except ExtractionError as e:
        error_message = f"Error during information extraction: {e}"
        logging.error(error_message)
        return error_message, error_message
    except StandardizationError as e:
        error_message = f"Error during data standardization: {e}"
        logging.error(error_message)
        return error_message, error_message
    except RelevancyAnalysisError as e:
        error_message = f"Error during relevancy analysis: {e}"
        logging.error(error_message)
        return error_message, error_message
    except CVScoutError as e:
        error_message = f"An agent workflow error occurred: {e}"
        logging.error(error_message)
        return error_message, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logging.error(error_message)
        return error_message, error_message

# Define the Gradio interface
with gr.Blocks(theme=gr.themes.Glass()) as demo:
    gr.Markdown("# CV-Scout: Multi-Agent Resume Intelligence System")
    gr.Markdown("Upload a resume PDF and optionally provide a job description to get a full analysis.")
    
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload Resume PDF", file_types=[".pdf"])
            jd_input = gr.Textbox(label="Job Description", lines=10, placeholder="Paste the job description here...")
            process_button = gr.Button("Process Resume", variant="primary")
            
        with gr.Column(scale=2):
            gr.Markdown("### Analysis Report")
            analysis_output = gr.Markdown()
            gr.Markdown("### Extracted Resume Data (JSON)")
            json_output = gr.JSON()
            
    process_button.click(
        fn=process_resume, 
        inputs=[file_input, jd_input], 
        outputs=[json_output, analysis_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)