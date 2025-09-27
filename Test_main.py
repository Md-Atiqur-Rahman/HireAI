
import ast
import streamlit as st
from src.feature.helper_requirement_analyzer.requirement_analysis import evaluate_resume

resume_text = """
Software Engineer with 6 years of experience in Java,SQL.
Holds a Bachelor's degree in Computer Science.
Worked with MongoDB  databases.
Strong in cloud
Experience with Javascripts,
(Azure/AWS) and Git version control
Practices clean code principles and pair programming occasionally.
Agile scrum
Fluent in oral and written communication in English
"""
# resume_text = extract_text_from_pdf( "E:/Thesis/resume-analyzer/resumes/Md Atiqur Rahman.pdf")
# resume_text = extract_text_from_pdf( "E:/Thesis/resume-analyzer/resumes/Arif Chowdhury.txt")
file_path = "E:/Thesis/resume-analyzer/resumes/Arif Chowdhury.txt"
with open(file_path, "r", encoding="utf-8") as f:
    resume_text = f.read()
job_requirements_str = "{'Experience': ['Full Stack Developer with 3-5 years of experience in C#,VB,SQL'], 'Education': ['Bachelor’s degree in Computer Science'], 'TechnicalSkills': ['Strong in ASP.NET Core, MVC, Web API, MS SQL.', 'Experience with Angular or React for front-end development.', 'Familiarity with cloud platforms (Azure/AWS) and Git version control.'], 'Others': ['Project Management skills on Agile scrum', 'Fluent in oral and written communication in English']}"  
#job_requirements_str = "{'Experience': ['Full Stack Developer with 3 years of experience in C#,SQL']}"  
#job_requirements_str = "{'Education': ['Bachelor’s degree in Computer Science']}"  
#job_requirements_str = "{'TechnicalSkills': ['Strong in ASP.NET Core, MVC, Web API, MS SQL.', 'Experience with Angular or React for front-end development.', 'Familiarity with cloud platforms (Azure/AWS) and Git version control.']}"  
#job_requirements_str = "{'TechnicalSkills': ['Experience with Angular or React for front-end development.']}"  
# job_requirements_str = "{'Others': ['Project Management skills on Agile scrum', 'Fluent in oral and written communication in English']}"  

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
