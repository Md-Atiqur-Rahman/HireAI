import re
from dateutil import parser
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

import re

def extract_skills(text):
    # Look for 'Skills' section (common in resumes)
    match = re.search(r"Skills\s*(.*?)(Experience|$)", text, re.DOTALL | re.IGNORECASE)
    if match:
        skills_text = match.group(1)
        #print(skills_text)
        # Split by common separators: comma, newline, semicolon
        skills = re.split(r"[,\n;]", skills_text)
        # Clean whitespace & remove empty
        skills = [s.strip() for s in skills if s.strip()]
        return skills
    return []

def extract_skills_from_resume(resume_text, top_n=15):
    # Preprocess text: remove extra symbols and lowercase
    clean_text = re.sub(r"[^A-Za-z0-9\s]", " ", resume_text)
    clean_text = re.sub(r"\s+", " ", clean_text).lower()
    
    # Treat each sentence/line as a "document"
    lines = [line.strip() for line in clean_text.split("\n") if line.strip()]
    
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
    tfidf_matrix = vectorizer.fit_transform(lines)
    
    # Sum TF-IDF scores for each term across all lines
    scores = tfidf_matrix.sum(axis=0).A1
    feature_names = vectorizer.get_feature_names_out()
    
    # Get top_n terms
    top_indices = scores.argsort()[::-1][:top_n]
    top_skills = [feature_names[i] for i in top_indices if scores[i] > 0]
    
    return top_skills

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




# Example usage
if __name__ == "__main__":
    
    pdf_path = "E:/Thesis/resume-analyzer/resumes/John Doe.pdf"
    pdf_path = "E:/Thesis/resume-analyzer/resumes/Craig Kovatch Kovatch.pdf"
    pdf_path = "E:/Thesis/resume-analyzer/resumes/Kumaresan-resume.pdf"
    pdf_path = "E:/Thesis/resume-analyzer/resumes/Josh Hinton Hinton.pdf"
    pdf_path = "E:/Thesis/resume-analyzer/resumes/Md Atiqur Rahman.pdf"
    text = extract_text_from_pdf(pdf_path)
    entries, total = extract_experience_entries(text)

    for entry in entries:
        print(entry)
    print(f"Total experiences = {total} Years")
