
import re

from sentence_transformers import SentenceTransformer,util
import spacy
nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")


def check_experience_skills(resume_text,requirement,resume_keywords,total_years,exp_ok,category):
    skills_part = re.split(r"experience in|with experience in|experience with", requirement, flags=re.IGNORECASE)[-1]
    required_skills = [s.strip() for s in re.split(r"[,/|]", skills_part) if s.strip()]

    matched, missing = [], []
    skills_ok = True
    for req in required_skills:
        # For short keywords or symbols, match exact in resume text
        if len(req) <= 3 or re.search(r"[#\.\-]", req):  # C#, .NET, etc.
            if re.search(re.escape(req), resume_text, re.IGNORECASE):
                matched.append(req)
            else:
                missing.append(req)
        else:
            # Use SBERT for longer phrases
            req_emb = sbert_model.encode(req, convert_to_tensor=True)
            cand_embs = sbert_model.encode(list(resume_keywords), convert_to_tensor=True)
            sims = util.cos_sim(req_emb, cand_embs)[0]
            if float(sims.max()) >= 0.5:
                matched.append(req)
            else:
                missing.append(req)


        skills_ok = len(matched) / len(required_skills) >= 0.5

    # Final status: only if BOTH experience and skills are ok
    status = "✅ Match" if exp_ok and skills_ok else "❌ Missing"

    print("matched------------\n", {', '.join(matched)})  # debug

    # Build reason string
    if not exp_ok and not skills_ok:
        reason = f"User has {total_years} years and no {', '.join(missing)} mentioned"
    elif not exp_ok:
        reason = f"User has {total_years} years"
    elif not skills_ok:
        reason = f"User has {total_years} years and no {', '.join(missing)} mentioned"
    else:
        reason = f"User has {total_years} years"
        
    return {
        "requirement": requirement,
        "status": status,
        "experience_check": reason,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "exp_ok": exp_ok,
        "skills_ok": skills_ok,
        "category": category
        }
        