
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
print("Loaded Gemini API Key:", os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_resume_feedback_gemini(resume_text, jd_text):
    prompt = f"""
You are an expert resume reviewer and ATS optimization assistant.

Your task is to analyze the following resume against the provided job description and generate a detailed feedback report.

## Job Description:
{jd_text}

## Resume:
{resume_text}

## Instructions:
1. Evaluate the resume for ATS compatibility.
2. Identify missing keywords from the job description.
3. Check for formatting issues.
4. Provide a score out of 100.
5. Suggest improvements.

## Output Format:
### ATS Compatibility Report
- ATS Score:
- Keyword Match Score:
- Missing Keywords:
- Formatting Issues:

### Suggestions for Improvement
- 

### Summary
"""

    model = genai.GenerativeModel("gemini-1.5-flash")  # or gemini-pro
    response = model.generate_content(prompt)
    return response.text
