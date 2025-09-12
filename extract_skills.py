from sklearn.feature_extraction.text import TfidfVectorizer
import re

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
