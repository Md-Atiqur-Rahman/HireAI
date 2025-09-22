import re

# -----------------------
# Check Education Requirement (Improved)
# -----------------------
def check_education(resume_text, requirement):
    """
    Checks if a required degree AND relevant field exist in the resume.
    Returns status and a polished reason string.
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

    # Extract clean education lines: avoid links, dates, or irrelevant text
    edu_lines = []
    for line in resume_text.split("\n"):
        clean_line = line.strip()
        # Skip lines that contain links or only numbers
        if "http" in clean_line.lower() or re.fullmatch(r"[\d\-\.,]+", clean_line):
            continue
        # Keep lines that contain degree keywords
        if any(k in clean_line.lower() for k in req_degree_keywords):
            edu_lines.append(clean_line)

    if not edu_lines:
        return "❌ Missing", f"No bachelor's degree in Computer Science or Engineering mentioned"

    # Check for field match
    for line in edu_lines:
        line_lower = line.lower()
        if any(f in line_lower for f in req_fields):
            return "✅ Met", f"user has {line.strip()}"  # Field matched

    # Degree present but field does not match
    # Extract just the degree + field (remove links/dates)
    user_field_clean = re.sub(r'\d{4}|\bhttp\S+\b', '', edu_lines[0]).strip()
    return "❌ Missing", f"Field of study not specified (User specified Field is {user_field_clean})"
