
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
                reason = r["experience_check"]
                matched.append(f"{req} ({reason})")
            elif cat in ["TechnicalSkills", "Skills"] and r.get("matched_keywords"):
                matched.append(f"{req} (Matched: {', '.join(r['matched_keywords'])})")
                matched_skills.extend(r['matched_keywords'])
            elif cat == "Education":
                matched.append(f"{req} ({r['reason']})")
            else:
                matched.append(f"{req} (Met)")

        # --- Handle Missing ---
        else:
            if cat in ["Experience", "TechnicalSkills"]:
                fail_due_to_critical = True  # only these can cause FAIL

            if cat == "Experience" and "experience_check" in r:
                reason = r["experience_check"]
                missing.append(f"{req} ({reason})")
            elif cat == "Education":
                missing.append(f"{req} ({r['reason']})")
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
    overall_score_display = (
        "FAIL (Critical experience or technical skill missing)"
        if fail_due_to_critical else f"{overall_score}%"
    )

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
