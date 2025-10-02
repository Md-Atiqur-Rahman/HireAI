# ===============================
# Experience Extractor
# ===============================
import re
from dateutil import parser
from datetime import datetime


def extract_experience_entries(text):
    experience_entries = []
    total_months = 0

    patterns = [
        r"(?P<title>.*?)\n(?P<company>.*?)\n\[(?P<start>\d{2}/\d{4})\]\s*-\s*(\[(?P<end>\d{2}/\d{4})\]|(?P<present>Present))",
        r"(?P<title>.*?)\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*(\[(?P<end>\d{2}/\d{4})\]|(?P<present>Present))\s*(?P<company>[A-Za-z0-9 ,.&()]+)",
        r"(?P<title>.*?)\s*:\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*\[(?P<end>\d{2}/\d{4}|Present)\]",
        r"(?P<title>.*?)\s+at\s+(?P<company>.*?)\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*\[(?P<end>\d{2}/\d{4}|Present)\]",
        r"(?P<title>.*?)\n(?P<company>.*?)\n(?P<start>\d{2}/\d{4})\s*-\s*(?P<end>\d{2}/\d{4}|Present)",
        r"(?P<title>.+?),\s*(?P<company>.+?)\n(?P<start>[A-Za-z\.]+ \d{4})\s*-\s*(?P<end>[A-Za-z\.]+ \d{4}|Present)",

        r"(?P<title>.*?)\s*\|\s*(?P<company>.*?)\n(?P<start>[A-Za-z]+\s*\d{4})\s*[-–]\s*(?P<end>[A-Za-z]+\s*\d{4}|Present)",
        r"(?P<title>.*?)\s+(at|@)\s+(?P<company>.*?)\s*(?P<start>[A-Za-z]+\s*\d{4})\s*[-–]\s*(?P<end>[A-Za-z]+\s*\d{4}|Present)",
    ]

    matches = []
    for pat in patterns:
        matches += list(re.finditer(pat, text))

    for match in matches:
        title = match.group("title").strip()
        company = match.group("company").strip() if "company" in match.groupdict() and match.group("company") else ""
        start = match.group("start")
        end = match.group("end") if match.group("end") else match.group("present")

        try:
            start_date = parser.parse(start)
            end_date = datetime.now() if end.lower() == "present" else parser.parse(end)
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += months
            years_fraction = round(months / 12, 1)
            formatted = f"{title} - {company}: [{start}] - [{end}] = {months} months ({years_fraction} years)"
            experience_entries.append(formatted)
        except:
            continue

    total_years = round(total_months / 12, 1)
    # print("total_years----->",total_years)
    return experience_entries, total_years

def extract_years_from_text(text):
    patterns = [
        r"(\d+)\+?\s+years of experience",
        r"over (\d+)\s+years",
        r"more than (\d+)\s+years"
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0
