import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_llm_json(prompt):
    """Generic function to call Groq LLaMA3 and force JSON output."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert HR AI. Always return your response in pure JSON format."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    import json
    return json.loads(response.choices[0].message.content)
