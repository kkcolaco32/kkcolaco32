from flask import Flask, render_template, request, Response, session, abort, jsonify, send_from_directory
from your_workflow_runner import run_workflow_with_progress
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a strong secret for production

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/start_scan', methods=['POST'])
def start_scan():
    user_input = request.form.get('url_input', '').strip()
    if not user_input:
        return "No URL provided", 400
    session['current_input'] = user_input
    return '', 204

@app.route('/scan', methods=['GET'])
def scan():
    user_input = session.get('current_input')
    if not user_input:
        return "No scan started", 400

    def event_stream():
        try:
            for msg in run_workflow_with_progress(user_input):
                yield f"data: {msg}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

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

if __name__ == "__main__":
    app.run(debug=True, threaded=True)