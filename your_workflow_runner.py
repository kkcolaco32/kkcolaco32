from agents import (
    chatgpt_interpret_intent,
    crawl_and_extract,
    identify_failure_pattern,
    generate_insights,
    report_results,
)

def run_workflow_with_progress(url):
    yield "Starting workflow"
    state = {"input_url": url}

    yield "Interpreting user intent"
    state.update(chatgpt_interpret_intent(state))

    yield "Crawling and extracting links"
    state.update(crawl_and_extract(state))

    yield "Identifying failure pattern"
    state.update(identify_failure_pattern(state))

    yield "Generating insights"
    for insight_part in generate_insights(state):
        yield "AI Summary: " + insight_part

    yield "Generating report"
    state.update(report_results(state))

    yield "Workflow completed"
    yield state.get("report", "No report generated")