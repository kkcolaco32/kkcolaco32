import os
import json
import re
from langchain.chat_models import ChatOpenAI
import openai
import time

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

    def extract_intent(prompt):
        response = llm.invoke(prompt)
        text = response.content
        text = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
        try:
            data = json.loads(text)
        except Exception:
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
        return data, text

    base_prompt = f"""
You are a website testing assistant. The user input is:
\"\"\"{user_input}\"\"\"

Extract from this input a JSON object with these fields:
- url: full URL or domain (add https:// and default to .com if missing)
- scan_type: either \"homepage_only\" or \"full_crawl\"
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

    max_retries = 2
    for attempt in range(max_retries + 1):
        data, raw_text = extract_intent(base_prompt)
        # Clean URL string
        url = data.get("url", "").strip().strip('"').strip("'").replace(" ", "")
        data["url"] = url

        # Validation step: ask AI to check if the output is valid and provide reasoning
        validation_prompt = f"""
You are an expert validator. Given the user input: \"{user_input}\" and the extracted JSON: {json.dumps(data)}
Does the JSON correctly and completely capture the user's intent? Reply with 'YES' or 'NO' and a short reasoning.
"""
        validation_response = llm.invoke(validation_prompt)
        validation_text = validation_response.content.strip()
        print(f"Validation attempt {attempt+1}: {validation_text}")
        if validation_text.lower().startswith("yes"):
            print(f"🤖 ChatGPT interpreted intent: {data}")
            return {
                "input_url": data.get("url"),
                "scan_type": data.get("scan_type", "full_crawl"),
                "include_paths": data.get("include_paths", []),
                "exclude_paths": data.get("exclude_paths", []),
                "notes": data.get("notes", "") + f"\nValidation: {validation_text}"
            }
        else:
            # Optionally, modify the prompt for the next attempt
            base_prompt += f"\n# Previous output was not satisfactory. Reason: {validation_text}\nPlease try again."
            time.sleep(1)  # avoid rate limits

    # If all retries fail, return the last data with validation reasoning
    print(f"🤖 ChatGPT interpreted intent (after retries): {data}")
    return {
        "input_url": data.get("url"),
        "scan_type": data.get("scan_type", "full_crawl"),
        "include_paths": data.get("include_paths", []),
        "exclude_paths": data.get("exclude_paths", []),
        "notes": data.get("notes", "") + f"\nValidation: {validation_text} (after retries)"
    }