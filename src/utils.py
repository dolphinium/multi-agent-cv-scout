import logging
from langchain_community.document_loaders import PyMuPDFLoader

logger = logging.getLogger(__name__)

def parse_pdf_to_text(file_path: str) -> str:
    """
    Parses a PDF file and returns its text content.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The concatenated text content from all pages of the PDF.
             Returns an empty string if an error occurs during parsing.

    Raises:
        ValueError: If no documents could be loaded from the PDF.
        Exception: Catches any other exceptions during parsing and logs them.
    """
    try:
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        
        if not documents:
            raise ValueError("Could not load any documents from the PDF.")
            
        # Concatenate content from all pages/documents
        full_text = "\n".join([doc.page_content for doc in documents])
        return full_text
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        # Re-raising the exception is handled in the calling agent (ingestion_agent)
        # For now, return empty string as original code did, but the agent will catch and raise PDFParsingError
        raise # Re-raise the exception to be caught by the ingestion_agent