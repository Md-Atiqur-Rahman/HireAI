### 1.	Add Category

### Like:
```
Softeware Engineer
```
### 2.	Add  Job Requirements

```
Experience Year: 3
```
```
Experience Skills : Net,C#,SQL 
```
#

```
Education: Computer Science
```
```
TechnicalSkills-1: Strong in ASP.NET Core, MVC, Web API.
```
```
TechnicalSkills-2: Experience with Angular or React for front-end development.
```

```
TechnicalSkills-3: Familiarity with cloud platforms (Azure/AWS) and Git version control.
```

```
Others-1: Project Management skills on Agile scrum

```
```
Others-2: Fluent in oral and written communication in English

```
So final out put is like
```
job_requirements = {
    "Experience": [
        "Full Stack Developer with 3 years of experience in C#,VB,SQL"
    ],
    "Education": [
        "Bachelor’s degree in Computer Science"
    ],
    "TechnicalSkills": [
        "Strong in ASP.NET Core, MVC, Web API, MS SQL.",
        "Experience with Angular or React for front-end development.",
        "Familiarity with cloud platforms (Azure/AWS) and Git version control."
    ],
    "Others": [
        "Project Management skills on Agile scrum",
        "Fluent in oral and written communication in English"
    ]
}

```
### 3. Check resume analyze

### Business logic
## Experience Matching Rules: 
```
1. If the user's years of experience are lower than the required experience, it must be shown as Fail.
```
```
2. If the years match but the skills do not match, it must be shown as Fail.
```
```
3. If the Years match but the skills do not match at least 50 percent, it must be shown as Fail.
```
```
4. If a range of years is given and it does not match within that range, then it must also be shown as Fail.
```
```
5. Only if both years and skills match above 50 percent, it will be shown as Pass.
```
## Education Matching Rules:

```
1. If the degree and subject do not match, the status will be marked as 'Missing'. In that case, no score will be given, but it will also not be considered as Fail.
```
```
2. If there are multiple sub-requirements, such as Master's and Bachelor's, then points will be given proportionally based on each sub-requirement.
```

## Technical Skills Matching Rules:
```
1. If the technical skill requirement does not match, that requirement will be marked as Fail.
```

```
Technical Skills Test: 
1. If none of the technical sub-requirements match with the resume, the Technical Skills section will be marked as Fail.
```
```
2. If the skills match less than 50%, the requirement will be marked as Missing.
```
```
3. If there are multiple sub-requirements in Technical Skills, each requirement will be checked individually, and a proportional score will be calculated and added for those that match.If at least one of the sub-requirements matches, it will be considered as Pass.
```
## Other logic Matching Rules:

```
1. If the Others requirements do not match, no score will be added, and it will not be considered as Fail.
```
```
2. If there are sub-requirements, a proportional score will also be added accordingly.
```
```
3. If it does not match at least 50%, it will be marked as Missing.
```
