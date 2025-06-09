import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from src.schemas import Resume
from src.utils import parse_pdf_to_text

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