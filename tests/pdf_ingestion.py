from langchain_community.document_loaders.parsers import PyMuPDFParser
from langchain_core.documents.base import Blob
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from constants import SYSTEM_MESSAGE
import os

load_dotenv(override=True)

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001", google_api_key=GEMINI_API_KEY)

parser = PyMuPDFParser(mode="single")
path = "../data/cv.pdf"

def summarize(content):
    messages = [
        ("system", SYSTEM_MESSAGE),
        ("human", content),
    ]
    out = llm.invoke(messages).content

    return out

def parse_pdf(path: str):
    blob = Blob.from_path(path)

    docs = []
    docs_lazy = parser.lazy_parse(blob)
    for doc in docs_lazy:
        docs.append(doc)

    return docs[0].page_content

def extract(path):
    raw = parse_pdf(path)
    summary = summarize(raw)
    return summary


print(extract(path))


