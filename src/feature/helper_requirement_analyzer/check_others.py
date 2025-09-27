

from sentence_transformers import SentenceTransformer,util
import spacy
import torch

from src.feature.helper_requirement_analyzer.check_technical_requirement import split_skills_line
from src.feature.dataclasses.requirementresults import RequirementResult


nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

def check_others_requirement(requirement,resume_text,req_keywords,resume_keywords,category):
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]
    resume_skills_sentences = []
    for sent in resume_sentences:
        if "," in sent and len(sent.split()) < 20:  # heuristic: likely a skills list
            resume_skills_sentences.extend(split_skills_line(sent))
        else:
            resume_skills_sentences.append(sent)
            
    
    req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
    res_embs = sbert_model.encode(resume_skills_sentences, convert_to_tensor=True)
    sims = util.cos_sim(req_emb, res_embs)[0]
    test = float(sims.max())
    test2=float(torch.max(sims))
    best_score = float(torch.max(sims)) if len(sims) > 0 else 0

    
    # SBERT similarity threshold
    if best_score >= 0.5:
        status = "✅ Match"
    else:
        # fallback to keyword overlap
        matched = req_keywords & resume_keywords
        missing = req_keywords - resume_keywords
        status = "✅ Match" if len(matched) / len(req_keywords) >= 0.5 else "❌ Missing"
        return RequirementResult(
            requirement=requirement,
            status=status,
            score=round(best_score, 2),
            category=category,
            matched_keywords=matched,
            missing_keywords=missing
        )

    # If SBERT match is good, consider all requirement keywords matched
    return RequirementResult(
        requirement=requirement,
        status=status,
        score=round(best_score, 2),
        category=category,
        matched_keywords=req_keywords,
        missing_keywords=set()
    )