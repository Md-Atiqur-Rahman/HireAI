
import re
from sklearn.feature_extraction.text import TfidfVectorizer

def calculate_ats_score(resume_text, jd_text):
    """
    Compute ATS score based on formatting checks and keyword matching.

    Parameters:
    - resume_text (str): Raw text from resume
    - jd_text (str): Raw text from job description

    Returns:
    - dict: ATS Score, Keyword Match Score, Matched Keywords, Missing Keywords, Formatting Deductions
    """
    score = 100
    deductions = 0

    # Formatting checks
    if re.search(r"[-=]{5,}", resume_text):
        deductions += 10

    standard_headings = ["Professional Summary", "Work Experience", "Education", "Skills"]
    for heading in standard_headings:
        if heading not in resume_text:
            deductions += 5

    if not re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", resume_text):
        deductions += 10
    if not re.search(r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", resume_text):
        deductions += 10

    # TF-IDF keyword matching
    documents = [jd_text, resume_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    jd_scores = tfidf_matrix[0].toarray()[0]
    resume_scores = tfidf_matrix[1].toarray()[0]

    matched_keywords = [feature_names[i] for i in range(len(feature_names)) if jd_scores[i] > 0.1 and resume_scores[i] > 0]
    missing_keywords = [feature_names[i] for i in range(len(feature_names)) if jd_scores[i] > 0.1 and resume_scores[i] == 0]

    keyword_match_score = round(sum([jd_scores[i] for i in range(len(feature_names)) if jd_scores[i] > 0.1 and resume_scores[i] > 0]) / sum(jd_scores) * 100, 2) if sum(jd_scores) > 0 else 0

    if keyword_match_score < 50:
        deductions += 20
    elif keyword_match_score < 70:
        deductions += 10

    final_score = max(0, score - deductions)

    return {
        "ATS Score": final_score,
        "Keyword Match Score (%)": keyword_match_score,
        "Matched Keywords": matched_keywords,
        "Missing Keywords": missing_keywords,
        "Formatting Deductions": deductions,
        "Raw TF-IDF Scores": {
            "JD": jd_scores.tolist(),
            "Resume": resume_scores.tolist()
        }
    }

