from typing import TypedDict, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from src.agents import ingestion_agent, extraction_agent, standardization_agent, relevancy_analysis_agent

class AgentState(TypedDict):
    """
    AgentState: Defines the state for the LangGraph agent workflow.

    This TypedDict holds the intermediate and final results as the workflow progresses
    through different agents.

    Attributes:
        file_path (str): The path to the uploaded resume PDF file.
        job_description (Optional[str]): The job description provided by the user, if any.
        raw_text (str): The raw text extracted from the PDF.
        extracted_json (Dict[str, Any]): The initial structured data extracted by the LLM.
        final_report (Dict[str, Any]): The standardized and final structured data.
        match_score (Optional[int]): The compatibility score of the resume against the job description (0-100).
        match_summary (Optional[str]): A summary explaining the match score.
    """
    file_path: str
    job_description: Optional[str]
    raw_text: str
    extracted_json: Dict[str, Any]
    final_report: Dict[str, Any]
    match_score: Optional[int]
    match_summary: Optional[str]
    

def should_run_analysis(state):
    """
    Conditional Edge Function: Determines whether to run the relevancy analysis agent.

    This function is used by LangGraph to decide the next step in the workflow
    based on the presence of a job description in the current state.

    Args:
        state (AgentState): The current state of the agent workflow.

    Returns:
        str: "run_analysis" if a job description is present, "skip_analysis" otherwise.
    """
    # Using logging instead of print for better practice
    # logger.info("---ROUTER: DECIDING NEXT STEP---") # Need to add logger to graph.py
    if state.get("job_description"):
        # logger.info("---ROUTER: Job description found. Proceeding to analysis.---")
        return "run_analysis"
    else:
        # logger.info("---ROUTER: No job description. Skipping analysis.---")
        return "skip_analysis"

def create_workflow():
    """
    Creates the LangGraph workflow for processing resumes.

    Defines the nodes (agents) and edges (transitions) of the state graph
    that orchestrates the resume processing pipeline.

    Returns:
        CompiledGraph: The compiled LangGraph application ready for invocation.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes (our agents)
    workflow.add_node("ingestion_agent", ingestion_agent)
    workflow.add_node("extraction_agent", extraction_agent)
    workflow.add_node("standardization_agent", standardization_agent)
    workflow.add_node("relevancy_analysis_agent", relevancy_analysis_agent) # Add the new agent node

    # 3. Redefine the edges with the new conditional logic
    workflow.set_entry_point("ingestion_agent")
    workflow.add_edge("ingestion_agent", "extraction_agent")
    workflow.add_edge("extraction_agent", "standardization_agent")

    # Add the conditional branching
    workflow.add_conditional_edges(
        "standardization_agent",
        should_run_analysis,
        {
            "run_analysis": "relevancy_analysis_agent",
            "skip_analysis": END
        }
    )
    
    # The analysis agent now leads to the end
    workflow.add_edge("relevancy_analysis_agent", END)

    # Compile the graph
    app = workflow.compile()
    return app

# To test the graph directly
if __name__ == '__main__':
    graph = create_workflow()
    
    # Example invocation
    inputs = {"file_path": "data/cv.pdf"}
    result = graph.invoke(inputs)
    
    print("\n---FINAL REPORT---")
    import json
    print(json.dumps(result.get("final_report"), indent=2))