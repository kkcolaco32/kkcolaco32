from urllib.parse import urlparse
from langchain_openai import ChatOpenAI
import os

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini")

def generate_insights(state):
    broken_links = state.get("broken_links", {})
    domain = urlparse(state["input_url"]).netloc.split('.')[0]

    total_links = len(state.get("all_links_status", {}))
    broken_count = len(broken_links)

    base_insights = []
    if broken_count == 0:
        base_insights.append(f"🎉 No broken links detected on {domain}. Website health looks good!")
    else:
        base_insights.append(f"⚠️ Found {broken_count} broken links out of {total_links} checked on {domain}.")
        base_insights.append("🔧 Recommend checking the listed URLs and fixing or redirecting them.")

    anomaly_prompt = f"""
You are an anomaly detection system.

Today's broken links: {list(broken_links.keys())}

Analyze and describe any unusual failure patterns or spikes.
"""
    anomaly_response = llm.invoke(anomaly_prompt)

    root_cause_prompt = f"""
Given these broken links:

{list(broken_links.keys())}

Suggest possible root causes for these failures.
"""
    root_cause_response = llm.invoke(root_cause_prompt)

    state["insights"] = "\n\n".join(base_insights)
    state["detailed_analysis"] = anomaly_response.content.strip() + "\n\n" + root_cause_response.content.strip()
    return state