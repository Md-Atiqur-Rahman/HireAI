

import re
from src.feature.helper_requirement_analyzer.extract_experience import extract_experience_entries, extract_years_from_text
# from src.Helper.resume_experience_gimini import generate_resume_experience_gemini


def  check_exp_ok_or_not_ok(requirement,resume_text):
        range_match = re.search(r"(\d+)\s*-\s*(\d+)\s*years", requirement, re.IGNORECASE)
        single_match = re.search(r"(\d+)\+?\s*years", requirement, re.IGNORECASE)

        min_years, max_years = None, None
        required_years_str = None
        if range_match:
            min_years, max_years = int(range_match.group(1)), int(range_match.group(2))
            required_years_str = f"{min_years}-{max_years} years"
        elif single_match:
            min_years = int(single_match.group(1))
            required_years_str = f"{min_years} years"

        # Extract total years from resume

        experience_entries, total_years = extract_experience_entries(resume_text)
        if total_years == 0:
            experience_entries, total_years = extract_experience_entries(resume_text)
        if total_years == 0:
            total_years = extract_years_from_text(resume_text)
        # if total_years == 0:
        #     print("call gemini---")
        #     total_years = generate_resume_experience_gemini(resume_text)

        # Check years
        exp_ok = False
        if min_years is not None and max_years is not None:
            exp_ok = min_years <= total_years <= max_years
        elif min_years is not None:
            exp_ok = total_years >= min_years
        return total_years,exp_ok,required_years_str