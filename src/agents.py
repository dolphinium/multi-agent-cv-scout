import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from src.schemas import Resume
from src.utils import parse_pdf_to_text
from src.schemas import Resume, RelevancyAnalysis


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the LLM with structured output capabilities
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", google_api_key=GEMINI_API_KEY)
structured_llm = llm.with_structured_output(Resume)

# 1. Ingestion Agent
def ingestion_agent(state):
    """
    Parses the PDF file path from the state and loads its content.
    """
    print("---AGENT: INGESTING AND PARSING PDF---")
    file_path = state.get("file_path")
    if not file_path:
        raise ValueError("File path must be provided in the state.")
    
    raw_text = parse_pdf_to_text(file_path)
    print("---AGENT: PDF PARSED SUCCESSFULLY---")
    return {"raw_text": raw_text}

# 2. Core Extraction Agent
def extraction_agent(state):
    """
    Extracts structured information from the raw text using the LLM.
    """
    print("---AGENT: EXTRACTING INFORMATION---")
    raw_text = state.get("raw_text")
    if not raw_text:
        return {"extracted_json": None}

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert resume parser. Your task is to extract information from the provided resume text and structure it according to the 'Resume' schema."),
            ("human", "{resume_text}"),
        ]
    )
    
    chain = prompt | structured_llm
    extracted_data = chain.invoke({"resume_text": raw_text})
    print("---AGENT: INFORMATION EXTRACTED---")
    return {"extracted_json": extracted_data}
    
# 3. Standardization Agent (could be expanded later)
def standardization_agent(state):
    """
    Standardizes the extracted JSON data. 
    For now, it just ensures it's in a dict format.
    """
    print("---AGENT: STANDARDIZING DATA---")
    extracted_json = state.get("extracted_json")
    if not extracted_json:
        return {"final_report": None}

    # Here you could add more complex logic, e.g., date formatting
    final_report = extracted_json.dict()
    print("---AGENT: DATA STANDARDIZED---")
    return {"final_report": final_report}

# 4. Job Match & Relevancy Agent
def relevancy_analysis_agent(state):
    """
    Analyzes the resume against the job description to provide a match score and summary.
    """
    print("---AGENT: ANALYZING RELEVANCY---")
    job_description = state.get("job_description")
    final_report = state.get("final_report")

    if not job_description or not final_report:
        print("---AGENT: SKIPPING RELEVANCY ANALYSIS (missing job description or report)---")
        return {"match_score": 0, "match_summary": "Not applicable (no job description provided)."}

    # We need a new structured LLM call specifically for this agent's output schema
    relevancy_llm = llm.with_structured_output(RelevancyAnalysis)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
             "You are an expert tech recruiter and hiring manager. Your task is to analyze the candidate's resume, provided as a JSON object, and compare it against the job description. "
             "Evaluate the experience, skills, and education to determine the candidate's suitability for the role. "
             "Provide a compatibility score from 0 to 100 and a concise summary justifying your score."),
            ("human", 
             "Please analyze the following resume and job description.\n"
             "---CANDIDATE RESUME---\n"
             "{resume_json}\n\n"
             "---JOB DESCRIPTION---\n"
             "{job_description}"
            ),
        ]
    )

    chain = prompt | relevancy_llm
    
    try:
        analysis_result = chain.invoke({
            "resume_json": final_report,
            "job_description": job_description
        })
        print("---AGENT: RELEVANCY ANALYSIS COMPLETE---")
        return {
            "match_score": analysis_result.score,
            "match_summary": analysis_result.summary
        }
    except Exception as e:
        print(f"---AGENT: ERROR during relevancy analysis: {e}---")
        return {"match_score": 0, "match_summary": "An error occurred during analysis."}