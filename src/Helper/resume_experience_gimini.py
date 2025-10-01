import sys
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from contextlib import redirect_stderr
import io

# ---------------------------
# Suppress Python-level logs
# ---------------------------
os.environ['ABSL_LOG_LEVEL'] = '3'
logging.getLogger("google").setLevel(logging.CRITICAL)
logging.getLogger("grpc").setLevel(logging.CRITICAL)

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------------------
# Function to get total work experience
# ---------------------------
def generate_resume_experience_gemini(resume_text):
    prompt = f"""
I will provide a resume text. Identify only professional job periods (ignore education, internships, or other dates) and calculate the total work experience in years, including months as decimals (e.g., 2.5 years). Merge overlapping or consecutive job periods. 

Output only the number in this format:

X.X

Resume text:
"{resume_text}"
"""
    model = genai.GenerativeModel("gemini-2.5-flash")  # or gemini-pro
    
    response = model.generate_content(prompt)
    
    # Extract the numeric part from response
    text = response.text.strip()
    
    # Only keep the number (ignoring any warnings)
    import re
    match = re.search(r"(\d+(\.\d+)?)", text)
    if match:
        total_years = float(match.group(1))
    else:
        total_years = 0.0  # fallback if nothing found

    return total_years




