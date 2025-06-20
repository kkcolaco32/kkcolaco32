from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env", override=True)
print(f"DEBUG: OPENAI_API_KEY is set: {bool(os.getenv('OPENAI_API_KEY'))}")

LOCK_FILE = 'scan.lock'
from graph import graph

def main():
    if os.path.exists(LOCK_FILE):
        print('A scan is already in progress. Please wait for it to finish.')
        return
    try:
        open(LOCK_FILE, 'w').close()
        url = input("Enter a URL or domain to scan (or 'test' for mock): ").strip()
        initial_state = {
            "input_url": url,
            "scan_type": "",  # will be set by interpret_user_intent
            "include_paths": [],
            "exclude_paths": [],
            "notes": "",
            "all_links": [],
            "domain": "",
            "all_links_status": {},
            "broken_links": {},
            "insights": "",
            "report": ""
        }
        print(f"[DEBUG] Initial state: {initial_state}")
        result = graph.invoke(initial_state)
        print(f"[DEBUG] Result from graph.invoke: {result}")
        print("\nScan complete. Summary:")
        print(result.get("report", "No report generated"))
    except Exception as e:
        print(f"Error during scan: {e}")
    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

if __name__ == "__main__":
    main()