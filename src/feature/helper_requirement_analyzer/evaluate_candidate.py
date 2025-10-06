import pandas as pd

from src.feature.helper_requirement_analyzer.summarize_results import summarize_results

def evaluate_candidate(candidate_id,overall_score, results):
    """
    Wrapper around summarize_results to get detailed category scores
    and a status label for each candidate.
    """
    overall_score, summary = summarize_results(results)

    # Initialize category scores
    cat_scores = {"Experience": 0, "Education": 0, "TechnicalSkills": 0, "Others": 0}
    cat_counts = {"Experience": 0, "Education": 0, "TechnicalSkills": 0, "Others": 0}
    cat_matched = {"Experience": 0, "Education": 0, "TechnicalSkills": 0, "Others": 0}

    # Calculate per-category proportional score
    for r in results:
        if r.category in cat_scores:
            cat_counts[r.category] += 1
            if r.status.startswith("✅"):
                cat_matched[r.category] += 1

    for cat in cat_scores:
        if cat_counts[cat] > 0:
            cat_scores[cat] = round((cat_matched[cat] / cat_counts[cat]) * 100, 1)

    # Assign status
    if overall_score >= 85:
        status = "Highly Qualified"
    elif overall_score >= 60:
        status = "Qualified"
    else:
        status = "Not Qualified"

    return {
        "Candidate": candidate_id,
        "Experience (%)": cat_scores["Experience"],
        "Education (%)": cat_scores["Education"],
        "Technical Skills (%)": cat_scores["TechnicalSkills"],
        "Others (%)": cat_scores["Others"],
        "Final Score": overall_score,
        "Status": status
    }

def build_summary_table(all_candidates_results):
    """
    all_candidates_results = {
        "C1": results_for_C1,
        "C2": results_for_C2,
        "C3": results_for_C3
    }
    """
    records = []
    for cid, results in all_candidates_results.items():
        record = evaluate_candidate(cid, results)
        records.append(record)

    df = pd.DataFrame(records)
    return df
