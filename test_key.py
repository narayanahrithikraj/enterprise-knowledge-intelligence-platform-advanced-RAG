import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")

print(f"Testing Key: {key[:6]}...")
genai.configure(api_key=key)

try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Connection Test: Reply with the word 'Success'.")
    print(f"🚀 {response.text.strip()}")
except Exception as e:
    print(f"❌ Google Gateway Rejected this key! Reason:\n{e}")
