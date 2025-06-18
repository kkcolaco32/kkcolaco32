from dotenv import load_dotenv
load_dotenv()
from graph import graph

def main():
    url = input("Enter a URL or domain to scan (or 'test' for mock): ").strip()
    try:
        result = graph.invoke({"input_url": url})
        print("\nScan complete. Summary:")
        print(result.get("report", "No report generated"))
    except Exception as e:
        print(f"Error during scan: {e}")

if __name__ == "__main__":
    main()