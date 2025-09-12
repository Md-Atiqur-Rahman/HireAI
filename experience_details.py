import re
from dateutil import parser
from datetime import datetime
import pdfplumber

def extract_experience_details(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        resume_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    resume_text = resume_text.replace("–", "-").replace("—", "-").replace(" to ", "-")

    pattern = r"(.+?)\s*\[(\d{2}/\d{4})\]\s*-\s*(?:\[(\d{2}/\d{4})\]|Present)"

    entries = re.findall(pattern, resume_text)
    experience_details = []
    individual_years = []
    for entry in entries:
        title = entry[0].strip()
        start = entry[1]
        end = entry[2] if entry[2] else "Present"
        try:
            start_date = parser.parse(start)
            end_date = datetime.now() if end.lower() == "present" else parser.parse(end)
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            years_fraction = round(months / 12, 2)
            individual_years.append(years_fraction)
            duration = f"{months} months ({years_fraction} years)"
            experience_details.append(f"{title}: [{start}] - [{end}] = {duration}")
        except Exception:
            continue


    total_experience_years = round(sum(individual_years), 2)
    return experience_details, total_experience_years

