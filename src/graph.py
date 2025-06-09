from typing import TypedDict, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from src.agents import ingestion_agent, extraction_agent, standardization_agent, relevancy_analysis_agent

class AgentState(TypedDict):
    """Defines the state for our agent workflow."""
    file_path: str
    job_description: Optional[str] 
    raw_text: str
    extracted_json: Dict[str, Any]
    final_report: Dict[str, Any]
    match_score: Optional[int]    
    match_summary: Optional[str]
    

def should_run_analysis(state):
    """
    A conditional edge function. If a job description is present,
    it routes to the relevancy_analysis_agent. Otherwise, it ends the process.
    """
    print("---ROUTER: DECIDING NEXT STEP---")
    if state.get("job_description"):
        print("---ROUTER: Job description found. Proceeding to analysis.---")
        return "run_analysis"
    else:
        print("---ROUTER: No job description. Skipping analysis.---")
        return "skip_analysis"

def create_workflow():
    """
    Creates the LangGraph workflow for processing resumes.
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