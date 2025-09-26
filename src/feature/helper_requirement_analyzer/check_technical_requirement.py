import re
from sentence_transformers import SentenceTransformer, util

from src.feature.dataclasses.requirementresults import RequirementResult

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

def split_technical_requirement(req_text):
    # split by commas, slashes, "and", "or", parentheses
    parts = re.split(r",|/|and|or|\(|\)", req_text)
    return [p.strip() for p in parts if p.strip()]


def check_technical_requirement(requirement, resume_text):
    required_skills = split_technical_requirement(requirement)
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]

    matched, missing = [], []

    # encode resume sentences once
    resume_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)

    for req_skill in required_skills:
        req_emb = sbert_model.encode(req_skill, convert_to_tensor=True)
        sims = util.cos_sim(req_emb, resume_embs)[0]
        if float(sims.max()) >= 0.6:  # semantic threshold
            matched.append(req_skill)
        else:
            missing.append(req_skill)

    # --- 50% rule ---
    match_ratio = len(matched) / len(required_skills) if required_skills else 0
    status = "✅ Match" if match_ratio >= 0.5 else "❌ Missing"

    # return {
    #     "requirement": requirement,
    #     "status": status,
    #     "category": "TechnicalSkills",
    #     "matched_keywords": matched,
    #     "missing_keywords": missing
    # }
    return RequirementResult(
        requirement=requirement,
        status=status,
        category="TechnicalSkills",
        matched_keywords=matched,
        missing_keywords=missing
    )
