# 🔗 Automated Broken Link Detection & Reporting Tool

An AI-powered broken link scanner built with LangGraph and Python, designed to help engineering teams streamline website quality assurance.

## 🚀 Features

- **Smart URL Completion:** Automatically completes domain inputs with common TLDs (.com, .ai, .org, etc.) by verifying reachability.
- **Full Website Crawl:** Recursively scans all pages within the same domain up to a configurable limit (default 50 pages).
- **Link Validation:** Checks all extracted links using HTTP HEAD requests to identify broken links (status codes 4xx, 5xx).
- **Detailed Reporting:** Generates reports in multiple formats:
  - Plain text (`.txt`)
  - CSV (`.csv`)
  - Styled HTML (`.html`, auto-opens in browser)
  - PDF (`.pdf`) with clear broken vs working links.
- **Organized Outputs:** Reports saved inside timestamped folders under `outputs/` for easy management.
- **Progress Feedback:** Real-time progress bar during link validation for user visibility.
- **Mock Mode:** Use input `test` to simulate scans with sample data for quick demos or testing.
- **ChatGPT Integration:** AI-powered user intent interpretation for dynamic scan configuration.

## 📋 Requirements

- Python 3.8+

## Installation

pip3 install -r requirements.txt

## Usage

Before running, copy `.env.example` to `.env` and add your OpenAI API key:

```sh
cp .env.example .env
# Then edit .env and set your OPENAI_API_KEY
```

Run the scanner:

python3 main.py

Enter a domain or full URL to scan (e.g., jiomart, https://ratl.ai), or enter test for mock data.

## Example:

Enter a URL or domain to scan (or 'test' for mock): jiomart
🤖 Auto-completing to: https://jiomart.com

🔍 Checking links for jiomart...
Checking Links for jiomart: 100%|██████████| 45/45 [00:20<00:00, 2.2 link/s]

✅ Scan complete! 3 broken links found out of 45 checked.
📄 Reports saved inside folder: outputs/jiomart_20250609_153000

📂 Folder Structure
 
ai-broken-link-detector/
├── agents/                # Modular agent nodes and logic
│   ├── chatgpt_intent.py
│   ├── crawler.py
│   ├── checker.py
│   ├── insights.py
│   ├── reporter.py
│   └── __init__.py
├── workflow_graph.py      # LangGraph DAG definition
├── main.py                # Entry point for running scans
├── requirements.txt       # Python dependencies
├── README.md              # This documentation
├── run_tests.py           # Script to run tests and coverage
├── outputs/               # Scan reports organized by domain and timestamp
├── sample_reports/        # Example scan reports for demos
├── tests/                 # Unit tests
├── htmlcov/               # Coverage reports
└── venv/                  # Python virtual environment (excluded from git)

## 🗺️ Workflow DAG (Agentic Steps)

```
[Interpret User Intent]
        |
[Crawl and Extract]
        |
[Identify Failure Pattern]
        |
[Correlate Events]
        |
[Generate Insights]
        |
[Report Results]
```

| Node Name                | Agentic Step                | Description                                                      |
|--------------------------|-----------------------------|------------------------------------------------------------------|
| interpret_user_intent    | Interpret User Intent       | Understands user input and configures scan parameters            |
| crawl_and_extract        | Select Relevant Logs        | Crawls site, extracts all links                                  |
| identify_failure_pattern | Identify Failure Pattern    | Checks links, finds broken ones, detects failure patterns        |
| correlate_events         | Correlate Events            | Groups failures by type/time/metadata for deeper analysis        |
| generate_insights        | Generate Insights, Detect Anomalies, Hypothesize Root Cause | Produces insights, anomaly detection, root cause hypotheses |
| report_results           | Report Output               | Generates and saves reports in multiple formats                  |

🧪 Testing

Run tests with:

python3 run_tests.py

🤝 Contribution
Feel free to open issues or pull requests to improve this tool.

📧 Contact
For questions or feedback, contact: kevincolacogofynd.com

Thank you for using this tool to improve your website quality! 🚀



