

🎯 **Current Features:**

📄 PDF resume parsing using pdfplumber

✅ Keyword extraction using NLTK

✅ TF-IDF Match Score (importance of matched keywords)

🔍 Semantic similarity scoring using SentenceTransformer(contextual relevance)

❌ Keyword Coverage Score (breadth of keyword match)

🎯 Weighted Fit Score

🔢 Fit score combining keyword match and semantic similarity

✅ Batch Resume Analysis

📊 Bar chart comparing Fit Scores

📂 Expandable candidate analysis

✅ Streamlit UI with file uploaders and CSV download

🧠 TF-IDF-based missing keyword prioritization

📥 CSV download of results

🏆 Ranked Candidates by Fit Score


Experienced in C#, VB.NET, and SQL Server.
per_req_weight = 30 / 3 = 10 points


🧠 **Core Features**
1.	**PDF Upload & Parsing**

    •	Extract text from resumes and job descriptions.

    •	Use libraries like pdfplumber, PyMuPDF, or pdfminer.

2.	**Information Extraction**

    •	Identify key sections: skills, experience, education, certifications.

    •	Use NLP models or rule-based parsing.

3.	**Matching & Scoring**

    •	Missing vs Matched: Compare resume content with job requirements.

    •	Similarity Score: Use cosine similarity or embeddings (e.g., Sentence-BERT).

    •	Keyword Match Score: Count and weigh keyword overlaps.

    •	Fit Score: Weighted combination of all scores + heuristics.


4.	**List View UI**

    •	Display candidate name, scores, matched/missing keywords.

    •	Optionally add filters, sorting, and export options.


🛠️ **Tech Stack Suggestions**

- **Backend:** Python (FastAPI or Flask)

- **NLP:** spaCy, NLTK, Hugging Face Transformers

- **Frontend:** React or Vue.js

- **Database:** PostgreSQL or MongoDB

- **Storage:** AWS S3 or local file system for PDFs

✅ **Step 1: Install Python on Windows**
Here’s how:
1.	Go to the official Python website: https://www.python.org/downloads/
2.	Download the latest version for Windows.
3.	Important: During installation, check the box that says:
    
     ✅ Add Python to PATH

4.	Complete the installation.
5.	Verify Installation
After installation, open a new Command Prompt and run:
python –version

🧰 **Recommended Tools to Open and Work with Python Files**
Here are some beginner-friendly options:
1.	VS Code (Visual Studio Code) 
2.	PyCharm
3.	Jupyter Notebook

✅ **Step 2: Create Your Project Folder**

    Folder Structure 
    resume-analyzer/
    │
    ├── resumes/               # Store uploaded PDFs
    ├── job_descriptions/      # Store job description PDFs or text
    ├── src/                   # Python scripts
    │   ├── parser.py          # PDF parsing logic
    │   ├── extractor.py       # NLP extraction
    │   ├── scorer.py          # Matching and scoring
    │   └── main.py            # Entry point
    └── requirements.txt       # List of dependencies

✅ **Step 3: Set Up Your Python Environment**
    
    Open the Terminal in VS Code:

    •	Go to Terminal → New Terminal

Then run:
    
```
python -m venv env
```

```
.\env\Scripts\Activate.ps1
    
streamlit run main.py  
```

✅ **Step 2: Install Required Python Libraries**

Here’s a list of essential libraries and what they’re for:

📄 PDF Parsing

•	pdfplumber – Extract text from PDFs

```
pip install pdfplumber
```
after that that package need to included in requirements
```
pip freeze > requirements.txt

```
🧠 **NLP & Text Processing**

•	nltk – Natural Language Toolkit

•	spacy – Industrial-strength NLP

•	scikit-learn – For similarity scoring

•	transformers – For advanced embeddings (optional)

```
pip install nltk spacy scikit-learn
```

```
pip install transformers sentence-transformers
```

📊 **Data Handling & Display**

•	pandas – For tabular data

•	tabulate – For pretty printing tables in CLI

```
pip install pandas tabulate
```

🌐 **Backend (Optional for Web App)**

•	fastapi – Lightweight web framework

•	uvicorn – ASGI server

```
pip install fastapi uvicorn
```

✅ **Step 3: Download NLP Models**

For spaCy, download the English model:

```
python -m spacy download en_core_web_sm
```

For nltk, download basic datasets:

```
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

**Start Coding**

**Step 1: Extract Text from PDF**

✅ See **parser.py**  in src/ folder


you should see the extracted resume text printed in the terminal.

**Step 2: Extract Keywords from Resume and Job Description**

✅ See **extractor.py** in src/ folder

For do this -

✅ Must Download the Required NLTK Resource

Create a file called download_nltk_data.py and add:
```
import nltk

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')  # This is the one causing the error
```

Then run it in your terminal:

```
python download_nltk_data.py
```

**Step 3: Compare Resume with Job Description**

✅ Inside the  Job Description File you see any txt file or 

Add some sample job requirements like:
```
We are looking for a Software Engineer with experience in Python, Django, REST APIs, and cloud platforms like AWS or Azure. Knowledge of Docker, Kubernetes, and CI/CD pipelines is a plus.
```

🧠 **Step 4: Add Semantic Similarity Using Sentence Embeddings**

We'll use the sentence-transformers library, which is built on top of Hugging Face Transformers and optimized for semantic similarity.

✅ Step-by-Step Guide

1. Install the Library (if not already installed) In your terminal:
```
pip install sentence-transformers
```
✅ See **scorer.py** in src/ folder

✅ Output Example
You’ll now see something like:
```
✅ Matched Keywords: {'python', 'aws', 'django'}
❌ Missing Keywords: {'kubernetes', 'ci', 'cd'}
📊 Keyword Match Score: 60.00%
🔍 Semantic Similarity Score: 78.45%
```
🔢 **Step 5: Combine Scores into a Fit Score**

Let’s now create a Fit Score that combines:

✅ Keyword Match Score

✅ Semantic Similarity Score

🎯 Simple Weighted Formula
You can use a formula like this:

```
fit_score = (0.6 * match_score) + (0.4 * similarity_score)
```
📊 Example Output
```
✅ Keyword Match Score: 60.00%
🔍 Semantic Similarity Score: 35.75%
🏆 Fit Score: 50.35%
```

**Step 5: Batch Resume Analysis + Table + CSV**

1. Make Sure You Have Multiple PDFs

Place multiple resume PDFs inside the resumes/ folder. Example:

✅ Output Example

```
📄 Resume: Jane_Doe.pdf
✅ Keyword Match Score: 70.00%
🔍 Semantic Similarity Score: 82.50%
🏆 Fit Score: 75.50%
❌ Missing Keywords: {'kubernetes', 'ci/cd'}

📄 Resume: John_Smith.pdf
✅ Keyword Match Score: 55.00%
🔍 Semantic Similarity Score: 65.00%
🏆 Fit Score: 59.00%
❌ Missing Keywords: {'aws', 'docker'}
```

**Step 6: Build a simple web interface**

Step 1: Install Streamlit
```
pip install streamlit
```
Step 2: see app.py in Your Project Root

▶️ Step 3: Run the App

```
streamlit run app.py
```
The interface  users can upload a CV and instantly analyze it.

In Streamlit app to:
```
Allow uploading a single resume PDF.
Let the user paste or type the job description directly into a text box.
Show the analysis results immediately after clicking a button.
```

📊 **Bar chart comparing Fit Scores**
```
pip install plotly
```
Now that you’ve got:
```
✅ Multiple resume uploads
📊 Fit Score comparison chart
📂 Expandable candidate analysis
```

📊 **Prioritized Missing Keywords (Based on TF-IDF):**

Integrated **TF-IDF scoring using TensorFlow** to prioritize meaningful missing keywords from the job description.

This will:

- Score each word in the job description based on its importance.
- Filters out words that are not present in the resume but are highly relevant.


To add TF-IDF keyword relevance scoring to your resume analyzer app, follow these steps to integrate it into your existing Streamlit code:

✅ Step-by-Step Integration

1. Import the necessary library

Make sure scikit-learn is installed:
```
pip install scikit-learn
```

Add this to your imports:
```
from sklearn.feature_extraction.text import TfidfVectorizer
```

🔍 **Enhanced Scoring Logic**

We'll calculate a Fit Score using a weighted combination of:

1. **TF-IDF Keyword Match Score**
   
    Measures how many important job description keywords are missing from the resume.

1. **Semantic Similarity Score**

    Uses a transformer model (e.g., SentenceTransformer) to compare the overall meaning of the resume and job description.

1. **Keyword Coverage Score**

    Measures how many job description keywords are present in the resume.

📦 **Required Libraries**
```
pip install streamlit pdfplumber nltk scikit-learn sentence-transformers plotly
```

🏆 **Ranked Candidates by Fit Score**

Ranks candidates by their Fit Score (%) and displays it in a clean table:
```
# 🏆 Ranked Candidates by Fit Score
df_ranked = df.sort_values(by="Fit Score (%)", ascending=False).reset_index(drop=True)
df_ranked.index += 1
df_ranked.index.name = "Rank"

st.subheader("🏆 Ranked Candidates by Fit Score")
st.dataframe(df_ranked)

```
This will:

- Sort candidates by their Fit Score (%) in descending order.
- Assign a rank starting from 1.
- Display the ranked table clearly in your Streamlit UI.

✅ **Included Packages:**

```
streamlit==1.27.0
pandas==2.1.0
pdfplumber==0.5.28
nltk==3.8.1
scikit-learn==1.3.0
sentence-transformers==2.2.2
plotly==5.17.0
gunicorn==21.2.0
streamlit-cloud==0.0.3
```
see also requirement.txt
