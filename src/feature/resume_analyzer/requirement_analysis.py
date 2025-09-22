import re
from dateutil import parser
from datetime import datetime
import spacy
from sentence_transformers import SentenceTransformer, util
import torch

from src.Helper.resume_experience_gimini import generate_resume_experience_gemini
from src.Helper.parser import extract_text_from_pdf

# ===============================
# Load Models
# ===============================
nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# ===============================
# Experience Extractor
# ===============================
def extract_experience_entries(text):
    experience_entries = []
    total_months = 0

    patterns = [
        r"(?P<title>.*?)\n(?P<company>.*?)\n\[(?P<start>\d{2}/\d{4})\]\s*-\s*(\[(?P<end>\d{2}/\d{4})\]|(?P<present>Present))",
        r"(?P<title>.*?)\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*(\[(?P<end>\d{2}/\d{4})\]|(?P<present>Present))\s*(?P<company>[A-Za-z0-9 ,.&()]+)",
        r"(?P<title>.*?)\s*:\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*\[(?P<end>\d{2}/\d{4}|Present)\]",
        r"(?P<title>.*?)\s+at\s+(?P<company>.*?)\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*\[(?P<end>\d{2}/\d{4}|Present)\]",
        r"(?P<title>.*?)\n(?P<company>.*?)\n(?P<start>\d{2}/\d{4})\s*-\s*(?P<end>\d{2}/\d{4}|Present)",
        r"(?P<title>.+?),\s*(?P<company>.+?)\n(?P<start>[A-Za-z\.]+ \d{4})\s*-\s*(?P<end>[A-Za-z\.]+ \d{4}|Present)",

        r"(?P<title>.*?)\s*\|\s*(?P<company>.*?)\n(?P<start>[A-Za-z]+\s*\d{4})\s*[-–]\s*(?P<end>[A-Za-z]+\s*\d{4}|Present)",
        r"(?P<title>.*?)\s+(at|@)\s+(?P<company>.*?)\s*(?P<start>[A-Za-z]+\s*\d{4})\s*[-–]\s*(?P<end>[A-Za-z]+\s*\d{4}|Present)",
    ]

    matches = []
    for pat in patterns:
        matches += list(re.finditer(pat, text))

    for match in matches:
        title = match.group("title").strip()
        company = match.group("company").strip() if "company" in match.groupdict() and match.group("company") else ""
        start = match.group("start")
        end = match.group("end") if match.group("end") else match.group("present")

        try:
            start_date = parser.parse(start)
            end_date = datetime.now() if end.lower() == "present" else parser.parse(end)
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += months
            years_fraction = round(months / 12, 1)
            formatted = f"{title} - {company}: [{start}] - [{end}] = {months} months ({years_fraction} years)"
            experience_entries.append(formatted)
        except:
            continue

    total_years = round(total_months / 12, 1)
    print("total_years----->",total_years)
    return experience_entries, total_years

def extract_years_from_text(text):
    patterns = [
        r"(\d+)\+?\s+years of experience",
        r"over (\d+)\s+years",
        r"more than (\d+)\s+years"
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0

# ===============================
# Keyword Extractor
# ===============================
def extract_keywords(text):
    doc = nlp(text.lower())
    return {token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"]}

# ===============================
# Requirement Checker
# ===============================
def check_requirement1(requirement, resume_sentences, resume_keywords, resume_text):
    # Handle experience requirement separately
    if "year" in requirement.lower():
        # Detect range "X-Y years"
        range_match = re.search(r"(\d+)\s*-\s*(\d+)\s*years", requirement, re.IGNORECASE)
        single_match = re.search(r"(\d+)\+?\s*years", requirement, re.IGNORECASE)

        min_years, max_years = None, None
        if range_match:
            min_years, max_years = int(range_match.group(1)), int(range_match.group(2))
        elif single_match:
            min_years = int(single_match.group(1))

        # Step 1: Try advanced extraction
        # total_years = generate_resume_experience_gemini(resume_text)
        # print(total_years)
        _, total_years = extract_experience_entries(resume_text)

        # Step 2: Fallback regex if advanced extraction fails
        if total_years == 0:
            total_years = extract_years_from_text(resume_text)

        # Step 3: Check requirement match
        if min_years is not None and max_years is not None:  
            status = "✅ Match" if min_years <= total_years <= max_years else "❌ Missing"
            experience_check = f"Requirement: {min_years}-{max_years} years, Candidate: {total_years} years"
        elif min_years is not None:  
            status = "✅ Match" if total_years >= min_years else "❌ Missing"
            experience_check = f"Requirement: {min_years}+ years, Candidate: {total_years} years"
        else:
            status = "❌ Missing"
            experience_check = f"Requirement unclear, Candidate: {total_years} years"

        # Continue with SBERT + keyword analysis for skills part
        req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
        res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
        sims = util.cos_sim(req_emb, res_embs)[0]
        best_idx = int(torch.argmax(sims))
        best_score = float(sims[best_idx])
        best_sentence = resume_sentences[best_idx] if resume_sentences else ""
        req_keywords = extract_keywords(requirement)
        matched = req_keywords & resume_keywords
        missing = req_keywords - resume_keywords

        return {
            "requirement": requirement,
            "status": status,
            "score": round(best_score, 2),
            "experience_check": experience_check,
            "best_sentence": best_sentence,
            "matched_keywords": list(matched),
            "missing_keywords": list(missing)
        }

    # ==========================
    # Generic (non-experience) requirement check
    # ==========================
    req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
    res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
    sims = util.cos_sim(req_emb, res_embs)[0]
    best_idx = int(torch.argmax(sims))
    best_score = float(sims[best_idx])
    best_sentence = resume_sentences[best_idx] if resume_sentences else ""
    req_keywords = extract_keywords(requirement)
    matched = req_keywords & resume_keywords
    missing = req_keywords - resume_keywords

    return {
        "requirement": requirement,
        "status": "✅ Match" if best_score >= 0.5 else "❌ Missing",
        "score": round(best_score, 2),
        "best_sentence": best_sentence,
        "matched_keywords": list(matched),
        "missing_keywords": list(missing)
    }

# ===============================
# Runner with Structured Requirements
# ===============================
def evaluate_resume1(resume_text, job_requirements):
    """
    Evaluates resume against structured job requirements (dict).
    """
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]
    resume_keywords = extract_keywords(resume_text)

    results = []

    for category, requirement in job_requirements.items():
        if not requirement.strip():
            continue  # skip empty category
        check = check_requirement1(requirement, resume_sentences, resume_keywords, resume_text)
        check["category"] = category  # track which category it belongs to
        results.append(check)

    # 🔹 Total work experience from experience requirements
    exp_results = [r for r in results if r["category"].lower() == "experience"]
    total_experience = 0.0
    if exp_results:
        for r in exp_results:
            if "experience_check" in r:
                match = re.search(r"Candidate:\s*([\d\.]+)\s*years", r["experience_check"])
                if match:
                    total_experience = float(match.group(1))
                    break

    # 🔹 Get overall summary
    overall_score, summary_text = summarize_results(results)

    return summary_text, total_experience, overall_score

def check_requirement(requirement, resume_sentences, resume_keywords, resume_text, category="Other"):
    """
    Enhanced requirement checker:
    - For Experience: validates years + skills (both must match)
    - Skills must meet >=50% semantic match
    - For TechnicalSkills: same semantic threshold
    - For others: SBERT + keyword match
    """
    # ---------- EXPERIENCE ----------
    if category.lower() == "experience" or "year" in requirement.lower():
        # Extract min/max years
        range_match = re.search(r"(\d+)\s*-\s*(\d+)\s*years", requirement, re.IGNORECASE)
        single_match = re.search(r"(\d+)\+?\s*years", requirement, re.IGNORECASE)

        min_years, max_years = None, None
        if range_match:
            min_years, max_years = int(range_match.group(1)), int(range_match.group(2))
        elif single_match:
            min_years = int(single_match.group(1))

        # Extract total years from resume
        _, total_years = extract_experience_entries(resume_text)
        if total_years == 0:
            total_years = extract_years_from_text(resume_text)

        # Check years
        exp_ok = False
        if min_years is not None and max_years is not None:
            exp_ok = min_years <= total_years <= max_years
        elif min_years is not None:
            exp_ok = total_years >= min_years

        # Extract required skills from requirement (text after "in" or after years)
        skills_part = re.split(r"experience in|with experience in|experience with", requirement, flags=re.IGNORECASE)[-1]
        required_skills = [s.strip() for s in re.split(r"[,/|]", skills_part) if s.strip()]
        
        # Check skills with SBERT similarity
        matched, missing = [], []
        if required_skills:
            req_embs = sbert_model.encode(required_skills, convert_to_tensor=True)
            cand_embs = sbert_model.encode(list(resume_keywords), convert_to_tensor=True)
            for i, req in enumerate(required_skills):
                sims = util.cos_sim(req_embs[i], cand_embs)[0]
                if float(sims.max()) >= 0.6:
                    matched.append(req)
                else:
                    missing.append(req)
            skills_ok = len(matched) / len(required_skills) >= 0.5
        else:
            skills_ok = True  # no skills required

        # Final status: only if BOTH experience and skills are ok
        status = "✅ Match" if exp_ok and skills_ok else "❌ Missing"
        experience_check = f"Requirement: {requirement}, Candidate: {total_years} years"

        return {
            "requirement": requirement,
            "status": status,
            "experience_check": experience_check,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "exp_ok": exp_ok,
            "skills_ok": skills_ok,
            "category": category
        }

    # ---------- TECHNICAL SKILLS ----------
    if category.lower() == "technicalskills":
        required_skills = [s.strip() for s in re.split(r"[,/|]", requirement) if s.strip()]
        candidate_skills = list(resume_keywords)

        req_embs = sbert_model.encode(required_skills, convert_to_tensor=True)
        cand_embs = sbert_model.encode(candidate_skills, convert_to_tensor=True)

        matched, missing = [], []
        for i, req in enumerate(required_skills):
            sims = util.cos_sim(req_embs[i], cand_embs)[0]
            if float(sims.max()) >= 0.6:  # semantic threshold
                matched.append(req)
            else:
                missing.append(req)

        ratio = len(matched) / len(required_skills) if required_skills else 0
        status = "✅ Match" if ratio >= 0.5 else "❌ Missing"

        return {
            "requirement": requirement,
            "status": status,
            "category": category,
            "matched_keywords": matched,
            "missing_keywords": missing
        }

    # ---------- GENERIC REQUIREMENTS ----------
    req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
    res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
    sims = util.cos_sim(req_emb, res_embs)[0]
    best_score = float(torch.max(sims)) if len(sims) > 0 else 0

    req_keywords = extract_keywords(requirement)
    matched = req_keywords & resume_keywords
    missing = req_keywords - resume_keywords

    return {
        "requirement": requirement,
        "status": "✅ Match" if best_score >= 0.5 else "❌ Missing",
        "score": round(best_score, 2),
        "category": category,
        "matched_keywords": list(matched),
        "missing_keywords": list(missing)
    }

def evaluate_resume(resume_text, job_requirements):
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]
    resume_keywords = extract_keywords(resume_text)

    results = []
    for category, requirement in job_requirements.items():
        if not requirement.strip():
            continue
        check = check_requirement(requirement, resume_sentences, resume_keywords, resume_text, category)
        results.append(check)

    overall_score, summary_text = summarize_results(results)
    total_experience = 0.0
    for r in results:
        if r["category"].lower() == "experience" and "experience_check" in r:
            match = re.search(r"Candidate:\s*([\d\.]+)\s*years", r["experience_check"])
            if match:
                total_experience = float(match.group(1))
                break

    return summary_text, total_experience, overall_score

# ===============================
# Improved Summarizer
# ===============================
def summarize_results(results):
    """
    Returns overall score and detailed summary grouped by category.
    Fail only if Experience or TechnicalSkills are missing.
    """
    weights = {
        "Experience": 3,
        "Education": 2,
        "TechnicalSkills": 3,
        "Skills": 1,
        "Others": 1
    }

    total_weight = 0
    earned_weight = 0

    matched = []
    missing = []
    matched_skills = []
    missing_skills = []

    fail_due_to_critical = False

    for r in results:
        req = r["requirement"]
        status = r["status"]
        cat = r.get("category", "Other")

        weight = weights.get(cat, 1)
        total_weight += weight

        # --- Handle Met ---
        if status.startswith("✅"):
            earned_weight += weight
            if cat == "Experience" and "experience_check" in r:
                reason = r["experience_check"].split("Candidate: ")[1]
                matched.append(f"{req} (User has {reason})")
            elif cat == "TechnicalSkills" and r.get("matched_keywords"):
                matched.append(f"{req} (Matched: {', '.join(r['matched_keywords'])})")
                matched_skills.extend(r['matched_keywords'])
            else:
                matched.append(f"{req} (Met)")

        # --- Handle Missing ---
        else:
            if cat in ["Experience", "TechnicalSkills"]:
                fail_due_to_critical = True  # only these can cause FAIL

            if cat == "Experience" and "experience_check" in r:
                reason = r["experience_check"].split("Candidate: ")[1]
                missing.append(f"{req} (User has {reason})")
            elif cat == "Education":
                missing.append(f"{req} (No degree mentioned)")
            elif cat in ["TechnicalSkills", "Skills"]:
                if r.get("missing_keywords"):
                    missing.append(f"{req} (No {', '.join(r['missing_keywords'])} mentioned)")
                    missing_skills.extend(r['missing_keywords'])
                else:
                    missing.append(f"{req} (Not mentioned)")
            else:
                missing.append(f"{req} (Not mentioned)")

    # --- Score Calculation ---
    overall_score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0
    if fail_due_to_critical:
        overall_score_display = "FAIL (Critical experience or technical skill missing)"
    else:
        overall_score_display = f"{overall_score}%"

    matched_skills = sorted(set(matched_skills))
    missing_skills = sorted(set(missing_skills))

    # --- Build Summary ---
    lines = [
        "📊 Summary:",
        f"✅ Matches {len(matched)} of {len(results)} required qualifications",
        f"\n📌 Met Requirements:\n   ✅ " + "\n   ✅ ".join(matched) if matched else "📌 Met: None",
        f"\n   Matched Skills: {', '.join(matched_skills)}" if matched_skills else "",
        f"\n⚠️ Missing Requirements:\n   ❌ " + "\n   ❌ ".join(missing) if missing else "⚠️ Missing: None",
        f"\n   Missing Skills: {', '.join(missing_skills)}" if missing_skills else "",
        f"\n🔢 Score: {overall_score_display}"
    ]

    return overall_score, "\n".join([line for line in lines if line])
