from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

def correlate_events(state):
    """
    Groups broken links by failure type (status code if available), time (if available), and metadata (domain/path).
    Adds a 'correlated_events' key to the state with grouped results.
    """
    broken_links = state.get("broken_links", {})
    all_links_status = state.get("all_links_status", {})
    domain = state.get("domain") or urlparse(state.get("input_url", "")).netloc
    
    # Group by status code (if available), domain, and path
    grouped = defaultdict(list)
    for link in broken_links:
        # Try to extract status code if present in all_links_status
        status = all_links_status.get(link, False)
        # Use status code or 'unknown'
        status_code = status if isinstance(status, int) else 'unknown'
        parsed = urlparse(link)
        group_key = (status_code, parsed.netloc, parsed.path)
        grouped[group_key].append(link)
    
    # Optionally, add a timestamp (now)
    timestamp = datetime.now().isoformat()
    correlated = {
        "timestamp": timestamp,
        "groups": [
            {
                "status_code": k[0],
                "domain": k[1],
                "path": k[2],
                "links": v
            } for k, v in grouped.items()
        ]
    }
    state["correlated_events"] = correlated
    print(f"🧩 Correlated Events: {len(correlated['groups'])} groups found.")
    return state
