from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env", override=True)
print(f"DEBUG: OPENAI_API_KEY is set: {bool(os.getenv('OPENAI_API_KEY'))}")

from langgraph.graph import StateGraph
from typing import TypedDict
from agents.chatgpt_intent import chatgpt_interpret_intent as interpret_user_intent
from agents.crawler import crawl_and_extract
from agents.checker import identify_failure_pattern
from agents.correlate_events import correlate_events
from agents.insights import generate_insights
from agents.reporter import report_results

class WorkflowState(TypedDict):
    input_url: str
    scan_type: str
    include_paths: list
    exclude_paths: list
    notes: str
    all_links: list
    domain: str
    all_links_status: dict
    broken_links: dict
    insights: str
    report: str

builder = StateGraph(state_schema=WorkflowState)

builder.add_node("interpret_user_intent", interpret_user_intent)
builder.add_node("crawl_and_extract", crawl_and_extract)
builder.add_node("identify_failure_pattern", identify_failure_pattern)
builder.add_node("correlate_events", correlate_events)
builder.add_node("generate_insights", generate_insights)
builder.add_node("report_results", report_results)

print("[DEBUG] Registered nodes:", builder.nodes.keys())

def next_step(state):
    if 'input_url' not in state or not state['input_url']:
        return 'interpret_user_intent'
    if 'all_links' not in state or not state['all_links']:
        return 'crawl_and_extract'
    if 'broken_links' not in state:
        return 'identify_failure_pattern'
    if 'insights' not in state:
        return 'generate_insights'
    # Always route to report_results as the final step
    return 'report_results'

builder.set_entry_point("interpret_user_intent")

builder.add_conditional_edges("interpret_user_intent", next_step, [
    "crawl_and_extract",
    "identify_failure_pattern",
    "generate_insights",
    "report_results"
])
builder.add_conditional_edges("crawl_and_extract", next_step, [
    "identify_failure_pattern",
    "generate_insights",
    "report_results"
])
builder.add_conditional_edges("identify_failure_pattern", next_step, [
    "correlate_events",
    "generate_insights",
    "report_results"
])
builder.add_conditional_edges("correlate_events", next_step, [
    "generate_insights",
    "report_results"
])
builder.add_conditional_edges("generate_insights", next_step, [
    "report_results"
])
# No outgoing edge from report_results; workflow ends

graph = builder.compile()
