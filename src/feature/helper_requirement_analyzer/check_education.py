import re

from sentence_transformers import SentenceTransformer, util
import torch

from src.feature.dataclasses.requirementresults import RequirementResult

# -----------------------
# Check Education Requirement (Improved)
# -----------------------
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
def check_education(resume_text, requirement):
    """
    Checks if a required degree AND relevant field exist in the resume.
    Returns a RequirementResult object.
    """
    requirement_lower = requirement.lower()

    # Detect required degree type
    if "bachelor" in requirement_lower or "b.sc" in requirement_lower:
        req_degree_keywords = ["bachelor", "b.sc", "bs", "b.eng", "b.engg"]
    elif "master" in requirement_lower or "m.sc" in requirement_lower:
        req_degree_keywords = ["master", "m.sc", "ms", "mba"]
    else:
        req_degree_keywords = []

    # Detect required field
    req_fields = []
    if "computer science" in requirement_lower:
        req_fields.append("computer science")
    if "engineering" in requirement_lower:
        req_fields.append("engineering")

    # Extract clean education lines from resume
    edu_lines = []
    for line in resume_text.split("\n"):
        clean_line = line.strip()
        if not clean_line:
            continue

        if "http" in clean_line.lower() or re.fullmatch(r"[\d\-\.,]+", clean_line):
            continue
        if "@" in clean_line or "email" in clean_line.lower():
            continue
        if re.search(r"\b\d{4}\b", clean_line) and "degree" not in clean_line.lower():
            # ignore standalone years unless part of degree
            continue
        
        if any(k in clean_line.lower() for k in req_degree_keywords):
            edu_lines.append(clean_line)

    matched_line = None
    matched_keywords = []
    missing_keywords = []
    semantic_matched = []
    for line in edu_lines:
        line_lower = line.lower()
        if any(f in line_lower for f in req_fields):
            matched_line = line
            break

    if matched_line:
        is_matched = True
        status = "✅ Match"
        reason = f"user has {matched_line.strip()}"
    elif edu_lines:
        # status = "❌ Missing"
        # reason = f"Field not specified in requirement, user has {edu_lines[0].strip()}"  # Degree present but field mismatch
        # ---- Semantic similarity check if no direct match ----
        req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
        res_embs = sbert_model.encode(edu_lines, convert_to_tensor=True)
        sims = util.cos_sim(req_emb, res_embs)[0]

        best_idx = int(torch.argmax(sims))
        best_score = float(sims[best_idx])

        if best_score >= 0.45:  # threshold
            is_matched = True
            status = "✅ Match"
            reason = f"user has {edu_lines[best_idx].strip()}"
            semantic_matched.append(edu_lines[best_idx].strip())
            matched_keywords.append(edu_lines[best_idx].strip())
        else:
            is_matched = False
            status = "❌ Missing"
            reason = f"Field not specified in requirement, user has {edu_lines[0].strip()}"
            matched_keywords.append(edu_lines[0].strip())
            missing_keywords.append(requirement)
    else:
        is_matched = False
        status = "❌ Missing"
        reason = f"No degree mentioned matching requirement"
        missing_keywords.append(requirement)

    return RequirementResult(
        requirement=requirement,
        is_matched=is_matched,
        status=status,
        reason=reason,
        category="Education",
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        semantic_matched=semantic_matched
    )
