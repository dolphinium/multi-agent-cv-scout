from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import logging

from src.email_agents import email_content_generator_agent, mock_dispatch_agent

logger = logging.getLogger(__name__)

class EmailAgentState(TypedDict):
    """Defines the state for the email generation workflow."""
    job_title: str
    positive_candidates: List[Dict[str, Any]]
    negative_candidates: List[Dict[str, Any]]
    processed_emails: List[str] # To store status messages from the dispatch agent

def email_orchestrator(state: EmailAgentState) -> Dict[str, List[str]]:
    """
    Orchestrates the entire email generation and dispatch process.
    Iterates through positive and negative candidate lists and processes them.
    """
    logger.info("---ORCHESTRATOR: Starting email generation process---")
    
    job_title = state['job_title']
    positive_candidates = state.get('positive_candidates', [])
    negative_candidates = state.get('negative_candidates', [])
    
    all_status_updates = []

    # Process positive candidates
    for candidate in positive_candidates:
        logger.info(f"Processing positive candidate: {candidate['full_name']}")
        content_input = {
            "candidate_name": candidate['full_name'],
            "job_title": job_title,
            "disposition": "positive"
        }
        generated_content = email_content_generator_agent(content_input)
        
        dispatch_input = {
            "email_address": candidate['email'],
            **generated_content
        }
        status = mock_dispatch_agent(dispatch_input)
        all_status_updates.append(status)

    # Process negative candidates
    for candidate in negative_candidates:
        logger.info(f"Processing negative candidate: {candidate['full_name']}")
        content_input = {
            "candidate_name": candidate['full_name'],
            "job_title": job_title,
            "disposition": "negative"
        }
        generated_content = email_content_generator_agent(content_input)
        
        dispatch_input = {
            "email_address": candidate['email'],
            **generated_content
        }
        status = mock_dispatch_agent(dispatch_input)
        all_status_updates.append(status)
        
    logger.info("---ORCHESTRATOR: Email process complete---")
    return {"processed_emails": all_status_updates}

def create_email_workflow():
    """Creates the LangGraph workflow for sending emails."""
    workflow = StateGraph(EmailAgentState)
    
    workflow.add_node("orchestrator", email_orchestrator)
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", END)
    
    return workflow.compile()