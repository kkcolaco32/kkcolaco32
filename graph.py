from langgraph.graph import StateGraph
from typing import TypedDict
from agents import (
    chatgpt_interpret_intent as interpret_user_intent,
    crawl_and_extract,
    identify_failure_pattern,
    correlate_events,
    generate_insights,
    report_results
)

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

builder.set_entry_point("interpret_user_intent")

builder.add_edge("interpret_user_intent", "crawl_and_extract")
builder.add_edge("crawl_and_extract", "identify_failure_pattern")
builder.add_edge("identify_failure_pattern", "correlate_events")
builder.add_edge("correlate_events", "generate_insights")
builder.add_edge("generate_insights", "report_results")

graph = builder.compile()
