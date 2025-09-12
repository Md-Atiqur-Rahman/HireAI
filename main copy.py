from pyresparser import ResumeParser
from experience import calculate_total_experience
from src.parser import extract_text_from_pdf
from src.extractor import extract_keywords
from src.scorer import calculate_similarity
import re
from dateutil import parser
from datetime import datetime

from pyresparser import ResumeParser
from dateutil import parser
from datetime import datetime
import re

def extract_with_pyresparser(file_path):
    return ResumeParser(file_path).get_extracted_data()

def calculate_total_experience(text):
    pattern = r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\\s/-]\\d{4}|\\d{2}/\\d{4})\\s*(?:–|-|to)\\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\\s/-]\\d{4}|\\d{2}/\\d{4})"
    date_ranges = re.findall(pattern, text)
    total_months = 0
    for range_text in date_ranges:
        parts = re.split(r"–|-|to", range_text)
        if len(parts) == 2:
            start, end = parts[0].strip(), parts[1].strip()
            try:
                start_date = parser.parse(start)
                end_date = datetime.now() if end.lower() == "present" else parser.parse(end)
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                total_months += max(months, 0)
            except:
                continue
    return round(total_months / 12, 2)


# Load resume
pdf_path = "E:/Thesis/resume-analyzer/resumes/Craig Kovatch Kovatch.pdf"
pdf_path = "E:/Thesis/resume-analyzer/resumes/Kumaresan-resume.pdf"
pdf_path = "E:/Thesis/resume-analyzer/resumes/John Doe.pdf"
resume_path = "E:/Thesis/resume-analyzer/resumes/Craig Kovatch Kovatch.pdf"
# Step 1: Extract structured data using pyresparser
data = extract_with_pyresparser(resume_path)

# Step 2: Extract raw text for custom experience calculation
resume_text = extract_text_from_pdf(resume_path)  # This should return plain text

# Step 3: Calculate experience using regex-based extractor
exp = calculate_total_experience(resume_text)

# Step 4: Use pyresparser experience if available, else fallback to custom
final_experience = data.get('experience') if data.get('experience') else exp

print(f"Total Experience: {final_experience} years")
