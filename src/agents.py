import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

import logging

from src.schemas import Resume
from src.utils import parse_pdf_to_text
from src.schemas import Resume, RelevancyAnalysis, PDFParsingError, ExtractionError, StandardizationError, RelevancyAnalysisError


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logger = logging.getLogger(__name__)

# Initialize the LLM with structured output capabilities
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", google_api_key=GEMINI_API_KEY)
structured_llm = llm.with_structured_output(Resume)

# 1. Ingestion Agent
def ingestion_agent(state):
    """
    Ingestion Agent: Parses the PDF file path from the state and loads its content.

    Args:
        state (AgentState): The current state of the agent workflow, expected to contain 'file_path'.

    Returns:
        dict: A dictionary containing the raw text extracted from the PDF under the key 'raw_text'.

    Raises:
        ValueError: If 'file_path' is not provided in the state.
        PDFParsingError: If an error occurs during the PDF parsing process.
    """
    logger.info("---AGENT: INGESTING AND PARSING PDF---")
    file_path = state.get("file_path")
    if not file_path:
        logger.error("File path must be provided in the state.")
        raise ValueError("File path must be provided in the state.")
    
    try:
        raw_text = parse_pdf_to_text(file_path)
        logger.info("---AGENT: PDF PARSED SUCCESSFULLY---")
        return {"raw_text": raw_text}
    except Exception as e:
        logger.error(f"---AGENT: ERROR during PDF parsing: {e}---")
        raise PDFParsingError(f"Error parsing PDF: {e}") from e

# 2. Core Extraction Agent
def extraction_agent(state):
    """
    Core Extraction Agent: Extracts structured information from the raw text using the LLM.

    Args:
        state (AgentState): The current state of the agent workflow, expected to contain 'raw_text'.

    Returns:
        dict: A dictionary containing the extracted structured data as a Pydantic model under the key 'extracted_json'.
              Returns {'extracted_json': None} if 'raw_text' is not provided.

    Raises:
        ExtractionError: If an error occurs during the LLM-based extraction process.
    """
    logger.info("---AGENT: EXTRACTING INFORMATION---")
    raw_text = state.get("raw_text")
    if not raw_text:
        logger.info("---AGENT: No raw text provided for extraction.---")
        return {"extracted_json": None}

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert resume parser. Your task is to extract information from the provided resume text and structure it according to the 'Resume' schema."),
            ("human", "{resume_text}"),
        ]
    )
    
    chain = prompt | structured_llm
    try:
        extracted_data = chain.invoke({"resume_text": raw_text})
        logger.info("---AGENT: INFORMATION EXTRACTED---")
        return {"extracted_json": extracted_data}
    except Exception as e:
        logger.error(f"---AGENT: ERROR during extraction: {e}---")
        raise ExtractionError(f"Error extracting information: {e}") from e
    
# 3. Standardization Agent (could be expanded later)
def standardization_agent(state):
    """
    Standardization Agent: Standardizes the extracted JSON data.

    Currently, this agent primarily converts the Pydantic model to a dictionary.
    Future enhancements could include date formatting, skill normalization, etc.

    Args:
        state (AgentState): The current state of the agent workflow, expected to contain 'extracted_json'.

    Returns:
        dict: A dictionary containing the standardized data under the key 'final_report'.
              Returns {'final_report': None} if 'extracted_json' is not provided.

    Raises:
        StandardizationError: If an error occurs during the standardization process.
    """
    logger.info("---AGENT: STANDARDIZING DATA---")
    extracted_json = state.get("extracted_json")
    if not extracted_json:
        logger.info("---AGENT: No extracted JSON provided for standardization.---")
        return {"final_report": None}

    # Here you could add more complex logic, e.g., date formatting
    try:
        final_report = extracted_json.dict()
        logger.info("---AGENT: DATA STANDARDIZED---")
        return {"final_report": final_report}
    except Exception as e:
        logger.error(f"---AGENT: ERROR during standardization: {e}---")
        raise StandardizationError(f"Error standardizing data: {e}") from e

# 4. Job Match & Relevancy Agent
def relevancy_analysis_agent(state):
    """
    Job Match & Relevancy Agent: Analyzes the resume against the job description.

    Compares the structured resume data ('final_report') with the 'job_description'
    to generate a compatibility score and a summary using an LLM.

    Args:
        state (AgentState): The current state of the agent workflow, expected to contain
                            'job_description' and 'final_report'.

    Returns:
        dict: A dictionary containing the match score ('match_score') and summary ('match_summary').
              Returns default values if 'job_description' or 'final_report' are missing.

    Raises:
        RelevancyAnalysisError: If an error occurs during the LLM-based relevancy analysis.
    """
    logger.info("---AGENT: ANALYZING RELEVANCY---")
    job_description = state.get("job_description")
    final_report = state.get("final_report")

    if not job_description or not final_report:
        logger.info("---AGENT: SKIPPING RELEVANCY ANALYSIS (missing job description or report)---")
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
        logger.info("---AGENT: RELEVANCY ANALYSIS COMPLETE---")
        return {
            "match_score": analysis_result.score,
            "match_summary": analysis_result.summary
        }
    except Exception as e:
        logger.error(f"---AGENT: ERROR during relevancy analysis: {e}---")
        raise RelevancyAnalysisError(f"Error during relevancy analysis: {e}") from e