

from sentence_transformers import SentenceTransformer,util
import spacy
import torch

from src.feature.dataclasses.requirementresults import RequirementResult


nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

def check_others_requirement(requirement,resume_sentences,req_keywords,resume_keywords,category):
    req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
    res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
    sims = util.cos_sim(req_emb, res_embs)[0]
    best_score = float(torch.max(sims)) if len(sims) > 0 else 0

    
    matched = req_keywords & resume_keywords
    missing = req_keywords - resume_keywords
    return RequirementResult(
        requirement=requirement,
        status="✅ Match" if best_score >= 0.5 else "❌ Missing",
        score= round(best_score, 2),
        category=category,
        matched_keywords=matched,
        missing_keywords=missing
    )