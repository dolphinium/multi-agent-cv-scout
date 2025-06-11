import os
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from src.schemas import GeneratedEmail

# Configure logging and load environment variables
load_dotenv()
logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize a specific LLM for this task
email_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)
structured_email_llm = email_llm.with_structured_output(GeneratedEmail)

def get_positive_prompt():
    """Returns the prompt template for a positive/acceptance email."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a friendly and professional tech recruiter. Your task is to write an enthusiastic email inviting the candidate for a technical interview. Be warm, personalize it with their name, and clearly state the next steps."),
            ("human", 
             "Please draft an interview invitation for the role of '{job_title}'.\n"
             "The candidate's name is {candidate_name}.\n\n"
             "Key points to include:\n"
             "- Express excitement about their application and strong profile.\n"
             "- Invite them to a technical interview.\n"
             "- Ask them for their availability in the coming week.\n"
             "- Keep the tone professional yet encouraging."
            )
        ]
    )

def get_negative_prompt():
    """Returns the prompt template for a negative/rejection email."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a polite, empathetic, and professional tech recruiter. Your task is to write a courteous rejection email. The goal is to maintain a positive company image and leave the candidate with a good impression despite the negative news."),
            ("human", 
             "Please draft a rejection email for the role of '{job_title}'.\n"
             "The candidate's name is {candidate_name}.\n\n"
             "Key points to include:\n"
             "- Thank the candidate for their interest and for taking the time to apply.\n"
             "- State that after careful consideration, you have decided not to move forward with their application at this time.\n"
             "- Mention that the decision was difficult due to a high volume of qualified applicants.\n"
             "- Wish them the best of luck in their job search.\n"
             "- Do NOT give specific feedback on their resume."
            )
        ]
    )

def email_content_generator_agent(candidate_info: dict) -> dict:
    """
    Generates the email content (subject and body) for a single candidate.
    
    Args:
        candidate_info (dict): A dictionary containing 'candidate_name', 'job_title', 
                               and 'disposition' ('positive' or 'negative').
    
    Returns:
        dict: A dictionary with the generated 'subject' and 'body'.
    """
    disposition = candidate_info.get("disposition")
    
    if disposition == "positive":
        prompt = get_positive_prompt()
        logger.info(f"---AGENT: Generating POSITIVE email content for {candidate_info['candidate_name']}---")
    elif disposition == "negative":
        prompt = get_negative_prompt()
        logger.info(f"---AGENT: Generating NEGATIVE email content for {candidate_info['candidate_name']}---")
    else:
        # Should not happen in normal flow
        return {"subject": "Error", "body": "Invalid disposition."}

    chain = prompt | structured_email_llm
    
    try:
        response = chain.invoke({
            "job_title": candidate_info["job_title"],
            "candidate_name": candidate_info["candidate_name"]
        })
        return {"subject": response.subject, "body": response.body}
    except Exception as e:
        logger.error(f"Error generating email content: {e}")
        return {"subject": "Generation Error", "body": f"Could not generate email content. Error: {e}"}

def mock_dispatch_agent(email_details: dict) -> str:
    """
    Mocks the sending of an email by logging it to the console.
    This is a safe way to demonstrate functionality without handling real credentials.
    """
    recipient = email_details['email_address']
    subject = email_details['subject']
    body = email_details['body']
    
    dispatch_log = (
        f"\n--- MOCK EMAIL DISPATCH ---\n"
        f"TO: {recipient}\n"
        f"SUBJECT: {subject}\n"
        f"BODY:\n{body}\n"
        f"---------------------------\n"
    )
    
    logger.info(dispatch_log)
    
    # Return a status message for the UI
    return f"✅ Mock email successfully generated for {recipient}."