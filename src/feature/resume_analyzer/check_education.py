def check_education(resume_text, requirement):
    """
    Checks if a required degree AND relevant field exist in the resume.
    Returns status and reason string.
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

    # Find all education lines in resume
    edu_lines = []
    for line in resume_text.split("\n"):
        line_lower = line.strip().lower()
        if any(k in line_lower for k in req_degree_keywords):
            edu_lines.append(line.strip())

    if not edu_lines:
        return "❌ Missing", f"No bachelor's degree in Computer Science or Engineering mentioned"

    # Check for field match
    for line in edu_lines:
        line_lower = line.lower()
        if any(f in line_lower for f in req_fields):
            return "✅ Met", f"user has {line.strip()}"  # Field matched

    # Degree present but field not matched
    return "❌ Missing", f"Degree present but field not mentioned (match: {', '.join(edu_lines)})"

