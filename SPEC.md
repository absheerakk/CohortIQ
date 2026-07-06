# Capstone Spec — Cohort IQ: Intelligent Course Companion

## What it does
A web application where AI Engineering interns can ask natural-language questions about their course material and receive answers completely grounded in the actual lesson content. To ensure trustworthiness, every answer is accompanied by exact citations pointing to the specific day's material the answer was drawn from, eliminating hallucinations.

## Who it's for
Interns in the Techgebra AI Engineering Internship cohort who want a faster, more reliable way to review concepts and find specific technical information without having to manually search through 14+ separate markdown files.

## How it works
1. All daily lesson markdown files are loaded, parsed, and chunked.
2. The chunks are embedded into vectors and stored in a persistent Chroma database, tagged with metadata indicating which specific day and file they originated from.
3. The user types a query into a clean Streamlit interface.
4. The question is embedded and matched against the closest, most relevant chunks in the database.
5. Gemini generates an answer using a strict system prompt that forces it to only use the retrieved context.
6. The final answer is displayed alongside clickable citations indicating which day(s) provided the information.

## Out of scope
- No support for file formats other than markdown (e.g., no PDF or Word document parsing).
- No user accounts, authentication, or saved conversation history across sessions.
- No editing or modifying of the lesson content through the application.
- The app is not optimized or guaranteed for documents outside the specific scope of the AI Engineering course material.
- **PII Checking on Document Upload:** Not applicable. The application retrieves coursework data directly from pre-defined local directories and does not accept user document uploads. PII guardrails are instead enforced directly on search input queries.