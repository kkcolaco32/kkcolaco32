import os
import datetime
import webbrowser
import csv
from urllib.parse import urlparse
from fpdf import FPDF

def generate_pdf_report(pdf_file, url, all_links_status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Broken Links Report for {url}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    total = len(all_links_status)
    broken = sum(1 for ok in all_links_status.values() if not ok)
    pdf.cell(200, 10, f"Total Links Checked: {total}", ln=True)
    pdf.cell(200, 10, f"Broken Links Found: {broken}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Broken Links:", ln=True)
    pdf.set_font("Arial", size=12)
    for link, ok in all_links_status.items():
        if not ok:
            pdf.multi_cell(0, 10, link)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Working Links:", ln=True)
    pdf.set_font("Arial", size=12)
    for link, ok in all_links_status.items():
        if ok:
            pdf.multi_cell(0, 10, link)

    pdf.output(pdf_file)

def report_results(state):
    all_links_status = state.get("all_links_status", {})
    url = state.get("input_url", "Unknown URL")

    if url == "test":
        domain = "test"
    else:
        domain = urlparse(url).netloc.split('.')[0]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    base_output_folder = "outputs"
    os.makedirs(base_output_folder, exist_ok=True)

    folder_name = f"{domain}_{timestamp}"
    output_folder = os.path.join(base_output_folder, folder_name)
    os.makedirs(output_folder, exist_ok=True)

    html_filename = os.path.join(output_folder, 'broken_links_report.html')
    txt_filename = os.path.join(output_folder, 'broken_links_report.txt')
    csv_filename = os.path.join(output_folder, 'broken_links_report.csv')
    pdf_filename = os.path.join(output_folder, 'broken_links_report.pdf')

    broken_links = [link for link, ok in all_links_status.items() if not ok]

    if not all_links_status:
        report = f"No links were checked on {url}."
    else:
        report = f"Links checked on {url}:\n" + "\n".join(all_links_status.keys())
        report += f"\n\nBroken links found:\n" + "\n".join(broken_links)

        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(f"Links checked for {url}\n\n")
            for link, ok in all_links_status.items():
                status = "OK" if ok else "BROKEN"
                f.write(f"{link} - {status}\n")

        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Link', 'Status'])
            for link, ok in all_links_status.items():
                writer.writerow([link, "OK" if ok else "BROKEN"])

        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Broken Links Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    padding: 20px;
    background-color: #f9f9f9;
}}
h1 {{ color: #333; }}
table {{
    width: 100%;
    border-collapse: collapse;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}}
th {{
    background-color: #f2f2f2;
}}
.status-ok {{
    color: green;
    font-weight: bold;
}}
.status-broken {{
    color: red;
    font-weight: bold;
}}
</style>
</head>
<body>
<h1>Broken Links Report for {url}</h1>
<p><strong>Total Links Checked:</strong> {len(all_links_status)}</p>
<p><strong>Broken Links Found:</strong> {len(broken_links)}</p>
<table>
<tr><th>Link</th><th>Status</th></tr>
""")
            for link, ok in all_links_status.items():
                status_class = "status-ok" if ok else "status-broken"
                status_text = "OK" if ok else "BROKEN"
                f.write(f"<tr><td><a href='{link}' target='_blank'>{link}</a></td><td class='{status_class}'>{status_text}</td></tr>\n")
            f.write("</table></body></html>")

        generate_pdf_report(pdf_filename, url, all_links_status)

        webbrowser.open(f'file://{os.path.abspath(html_filename)}')

    # --- Agentic Workflow Summary ---
    summary_lines = [
        "\n--- Agentic Workflow Summary ---",
        f"1. Interpret User Intent: {state.get('scan_type', 'N/A')} | Notes: {state.get('notes', '')}",
        f"2. Crawl and Extract: {len(state.get('all_links', []))} links found.",
        f"3. Identify Failure Pattern: {len(broken_links)} broken links detected.",
        f"4. Correlate Events: {len(state.get('correlated_events', {}).get('groups', [])) if state.get('correlated_events') else 0} groups formed.",
        f"5. Generate Insights: {state.get('insights', 'N/A')}",
        f"6. Report Results: Reports generated in TXT, CSV, HTML, PDF."
    ]
    summary = "\n".join(summary_lines)

    # Append summary to TXT report
    with open(txt_filename, 'a', encoding='utf-8') as f:
        f.write(summary)

    # Append summary to HTML report
    with open(html_filename, 'a', encoding='utf-8') as f:
        f.write(f"<h2>Agentic Workflow Summary</h2><ul>")
        for line in summary_lines[1:]:
            f.write(f"<li>{line}</li>")
        f.write("</ul>")

    # Add summary to returned report string
    report += summary

    print(f"\n✅ Scan complete! {len(broken_links)} broken links found out of {len(all_links_status)} checked.")
    print(f"📄 Reports saved inside folder: {output_folder}")

    return {"report": report}