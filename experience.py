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

