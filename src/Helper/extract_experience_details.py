import re
from dateutil import parser
from datetime import datetime
from extract_skills import extract_skills_from_resume

def extract_experience_entries(text):
    experience_entries = []
    total_months = 0

    # Pattern 1: Multiline format with brackets
    pattern_multiline = r"(?P<title>.*?)\n(?P<company>.*?)\n\[(?P<start>\d{2}/\d{4})\]\s*-\s*(\[(?P<end>\d{2}/\d{4})\]|(?P<present>Present))"

    # Pattern 2: Inline format with brackets
    pattern_inline = r"(?P<title>.*?)\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*(\[(?P<end>\d{2}/\d{4})\]|(?P<present>Present))\s*(?P<company>[A-Za-z0-9 ,.&()]+)"

    # Pattern 3: Colon-separated format
    pattern_colon = r"(?P<title>.*?)\s*:\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*\[(?P<end>\d{2}/\d{4}|Present)\]"

    # Pattern 4: 'at' format
    pattern_at = r"(?P<title>.*?)\s+at\s+(?P<company>.*?)\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*\[(?P<end>\d{2}/\d{4}|Present)\]"

    # Pattern 5: Multiline format without brackets
    pattern_unbracketed = r"(?P<title>.*?)\n(?P<company>.*?)\n(?P<start>\d{2}/\d{4})\s*-\s*(?P<end>\d{2}/\d{4}|Present)"
    
    # Regex for job blocks
    pattern_jobblocks = r"(?P<title>.+?),\s*(?P<company>.+?)\n(?P<start>[A-Za-z\.]+ \d{4})\s*-\s*(?P<end>[A-Za-z\.]+ \d{4}|Present)"

        # Step 3a: Extract skills and filter text
    skills = extract_skills_from_resume(text)
    lines = text.split("\n")
    skills_lower = [s.lower() for s in skills]

    filtered_text = "\n".join([line for line in lines if line.strip() and line.strip().lower() not in skills_lower])
    # Combine all matches
    matches = list(re.finditer(pattern_multiline, text)) + \
              list(re.finditer(pattern_inline, text)) + \
              list(re.finditer(pattern_colon, text)) + \
              list(re.finditer(pattern_at, text)) + \
              list(re.finditer(pattern_jobblocks, filtered_text)) + \
              list(re.finditer(pattern_unbracketed, text))
    


    for match in matches:
        title = match.group("title").strip()
        company = match.group("company").strip() if "company" in match.groupdict() and match.group("company") else ""
        # Clean company from skills
        for skill in skills_lower:
                pattern_skill = r"\b" + re.escape(skill) + r"\b.*"
                company = re.sub(pattern_skill, "", company, flags=re.IGNORECASE).strip()
        start = match.group("start")
        end = match.group("end") if match.group("end") else match.group("present")

        try:
            start_date = parser.parse(start)
            end_date = datetime.now() if end.lower() == "present" else parser.parse(end)
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += months
            years_fraction = round(months / 12, 1)
            duration = f"{months} months ({years_fraction} years)"
            formatted = f"{title} - {company}: [{start}] - [{end}] = {duration}"
            experience_entries.append(formatted)
        except Exception as e:
            print(f"Error parsing: {title} at {company} — {e}")
            continue
    total_years = round(total_months / 12, 1)
    return experience_entries, total_years


# --- Fallback 1: Regex for explicit years in text ---
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


# --- Main Checker ---
def check_experience_requirement(resume_text, requirement="5+ years"):
    required_years = int(re.search(r"(\d+)", requirement).group(1))

    # Step 1: Try your advanced parser
    entries, total_years = extract_experience_entries(resume_text)
    if total_years > 0:
        return total_years >= required_years, total_years, "method=experience_entries"

    # Step 2: Try regex patterns
    regex_years = extract_years_from_text(resume_text)
    if regex_years > 0:
        return regex_years >= required_years, regex_years, "method=regex_years"

    # Step 3: Fallback → let SBERT similarity decide
    # (pretend semantic similarity ≥0.75 counts as satisfying requirement)
    # For real pipeline, plug in SBERT model here
    sbert_score = 0.72  # placeholder, replace with model.encode()
    return sbert_score >= 0.75, None, "method=sbert"


