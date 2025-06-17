import requests
from tqdm import tqdm
from langchain.chat_models import ChatOpenAI
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=openai.api_key, model="gpt-4o-mini")

def check_links(all_links, domain):
    link_status = {}
    print(f"\n🔍 Checking {len(all_links)} links for {domain}...")
    for link in tqdm(all_links, desc=f"Checking Links for {domain}", unit="link"):
        try:
            resp = requests.head(link, allow_redirects=True, timeout=3)
            link_status[link] = resp.status_code < 400
        except Exception:
            link_status[link] = False
    return link_status

def identify_failure_pattern(state):
    all_links = state["all_links"]
    domain = state["domain"]
    all_links_status = check_links(all_links, domain)
    broken = {link: status for link, status in all_links_status.items() if not status}
    print(f"🔎 Failure pattern: {len(broken)} broken links found on domain {domain}")
    anomaly_prompt = f"""
You are an anomaly detection system.

Today's broken links: {list(broken.keys())}

Analyze and describe any unusual failure patterns or spikes.
"""
    anomaly_response = llm.invoke(anomaly_prompt)
    print("Anomaly detection insights:", anomaly_response.content)
    return {
        "input_url": state["input_url"],
        "all_links_status": all_links_status,
        "broken_links": broken
    }