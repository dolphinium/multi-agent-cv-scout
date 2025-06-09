from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from src.agents import ingestion_agent, extraction_agent, standardization_agent

class AgentState(TypedDict):
    """Defines the state for our agent workflow."""
    file_path: str
    raw_text: str
    extracted_json: Dict[str, Any]
    final_report: Dict[str, Any]

def create_workflow():
    """
    Creates the LangGraph workflow for processing resumes.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes (our agents)
    workflow.add_node("ingestion_agent", ingestion_agent)
    workflow.add_node("extraction_agent", extraction_agent)
    workflow.add_node("standardization_agent", standardization_agent)

    # Define the edges (the flow of control)
    workflow.set_entry_point("ingestion_agent")
    workflow.add_edge("ingestion_agent", "extraction_agent")
    workflow.add_edge("extraction_agent", "standardization_agent")
    workflow.add_edge("standardization_agent", END) # End of the workflow

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