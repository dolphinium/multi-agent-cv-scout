from pydantic import BaseModel, Field
from typing import List, Optional


class Education(BaseModel):
    instution: str = Field(..., description="Name of the university or instution")
    degree: str = Field(..., description= "The degree obtained")
    gpa: Optional[str] = Field(None, description="Grade Point Average")
    years: str = Field(..., description="Start and end years of education")
    location: Optional[str] = Field(None, description="Location of the institution")
    
class Experience(BaseModel):
    company: str = Field(..., description="Name of the company")
    title: str = Field(..., description="Job title or role")
    years: str = Field(..., description="Start and end dates of employment")
    location: Optional[str] = Field(None, description="Location of the company")
    description: str = Field(..., description="Description of responsibilities and achievements")

class Resume(BaseModel):
    full_name: str = Field(..., description="Full name of the candidate")
    mail: str = Field(..., description="Email address of the candidate")
    phone_number: Optional[str] = Field(None, description="Phone number")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    education: List[Education] = Field(..., description="List of educational qualifications")
    experience: List[Experience] = Field(..., description="List of professional experiences")
    technical_skills: List[str] = Field(..., description="List of technical skills")
    languages: List[str] = Field(..., description="List of languages spoken by the candidate")