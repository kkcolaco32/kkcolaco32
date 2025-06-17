import os
import json
import re
from langchain.chat_models import ChatOpenAI
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=openai.api_key, model="gpt-4.1")

def chatgpt_interpret_intent(state):
    user_input = state["input_url"].strip()

    # Handle mock test mode explicitly
    if user_input.lower() == "test":
        return {
            "input_url": "test",
            "scan_type": "full_crawl",
            "include_paths": [],
            "exclude_paths": [],
            "notes": "Mock test mode enabled"
        }

    # Proceed with normal AI-driven intent parsing for other inputs
    prompt = f"""
You are a website testing assistant. The user input is:
\"\"\"{user_input}\"\"\"

Extract from this input a JSON object with these fields:
- url: full URL or domain (add https:// and default to .com if missing)
- scan_type: either "homepage_only" or "full_crawl"
- include_paths: list of URL paths to include (empty means include all)
- exclude_paths: list of URL paths to exclude
- notes: any special instructions

Example:
{{
  "url": "https://jiomart.com",
  "scan_type": "full_crawl",
  "include_paths": ["/blog", "/products"],
  "exclude_paths": ["/ads"],
  "notes": "Scan only blog and products, exclude ads"
}}
"""
    response = llm.invoke(prompt)
    text = response.content
    # Remove markdown if any
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)

    try:
        data = json.loads(text)
    except Exception:
        # fallback default completion if AI fails
        if user_input.startswith("http"):
            url = user_input
        else:
            url = f"https://{user_input}.com"
        data = {
            "url": url,
            "scan_type": "full_crawl",
            "include_paths": [],
            "exclude_paths": [],
            "notes": ""
        }

    # Clean URL string
    url = data.get("url", "").strip().strip('"').strip("'").replace(" ", "")
    data["url"] = url

    print(f"🤖 ChatGPT interpreted intent: {data}")

    return {
        "input_url": data.get("url"),
        "scan_type": data.get("scan_type", "full_crawl"),
        "include_paths": data.get("include_paths", []),
        "exclude_paths": data.get("exclude_paths", []),
        "notes": data.get("notes", "")
    }