from dotenv import load_dotenv
load_dotenv()
import os
print(f"DEBUG: OPENAI_API_KEY is set: {bool(os.getenv('OPENAI_API_KEY'))}")

from flask import Flask, render_template, request, Response, session, abort, jsonify, send_from_directory
from your_workflow_runner import run_workflow_with_progress
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a strong secret for production

LOCK_FILE = 'scan.lock'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/start_scan', methods=['POST'])
def start_scan():
    if os.path.exists(LOCK_FILE):
        return "A scan is already in progress. Please wait for it to finish.", 409
    user_input = request.form.get('url_input', '').strip()
    if not user_input:
        return "No URL provided", 400
    session['current_input'] = user_input
    return '', 204

@app.route('/scan', methods=['GET'])
def scan():
    if os.path.exists(LOCK_FILE):
        return "A scan is already in progress. Please wait for it to finish.", 409
    user_input = session.get('current_input')
    if not user_input:
        return "No scan started", 400

    def event_stream():
        try:
            open(LOCK_FILE, 'w').close()
            for msg in run_workflow_with_progress(user_input):
                yield f"data: {msg}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
        finally:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/reports', methods=['GET'])
def list_reports():
    reports_dir = os.path.abspath('outputs')
    try:
        folders = [f for f in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, f))]
        folders.sort(reverse=True)
        return jsonify(folders)
    except Exception as e:
        print(f"Error listing reports: {e}")
        return jsonify([]), 500

@app.route('/outputs/<path:filename>')
def serve_reports(filename):
    reports_dir = os.path.abspath('outputs')
    file_path = os.path.join(reports_dir, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(reports_dir, filename)

@app.route('/schedule_scan', methods=['POST'])
def schedule_scan():
    domain = request.form.get('schedule_domain', '').strip() or 'test'
    time_str = request.form.get('schedule_time', '15:00')
    frequency = request.form.get('schedule_frequency', 'daily')
    # Save schedule config to a file for the scheduler to pick up
    config = {
        'domain': domain,
        'time': time_str,
        'frequency': frequency
    }
    import json
    with open('schedule_config.json', 'w') as f:
        json.dump(config, f)
    return jsonify({'status': 'scheduled', 'config': config})

@app.route('/latest_report_files', methods=['GET'])
def latest_report_files():
    base_dir = os.path.abspath('outputs')
    # List all subfolders in outputs/
    subfolders = [
        os.path.join(base_dir, name)
        for name in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, name))
    ]
    if not subfolders:
        return jsonify({"error": "No reports available for download."}), 404
    # Sort by modification time, newest last
    latest_folder = max(subfolders, key=os.path.getmtime)
    expected_files = [
        "broken_links_report.html",
        "broken_links_report.pdf",
        "broken_links_report.csv",
        "broken_links_report.txt"
    ]
    files = {}
    for fname in expected_files:
        fpath = os.path.join(latest_folder, fname)
        if os.path.exists(fpath):
            # Return relative path for frontend download links
            rel_path = os.path.relpath(fpath, base_dir)
            files[fname] = f"/outputs/{rel_path}"
    if not files:
        return jsonify({"error": "No reports available for download."}), 404
    return jsonify({"folder": os.path.basename(latest_folder), "files": files})

if __name__ == "__main__":
    app.run(debug=True, threaded=True)