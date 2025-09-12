from sklearn.feature_extraction.text import TfidfVectorizer
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


def extract_skills_tfidf(resume_text, jd_text, top_n=10):
    documents = [jd_text, resume_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    resume_scores = tfidf_matrix[1].toarray()[0]
    top_indices = resume_scores.argsort()[::-1][:top_n]
    return [feature_names[i] for i in top_indices if resume_scores[i] > 0]

