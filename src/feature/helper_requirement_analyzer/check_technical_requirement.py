import os
import re
import sys
from sentence_transformers import SentenceTransformer, util
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.feature.dataclasses.requirementresults import RequirementResult

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")


def split_technical_requirement(req_text):
    # split by commas, slashes, or standalone "and/or", parentheses
    parts = re.split(r",|/|\band\b|\bor\b|\(|\)", req_text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]

def split_skills_line(line):
    parts = re.split(r",|/|\band\b|\bor\b", line)
    return [p.strip() for p in parts if p.strip()]

def check_technical_requirement(requirement, resume_text):
    required_skills = split_technical_requirement(requirement)
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]

    matched, missing = [], []

    # encode resume sentences once
    resume_skills_sentences = []
    for sent in resume_sentences:
        if "," in sent and len(sent.split()) < 20:  # heuristic: likely a skills list
            resume_skills_sentences.extend(split_skills_line(sent))
        else:
            resume_skills_sentences.append(sent)

    # Now embed properly
    resume_embs = sbert_model.encode(resume_skills_sentences, convert_to_tensor=True)

    for req_skill in required_skills:
        req_emb = sbert_model.encode(req_skill, convert_to_tensor=True)
        sims = util.cos_sim(req_emb, resume_embs)[0]
        test =float(sims.max())
        if float(sims.max()) >= 0.5:  # semantic threshold
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
