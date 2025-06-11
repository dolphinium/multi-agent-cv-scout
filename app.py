import gradio as gr
import pandas as pd
import re 
from src.graph import create_workflow
from src.database import add_job, get_all_jobs, get_ranked_candidates_for_job
from src.email_graph import create_email_workflow 
from src.database import add_job, get_all_jobs, get_ranked_candidates_for_job
import logging
import os

# Import custom exceptions
from src.schemas import PDFParsingError, ExtractionError, StandardizationError, RelevancyAnalysisError, CVScoutError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the compiled workflow app
graph_app = create_workflow()
email_app = create_email_workflow()

# --- Functions for Tab 1: Processing ---

def process_resumes_and_job(files, job_description, progress=gr.Progress()):
    if not files:
        raise gr.Error("Please upload at least one resume PDF.")
    if not job_description or not job_description.strip():
        raise gr.Error("Please provide a job description.")

    logger.info(f"---APP: Starting batch processing for {len(files)} resumes.---")

    try:
        job_id = add_job(job_description)
    except Exception as e:
        error_message = f"Error saving job description to database: {e}"
        logger.error(error_message)
        raise gr.Error(error_message)

    processed_count = 0
    error_count = 0
    error_messages = []
    total_files = len(files)

    for i, file in enumerate(files):
        progress(i / total_files, desc=f"Processing {os.path.basename(file.name)}")
        try:
            inputs = {
                "file_path": file.name,
                "job_description": job_description,
                "job_id": job_id
            }
            result_state = graph_app.invoke(inputs)
            
            if result_state.get("candidate_id") is not None:
                processed_count += 1
            else:
                error_count += 1
                error_messages.append(f"- {os.path.basename(file.name)}: Processing completed but no candidate ID was returned.")

        except (PDFParsingError, ExtractionError, StandardizationError, RelevancyAnalysisError, CVScoutError) as e:
            error_count += 1
            error_messages.append(f"- {os.path.basename(file.name)}: {e}")
        except Exception as e:
            error_count += 1
            error_messages.append(f"- {os.path.basename(file.name)}: An unexpected error occurred: {str(e)}")

    summary_report = f"## Batch Processing Complete\n\n"
    summary_report += f"✅ **Successfully Processed:** {processed_count} resume(s)\n"
    if error_count > 0:
        summary_report += f"❌ **Failed:** {error_count} resume(s)\n\n"
        summary_report += "**Error Details:**\n" + "\n".join(error_messages)
    
    return "Batch processing finished. Results are saved to the database. Check the 'Candidate Dashboard' tab.", summary_report

# --- Functions for Tab 2: Dashboard ---

def update_job_dropdown():
    jobs = get_all_jobs()
    job_choices = [job[0] for job in jobs]
    return gr.Dropdown(choices=job_choices, label="Select a Job Description", interactive=True)

# *** MAJOR CHANGE HERE: This function now populates the CheckboxGroup and the DataFrame ***
def load_candidate_dashboard(job_display_string: str):
    """Loads ranked candidates and populates both the checkbox selector and the details table."""
    if not job_display_string:
        # Return empty state for all three components
        return gr.CheckboxGroup(choices=[]), pd.DataFrame(), gr.Button(interactive=False)
    
    try:
        job_id = int(job_display_string.split('(ID:')[-1].strip()[:-1])
    except (ValueError, IndexError):
        logger.error(f"Could not parse job_id from string: {job_display_string}")
        return gr.CheckboxGroup(choices=[]), pd.DataFrame(), gr.Button(interactive=False)

    df = get_ranked_candidates_for_job(job_id)
    
    if not df.empty:
        # Create choices for the CheckboxGroup. Format: "Name <email@address.com>"
        # This format is easy to parse later to get the unique email.
        checkbox_choices = [f"{row['full_name']} <{row['email']}>" for index, row in df.iterrows()]

        # Prepare the DataFrame for display (no changes here)
        df_display = df[['full_name', 'email', 'match_score', 'match_summary']].copy()
        df_display.rename(columns={
            'full_name': 'Candidate Name', 'email': 'Email',
            'match_score': 'Score', 'match_summary': 'AI Summary'
        }, inplace=True)
        
        # Return the populated components
        return gr.CheckboxGroup(choices=checkbox_choices, label="Select Candidates to Interview"), df_display, gr.Button(interactive=True)
    else:
        # Return empty components if no candidates are found
        return gr.CheckboxGroup(choices=[]), pd.DataFrame(), gr.Button(interactive=False)

# *** MAJOR CHANGE HERE: This function now takes a list of strings from the CheckboxGroup ***
def trigger_email_process(selected_candidates_list: list, job_display_string: str):
    """Triggers the email generation workflow based on user's checkbox selections."""
    if not selected_candidates_list:
        raise gr.Error("No candidates were selected. Please check the boxes for candidates you wish to interview.")

    if not job_display_string:
        raise gr.Error("No job selected. Please ensure a job is active in the dropdown.")

    try:
        job_id = int(job_display_string.split('(ID:')[-1].strip()[:-1])
        job_title = job_display_string.split(' (ID:')[0]
    except (ValueError, IndexError):
        raise gr.Error("Could not identify the selected job. Please refresh and try again.")
    
    # Extract emails from the checkbox list. e.g., "John Doe <j.doe@email.com>" -> "j.doe@email.com"
    selected_emails = set()
    for item in selected_candidates_list:
        match = re.search(r'<(.*?)>', item)
        if match:
            selected_emails.add(match.group(1))

    all_applicants_df = get_ranked_candidates_for_job(job_id)
    if all_applicants_df.empty:
        raise gr.Error("Could not retrieve applicant data from the database.")

    positive_candidates = all_applicants_df[all_applicants_df['email'].isin(selected_emails)].to_dict('records')
    negative_candidates = all_applicants_df[~all_applicants_df['email'].isin(selected_emails)].to_dict('records')

    workflow_input = {
        "job_title": job_title,
        "positive_candidates": positive_candidates,
        "negative_candidates": negative_candidates
    }
    
    result = email_app.invoke(workflow_input)
    
    processed_emails = result.get("processed_emails", [])
    
    summary = f"### Email Generation Complete\n\n"
    summary += f"**Total Emails Generated:** {len(processed_emails)}\n"
    summary += f"**Accepted:** {len(positive_candidates)} | **Rejected:** {len(negative_candidates)}\n\n"
    summary += "--- \n\n"
    summary += "\n".join(processed_emails)
    
    return summary

# --- Define the Gradio Interface with Tabs (UPDATED) ---

with gr.Blocks(theme=gr.themes.Glass(), title="CV-Scout") as demo:
    gr.Markdown("# CV-Scout: Multi-Agent Resume Intelligence System")

    with gr.Tabs():
        # --- Tab 1: Process Resumes (No changes) ---
        with gr.TabItem("Process New Resumes"):
            # ... (This whole tab section is unchanged)
            gr.Markdown("Upload multiple resume PDFs and provide a job description to process and rank candidates.")
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(label="Upload Resume PDFs", file_count="multiple",file_types=[".pdf"])
                    jd_input = gr.Textbox(label="Job Description", lines=10, placeholder="Paste the job description here...")
                    process_button = gr.Button("Process and Rank Resumes", variant="primary")
                with gr.Column(scale=2):
                    gr.Markdown("### Processing Summary")
                    status_output = gr.Textbox(label="Status", interactive=False)
                    summary_output = gr.Markdown()
            process_button.click(fn=process_resumes_and_job, inputs=[file_input, jd_input], outputs=[status_output, summary_output])

        # --- Tab 2: Candidate Dashboard (UPDATED UI COMPONENTS) ---
        with gr.TabItem("Candidate Dashboard") as dashboard_tab:
            gr.Markdown("View ranked candidates for a specific job and select them for the next stage.")
            with gr.Row():
                job_dropdown = gr.Dropdown(label="Select a Job Description", interactive=False)
                refresh_button = gr.Button("Refresh Jobs")
            
            # *** NEW COMPONENT for explicit selection ***
            candidate_selector = gr.CheckboxGroup(label="Select Candidates to Interview")
            
            # *** UPDATED COMPONENT: Now for viewing only (interactive=False) and using modern name gr.DataFrame ***
            candidate_dataframe = gr.DataFrame(
                headers=["Candidate Name", "Email", "Score", "AI Summary"],
                datatype=["str", "str", "number", "str"],
                interactive=False, 
                label="Ranked Candidate Details"
            )
            
            proceed_button = gr.Button("Generate Emails for Selected Candidates", variant="primary", interactive=False)
            
            action_summary_output = gr.Markdown()

            # --- Event Listeners for Dashboard (UPDATED) ---
            dashboard_tab.select(fn=update_job_dropdown, inputs=None, outputs=job_dropdown)
            refresh_button.click(fn=update_job_dropdown, inputs=None, outputs=job_dropdown)
            
            # *** UPDATED: load_candidate_dashboard now populates three components ***
            job_dropdown.change(
                fn=load_candidate_dashboard, 
                inputs=job_dropdown, 
                outputs=[candidate_selector, candidate_dataframe, proceed_button]
            )

            # *** UPDATED: proceed_button now takes input from the new candidate_selector ***
            proceed_button.click(
                fn=trigger_email_process,
                inputs=[candidate_selector, job_dropdown], 
                outputs=action_summary_output
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)