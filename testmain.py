import ast
import streamlit as st
from src.feature.helper_requirement_analyzer.requirement_analysis import evaluate_resume

resume_text = """
Software Engineer with 6 years of experience in .Net.
Holds a Bachelor's degree in Computer Science.
Worked with MongoDB and Oracle databases.
Practices clean code principles and pair programming occasionally.
ASP.NET Core, MVC, Web API,Angular or React,Git version control
Agile,
Fluent in oral and written communication in English
"""
job_requirements_str = "{'Experience': ['Full Stack Developer with 3 years of experience in C#,SQL'], 'Education': ['Bachelor’s degree in Computer Science'], 'TechnicalSkills': ['Strong in ASP.NET Core, MVC, Web API, MS SQL.', 'Experience with Angular or React for front-end development.', 'Familiarity with cloud platforms (Azure/AWS) and Git version control.'], 'Others': ['Project Management skills on Agile scrum', 'Fluent in oral and written communication in English']}"  

    # convert string → dict
job_requirements = ast.literal_eval(job_requirements_str)
summary_text, total_exp, total_score,technicalskills = evaluate_resume(resume_text, job_requirements)
# print("resume_text:------------\n",resume_text)
# print("job_requirements:--------------\n",job_requirements)
# print("skills:-------------\n",technicalskills)
# email = extract_email(resume_text)
# phone = extract_phone(resume_text)
# name = extract_name_from_text(resume_text,email)
#skills = extract_skills_tfidf(resume_text,"\n".join(job_requirements))
# save_candidate(name, email, phone, total_exp, total_score,technicalskills , summary_text, selected_category_id)
# summary_text = summarize_results(results)
# st.subheader("Resume Evaluation Summary")
print(summary_text) 