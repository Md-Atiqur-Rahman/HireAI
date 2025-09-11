from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()  # ✅ This loads the .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # ✅ This fetches the key

