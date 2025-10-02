import re

from src.feature.dataclasses.requirementresults import RequirementResult

# -----------------------
# Check Education Requirement (Improved)
# -----------------------
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
    for line in edu_lines:
        line_lower = line.lower()
        if any(f in line_lower for f in req_fields):
            matched_line = line
            break

    if matched_line:
        status = "✅ Match"
        reason = f"user has {matched_line.strip()}"
    elif edu_lines:
        status = "❌ Missing"
        reason = f"Field not specified in requirement, user has {edu_lines[0].strip()}"  # Degree present but field mismatch
    else:
        status = "❌ Missing"
        reason = f"No degree mentioned matching requirement"

    return RequirementResult(
        requirement=requirement,
        status=status,
        reason=reason,
        category="Education"
    )
