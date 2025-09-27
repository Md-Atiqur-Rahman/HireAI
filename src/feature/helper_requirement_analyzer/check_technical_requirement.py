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
      # --- 1. Extract required skills from requirement text ---
    required_skills = split_technical_requirement(requirement)
    
    #required_skills = [s.strip() for s in re.split(r"[,/|]", skills_part) if s.strip()]
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]

    matched = []
    missing = []

    resume_skills_sentences = []
    for sent in resume_sentences:
        if "," in sent and len(sent.split()) < 20:  # heuristic: likely a skills list
            resume_skills_sentences.extend(split_skills_line(sent))
        else:
            resume_skills_sentences.append(sent)
    # --- 2. Match skills ---
    for skill in required_skills:
        found = False

        # Direct mention in resume text
        if re.search(rf"\b{re.escape(skill)}\b", resume_text, re.IGNORECASE):
            matched.append(skill)
            found = True
        if not found:
            # Fallback to keyword bag
            for kw in resume_skills_sentences:
                if skill.lower() in kw.lower():
                    matched.append(skill)
                    found = True
                    break
        # --- 3. Fallback: semantic similarity (SBERT) ---
        if not found and len(skill.split()) > 1 and resume_skills_sentences:
            resume_embs = sbert_model.encode(resume_skills_sentences, convert_to_tensor=True)
            req_emb = sbert_model.encode(skill, convert_to_tensor=True)
            sims = util.cos_sim(req_emb, resume_embs)[0]
            test = float(sims.max())
            if float(sims.max()) >= 0.5:  # semantic threshold
                matched.append(skill)
                found = True
        if not found:
            missing.append(skill)

     # --- 3. Calculate skill match ratio ---
    skills_ratio = len(matched) / len(required_skills) if required_skills else 0
    #skills_ok = skills_ratio >= 0.5  # ✅ at least 50% match

    # --- 5. Build status & reason ---
    status = "✅ Match" if skills_ratio >= 0.5 else "❌ Missing"

    return RequirementResult(
        requirement=requirement,
        status=status,
        category="TechnicalSkills",
        matched_keywords=matched,
        missing_keywords=missing
    )
