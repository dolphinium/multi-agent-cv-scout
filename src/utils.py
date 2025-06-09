from langchain_community.document_loaders import PyMuPDFLoader

def parse_pdf_to_text(file_path: str) -> str:
    """
    Parses a PDF file and returns its text content.
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
        print(f"Error parsing PDF: {e}")
        return ""