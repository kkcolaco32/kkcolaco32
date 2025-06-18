import os
import datetime
import csv
from urllib.parse import urlparse
from fpdf import FPDF
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

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

        # Upload HTML report to GCS and get public URL
        gcs_bucket = os.getenv('GCS_BUCKET')
        html_report_url = None
        if gcs_bucket:
            gcs_key = os.path.join(f"broken-link-reports/{os.path.basename(output_folder)}", os.path.basename(html_filename))
            html_report_url = upload_to_gcs(html_filename, gcs_bucket, gcs_key)
        if not html_report_url:
            html_report_url = f"file://{os.path.abspath(html_filename)}"

        domain = urlparse(url).netloc or url
        # Gmail config (fixed sender/recipient/subject)
        gmail_user = 'kevincolaco@gofynd.com'
        gmail_pass = os.getenv('GMAIL_PASS')
        gmail_to = 'bhuvaneshkachave@gofynd.com'
        subject = 'AI-powered Broken Link Detector Report'
        summary = f"Broken Link Report for {url}\nTotal: {len(all_links_status)} | Broken: {len(broken_links)}"

        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if slack_webhook:
            send_slack_notification(slack_webhook, html_report_url, domain)
        if gmail_user and gmail_pass and gmail_to:
            send_gmail_report(gmail_user, gmail_pass, gmail_to, subject, summary, [txt_filename, csv_filename, pdf_filename])

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

def upload_to_gcs(file_path, bucket_name, object_name=None):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    if object_name is None:
        object_name = os.path.basename(file_path)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(file_path, content_type='text/html')
    # Do not call blob.make_public() if uniform bucket-level access is enabled
    return blob.public_url

def send_slack_notification(webhook_url, html_report_url, domain):
    # Map known domains to Slack emoji logos
    domain_logos = {
        'jiomart': ':jiomart:',
        'ratl': ':ratl:',
        'tirabeauty': ':tirabeauty:',
        'fynd': ':fynd:',
        'test': ':test:',
        # Add more domain:emoji mappings as needed
    }
    domain_key = domain.lower().split('.')[0]
    logo = domain_logos.get(domain_key, '')
    if logo:
        domain_display = f"{domain} {logo}"
    else:
        domain_display = domain
    message = (
        f"*Domain:* {domain_display}\n"
        f"*Report Link:* <{html_report_url}|Tap Me :tapme:>"
    )
    payload = {"text": message}
    requests.post(webhook_url, json=payload)

def send_gmail_report(sender_email, sender_password, recipient_email, subject, body, attachments=None):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    attachments = attachments or []
    for file_path in attachments:
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)