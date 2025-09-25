def summarize_results(results):
    """
    Returns overall score and detailed summary grouped by category.
    Fail only if:
        - Experience requirement not satisfied (years বা skills fail হলে)
        - OR all TechnicalSkills requirements are ❌ Missing
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

    # --- Check TechnicalSkills overall ---
    tech_results = [r for r in results if r.get("category") == "TechnicalSkills"]
    tech_has_match = any(r["status"].startswith("✅") for r in tech_results)

    if tech_results and not tech_has_match:
        fail_due_to_critical = True  # সব TechnicalSkills missing হলে FAIL

    for r in results:
        req = r["requirement"]
        status = r["status"]
        cat = r.get("category", "Other")

        weight = weights.get(cat, 1)
        total_weight += weight

        # ✅ Matched case
        if status.startswith("✅"):
            if cat == "TechnicalSkills":
                # proportional scoring based on matched vs total
                total_req_count = len(r.get("matched_keywords", [])) + len(r.get("missing_keywords", []))
                if total_req_count > 0:
                    per_req_weight = weight / total_req_count
                    earned_weight += per_req_weight * len(r.get("matched_keywords", []))
                matched.append(f"{req} (Matched: {', '.join(r['matched_keywords'])})")
                matched_skills.extend(r['matched_keywords'])

            elif cat == "Experience":
                # Experience pass হলে weight add হবে
                earned_weight += weight
                reason = r.get("experience_check", "Experience check not available")
                matched.append(f"{req} ({reason})")

                # check skills_ok, exp_ok
                if not r.get("exp_ok", True) or not r.get("skills_ok", True):
                    fail_due_to_critical = True

            elif cat == "Education":
                earned_weight += weight
                matched.append(f"{req} ({r.get('reason','Met')})")

            elif cat in ["Skills", "Others"]:
                earned_weight += weight
                if r.get("matched_keywords"):
                    matched.append(f"{req} (Matched: {', '.join(r['matched_keywords'])})")
                    matched_skills.extend(r['matched_keywords'])
                else:
                    matched.append(f"{req} (Met)")

        # ❌ Missing case
        else:
            if cat == "Experience":
                fail_due_to_critical = True
                reason = r.get("experience_check", "Not mentioned")
                missing.append(f"{req} ({reason})")

            elif cat == "Education":
                missing.append(f"{req} ({r.get('reason','Not mentioned')})")

            elif cat in ["TechnicalSkills", "Skills", "Others"]:
                if r.get("missing_keywords"):
                    missing.append(f"{req} (No {', '.join(r['missing_keywords'])} mentioned)")
                    missing_skills.extend(r['missing_keywords'])
                else:
                    missing.append(f"{req} (Not mentioned)")

    overall_score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0
    overall_score_display = (
        "❌ FAIL (Critical Experience or all TechnicalSkills missing)"
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
        f"\n🔢 Score: {overall_score_display}"
    ]

    return overall_score, "\n".join([line for line in lines if line])
