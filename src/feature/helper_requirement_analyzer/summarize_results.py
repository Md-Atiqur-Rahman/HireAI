import pandas as pd
from src.feature.dataclasses.Score import Score


def summarize_results(results):
    """
    Returns overall score and detailed summary grouped by category.
    Fail only if Experience or TechnicalSkills are completely missing.
    Proportional score applied for TechnicalSkills, Education, and Others if multiple requirements exist.
    """
    weights = {
        "Experience": 30,
        "Education": 20,
        "TechnicalSkills": 30,
        "Others": 20
    }

    total_weight = 0
    earned_weight = 0

    matched = []
    missing = []
    matched_skills = []
    missing_skills = []
    semantic_matches = []
    category_scores = {
        "Experience": 0,
        "Education": 0,
        "TechnicalSkills": 0,
        "Others": 0
    }

    fail_due_to_critical = False

    # --- Preprocess TechnicalSkills ---
    tech_results = [r for r in results if r.category == "TechnicalSkills"]
    tech_any_matched = any(r.is_matched for r in tech_results)

    if tech_results and not tech_any_matched:
        fail_due_to_critical = True

    # --- Group results by category for proportional calculation ---
    categories = {}
    for r in results:
        cat = r.category if r.category else "Other"
        categories.setdefault(cat, []).append(r)

    for cat, cat_results in categories.items():
        weight = weights.get(cat, 0)
        total_weight += weight

        if cat in ["TechnicalSkills", "Education", "Others"]:
            n_reqs = len(cat_results)
            if n_reqs == 0:
                continue
            per_req_weight = weight / n_reqs
            cat_earned = 0
            for r in cat_results:
                req = r.requirement
                status = r.status
                ismatched = r.is_matched
                if cat == "TechnicalSkills": 
                    if r.is_matched:
                        earned_weight += per_req_weight
                        cat_earned += per_req_weight
                        matched.append(f"{req} (Matched: {', '.join(r.matched_keywords)})")
                        matched_skills.extend(r.matched_keywords)
                        # collect semantic matches if present
                        if hasattr(r, "semantic_matched") and r.semantic_matched:
                            semantic_matches.extend(r.semantic_matched)
                    else:
                        missing.append(f"{req} (No {', '.join(r.missing_keywords)} mentioned)")
                        missing_skills.extend(r.missing_keywords)
                        if hasattr(r, "semantic_matched") and r.semantic_matched:
                            semantic_matches.extend(r.semantic_matched)

                else:  # Education or Others
                    if r.is_matched:
                        earned_weight += per_req_weight
                        cat_earned += per_req_weight
                        reason = getattr(r, "reason", "Met")
                        matched.append(f"{req} ({reason})")
                        if hasattr(r, "semantic_matched") and r.semantic_matched:
                            semantic_matches.extend(r.semantic_matched)
                    else:
                        if hasattr(r, "semantic_matched") and r.semantic_matched:
                            semantic_matches.extend(r.semantic_matched)
                        if cat == "Education":
                            reason = getattr(r, "reason", "Not mentioned")
                            missing.append(f"{req} ({reason})")
                        else: missing.append(f"{req} (Not mentioned)")
            category_scores[cat] = round((cat_earned / weight) * 100, 1) if weight > 0 else 0

        elif cat == "Experience":
            cat_earned = 0
            for r in cat_results:
                req = r.requirement
                status = r.status
                ismatched = r.is_matched
                if r.is_matched:
                    earned_weight += weight
                    cat_earned += weight
                    reason = getattr(r, "experience_check", "Met")
                    matched.append(f"{req} ({reason})")
                    matched_skills.extend(r.matched_keywords)
                    if hasattr(r, "semantic_matched") and r.semantic_matched:
                        semantic_matches.extend(r.semantic_matched)
                else:
                    fail_due_to_critical = True
                    reason = getattr(r, "experience_check", "Not mentioned")
                    missing.append(f"{req} ({reason})")
                    missing_skills.extend(r.missing_keywords)
                    if hasattr(r, "semantic_matched") and r.semantic_matched:
                        semantic_matches.extend(r.semantic_matched)
            category_scores["Experience"] = round((cat_earned / weight) * 100, 1) if weight > 0 else 0
        else:
            for r in cat_results:
                req = r.requirement
                status = r.status
                ismatched = r.is_matched
                if r.is_matched:
                    earned_weight += weight
                    cat_earned += weight
                    matched.append(f"{req} (Met)")
                else:
                    missing.append(f"{req} (Not mentioned)")

    overall_score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0
    
    status_Rank = 0
    if fail_due_to_critical:
        overall_score_display = f"{overall_score}% – ❌ Not Qualified"
        fail_reason = "Critical experience or technical skill missing"
        status = "❌ Not Qualified" 
        ismatched = False
        status_Rank = 0
    else:
        status,status_Rank = check_Status(overall_score,False)
        overall_score_display = f"{overall_score}% - ✅ {status}"
        fail_reason = None
        


    semantic_matches = sorted(set(semantic_matches))
    matched_skills = sorted(set(matched_skills))
    missing_skills = sorted(set(missing_skills))

    lines = [
        "📊 Summary:",
        f"✅ Matches {len(matched)} of {len(results)} required qualifications",
        f"\n📌 Met Requirements:\n   ✅ " + "\n   ✅ ".join(matched) if matched else "📌 Met: None",
        f"\n   Matched Skills: {', '.join(matched_skills)}" if matched_skills else "",
        f"\n⚠️ Missing Requirements:\n   ❌ " + "\n   ❌ ".join(missing) if missing else "⚠️ Missing: None",
        f"\n   Missing Skills: {', '.join(missing_skills)}" if missing_skills else "",
        f"\n🔢 Score: {overall_score_display}"
    ]
    if fail_reason:
        lines.append(f"Reason: {fail_reason}")
    
    summary_text = "\n".join([line for line in lines if line])
    score_obj = Score(
    experience=category_scores.get("Experience", 0),
    education=category_scores.get("Education", 0),
    technical_skills=category_scores.get("TechnicalSkills", 0),
    others=category_scores.get("Others", 0),
    total=overall_score,
    is_matched= not fail_due_to_critical,
    status=status)


     # --- Build grouped DataFrame per category ---
    raw_rows = []
    for cat, cat_results in categories.items():
        for r in cat_results:
            total_keywords = len(r.matched_keywords) + len(r.missing_keywords)
            match_percent = round(100 * len(r.matched_keywords) / total_keywords, 1) if total_keywords > 0 else 0
            raw_rows.append({
                "Category": cat,
                "Requirement": r.requirement,
                "KeywordsMatched": ", ".join(r.matched_keywords),
                "SemanticMatches": ", ".join(getattr(r, "semantic_matched", [])),
                "MissingRequirements": ", ".join(r.missing_keywords),
                "MatchPercent": match_percent
            })
    #df_grouped = pd.DataFrame(raw_rows)
    #semantic_matched
    #semantic_matched
    return overall_score, summary_text, score_obj,raw_rows,status_Rank

def check_Status(overall_score, fail_due_to_critical=False):
    if fail_due_to_critical:
        return "Not Qualified",0
    elif overall_score >= 85:
        return "Highly Qualified",3
    elif overall_score >= 60:
        return "Qualified",2
    else:
        return "Not Qualified",1
