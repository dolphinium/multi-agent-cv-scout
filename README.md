# CV-Scout: A Multi-Agent Resume Intelligence System

An AI-powered system designed to transform unstructured resume PDFs into actionable, structured data and perform intelligent job-to-candidate matching. This project demonstrates an end-to-end multi-agent workflow using Langchain(LangGraph) and the Google Gemini API.


![alt text](./docs/front-page.png " CV-Scout Front Page")

## 🚀 Project Vision

In today's competitive job market, recruiters and hiring managers are inundated with resumes. The initial screening process is manual, time-consuming, and prone to inconsistency. CV-Scout addresses this challenge by leveraging a sophisticated multi-agent AI system to automate the analysis of candidate resumes.

The system ingests a candidate's PDF resume, converts the unstructured data into a clean, structured format, and evaluates the candidate's profile against a provided job description, offering a quantitative score and a qualitative analysis. This project is a practical implementation of the principles of complex workflow automation and AI-driven data intelligence.

## ✨ Core Features

*   **PDF Resume Parsing:** Upload any standard resume in PDF format.
*   **Structured Data Extraction:** Automatically identifies and extracts key information such as contact details, work experience, education, and skills.
*   **Job-to-Candidate Matching:** Scores the resume against a job description to quantify candidate-role fit.
*   **AI-Powered Analysis:** Provides a brief, human-readable summary explaining the compatibility score, highlighting strengths and potential gaps.
*   **Interactive UI:** A simple and intuitive user interface built with Gradio for easy demonstration and use.
*   **Dockerized Deployment:** The entire application is containerized with Docker for easy, reliable, and portable deployment.

## 🛠️ Technical Architecture

CV-Scout is architected as a robust multi-agent system where a central **Orchestrator Agent** manages a team of specialized agents. This design ensures modularity, scalability, and clarity of purpose for each component. The entire workflow is managed using **Langchain's LangGraph** framework, which is ideal for creating cyclical and stateful agentic applications.

```mermaid
graph TD
    subgraph User Interface
        A[Gradio UI]
    end

    subgraph Agentic Core
        B(Orchestrator Agent)

        subgraph Specialist Agent Team
            C[Ingestion & Parsing Agent]
            D[Core Extraction Agent]
            E[Standardization Agent]
            F[Job Match & Relevancy Agent]
            G[Synthesizer Agent]
        end
    end
    
    A -- PDF & Job Description --> B;
    B -- Raw PDF --> C;
    C -- Cleaned Text --> B;
    B -- Cleaned Text --> D;
    D -- Raw JSON --> B;
    B -- Raw JSON --> E;
    E -- Standardized JSON --> B;
    B -- Standardized JSON & Job Description --> F;
    F -- Scored Analysis --> B;
    B -- Final Data --> G;
    G -- Final Report --> B;
    B -- Structured Output & Analysis --> A;
```
### The Agent Team:
*   **Orchestrator Agent (The Manager):** Built with LangGraph, it manages the state and sequence of the entire operation, delegating tasks to the appropriate specialist agent.
*   **Ingestion & Parsing Agent:** Uses `PyMuPDF` to extract raw text from the uploaded PDF and performs initial text cleaning.
*   **Core Extraction Agent:** Leverages the **Gemini API** with advanced prompt engineering to perform Named Entity Recognition (NER) and extract key details into a raw JSON format.
*   **Standardization Agent:** A crucial quality control step. This agent cleans the extracted data, standardizing formats (e.g., dates) and ensuring consistency.
*   **Job Match & Relevancy Agent (RAG):** Implements a **Retrieval-Augmented Generation (RAG)** pattern. It compares the structured resume data against the job description to generate a compatibility score and a qualitative summary.
*   **Synthesizer Agent:** Compiles all the structured data and the relevancy analysis into a final, clean JSON object and a human-readable report for the UI.

## ⚙️ Tech Stack

*   **Programming Language:** Python
*   **Core AI Framework:** Langchain (utilizing LangGraph for agent orchestration)
*   **Deployment:** Docker
*   **LLM:** Google Gemini API
*   **PDF Parsing:** PyMuPDF (`fitz`)
*   **UI Framework:** Gradio

## 🗺️ Project Stages

The development of CV-Scout followed a structured, iterative process.

Stage 1: Core Functionality & MVP [✅]      
Stage 2: Implementing the Multi-Agent Architecture [✅]     
Stage 3: Advanced Feature Integration & Analysis [✅]       
Stage 4: Dockerization [✅]     

### Stage 1: Core Functionality & MVP

The initial goal was to validate the core concept: extracting structured data from a PDF. This stage focused on creating a Minimum Viable Product (MVP) with a single, monolithic Langchain chain.
*   **Objective:** Successfully parse a PDF and extract the candidate's name and email.
*   **Outcome:** Proved the viability of the core technology stack and established a baseline for more complex development.

### Stage 2: Implementing the Multi-Agent Architecture

Moving from a single chain to a sophisticated multi-agent system was the key architectural evolution. This stage focused on building the robust, orchestrated workflow described in the architecture diagram.
*   **Objective:** Decompose the single chain into specialized agents managed by an orchestrator using LangGraph.
*   **Outcome:** A highly modular and scalable system that mirrors real-world team collaboration, improving robustness and maintainability.

### Stage 3: Advanced Feature Integration & Analysis

With the agentic foundation in place, this final stage focused on adding high-value business intelligence, transforming the tool from a simple parser into a decision-support system.
*   **Objective:** Add the ability to score a resume against a job description.
*   **Outcome:** Significantly enhanced the project's utility by providing immediate, actionable insights for the user.

### Stage 4: Dockerization

This stage focused on encapsulating the application into a portable and reproducible environment using Docker.
*   **Objective:** Create a Docker image that contains the application, all its dependencies, and the necessary runtime configuration.
*   **Implementation:** Wrote a multi-stage `Dockerfile` for efficient image building and a `.dockerignore` file to keep the image lean.
*   **Outcome:** The application is now fully portable and can be run with two simple commands, eliminating "it works on my machine" issues and preparing it for cloud deployment.

## 🚀 Setup and Installation

You can run this project in two ways: with Docker (recommended for ease of use) or by setting up a local Python environment.

### Method 1: Running with Docker (Recommended)

**Prerequisites:** Docker must be installed and running on your system.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dolphinium/multi-agent-cv-scout.git
    cd multi-agent-cv-scout
    ```

2.  **Set up your API Key:**
    Create a file named `.env` in the root of the project and add your API key:
    ```
    GEMINI_API_KEY="your-google-api-key"
    ```

3.  **Build the Docker image:**
    ```bash
    docker build -t cv-scout .
    ```

4.  **Run the Docker container:**
    ```bash
    docker run -p 7860:7860 --env-file .env cv-scout
    ```

5.  Open your browser and navigate to `http://localhost:7860`.

### Method 2: Running Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dolphinium/multi-agent-cv-scout.git
    cd multi-agent-cv-scout
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows: venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**
    Create a file named `.env` in the root of the project and add your API key:
    ```
    GEMINI_API_KEY="your-google-api-key"
    ```

5.  **Run the Gradio application:**
    ```bash
    gradio app.py
    ```

6.  Open your browser and navigate to the local URL provided by Gradio (e.g., `http://127.0.0.1:7860`).

## 🔮 Future Improvements

*   **Batch Processing:** Allow users to upload multiple resumes for simultaneous analysis.
*   **Database Integration:** Store the structured outputs in a database (e.g., SQLite, PostgreSQL) for long-term storage and trend analysis.
*   **Enhanced UI Features:** Add features like resume comparison, skill gap analysis, and candidate ranking.
*   **Fine-Tuning:** Fine-tune a smaller, open-source model on a curated dataset of resumes to improve accuracy and reduce API costs.
*   **Expanded Skill Ontology:** Develop a more sophisticated system for classifying skills into predefined categories to enhance search and filtering capabilities.