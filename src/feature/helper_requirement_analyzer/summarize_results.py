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

    fail_due_to_critical = False

    # --- Preprocess TechnicalSkills ---
    tech_results = [r for r in results if r.category == "TechnicalSkills"]
    tech_any_matched = any(len(r.matched_keywords) > 0 for r in tech_results)
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
            for r in cat_results:
                req = r.requirement
                status = r.status
                if cat == "TechnicalSkills": 
                    if r.matched_keywords:
                        earned_weight += per_req_weight
                        matched.append(f"{req} (Matched: {', '.join(r.matched_keywords)})")
                        matched_skills.extend(r.matched_keywords)
                    else:
                        missing.append(f"{req} (No {', '.join(r.missing_keywords)} mentioned)")
                        missing_skills.extend(r.missing_keywords)
                else:  # Education or Others
                    if status.startswith("✅"):
                        earned_weight += per_req_weight
                        reason = getattr(r, "reason", "Met")
                        matched.append(f"{req} ({reason})")
                    else:
                        missing.append(f"{req} (Not mentioned)")

        elif cat == "Experience":
            for r in cat_results:
                req = r.requirement
                status = r.status
                if status.startswith("✅"):
                    earned_weight += weight
                    reason = getattr(r, "experience_check", "Met")
                    matched.append(f"{req} ({reason})")
                    matched_skills.extend(r.matched_keywords)
                else:
                    fail_due_to_critical = True
                    reason = getattr(r, "experience_check", "Not mentioned")
                    missing.append(f"{req} ({reason})")
                    missing_skills.extend(r.missing_keywords)

        else:
            for r in cat_results:
                req = r.requirement
                status = r.status
                if status.startswith("✅"):
                    earned_weight += weight
                    matched.append(f"{req} (Met)")
                else:
                    missing.append(f"{req} (Not mentioned)")

    overall_score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0
    overall_score_display = (
        "FAIL (Critical experience or technical skill missing)"
        if fail_due_to_critical else f"{overall_score}%"
    )

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

    return overall_score, "\n".join([line for line in lines if line])
