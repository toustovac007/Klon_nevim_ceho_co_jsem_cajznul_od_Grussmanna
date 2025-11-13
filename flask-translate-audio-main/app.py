import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

# Load configuration from environment (with defaults from .env)
TRANSCRIBE_API_URL = os.environ.get("TRANSCRIBE_API_URL", "https://aivoice.sspu-opava.cz")
TRANSCRIBE_ENDPOINT = os.environ.get('TRANSCRIBE_ENDPOINT', '/inference')
MANUAL_URL = os.environ.get("TRANSCRIBE_API_MANUAL", "http://192.168.22.141:9010")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), os.environ.get('UPLOAD_DIR', 'uploads'))
# If KEEP_UPLOADS is true, uploaded files are kept after forwarding; otherwise they are removed
KEEP_UPLOADS = os.environ.get('KEEP_UPLOADS', '0').lower() in ('1', 'true', 'yes')

# ensure upload dir exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # uploaded file
        file = request.files.get('file')
        language = request.form.get('language', 'en')
        temperature = request.form.get('temperature', '0.0')

        # Validate language and temperature
        allowed_langs = {'en', 'cz'}
        if language not in allowed_langs:
            flash(f'Invalid language: {language}', 'error')
            return redirect(url_for('upload'))

        try:
            temperature = float(temperature)
        except (TypeError, ValueError):
            flash('Temperature must be a number between 0.0 and 1.0', 'error')
            return redirect(url_for('upload'))

        if not (0.0 <= temperature <= 1.0):
            flash('Temperature must be between 0.0 and 1.0', 'error')
            return redirect(url_for('upload'))

        if not file:
            flash('No file uploaded', 'error')
            return redirect(url_for('upload'))

        # Save uploaded file to uploads/ with secure filename
        filename = secure_filename(file.filename)
        saved_path = os.path.join(UPLOAD_DIR, filename)
        file.save(saved_path)

        # Open saved file and forward to transcription API
        data = {'language': language, 'temperature': str(temperature)}
        try:
                with open(saved_path, 'rb') as fh:
                    files = {'file': (filename, fh, file.mimetype)}
                    target_url = TRANSCRIBE_API_URL.rstrip('/') + TRANSCRIBE_ENDPOINT
                    resp = requests.post(
                        target_url,
                        files=files,
                        data=data,
                        timeout=360,
                    )
        except requests.RequestException as e:
            flash(f'Error contacting transcription API: {e}', 'error')
            return redirect(url_for('upload'))

        if resp.status_code != 200:
            if resp.status_code == 404:
                flash(f'Transcription API returned 404 Not Found for {target_url}. Check TRANSCRIBE_ENDPOINT or the API server.', 'error')
            else:
                flash(f'Transcription API returned {resp.status_code}: {resp.text}', 'error')
            return redirect(url_for('upload'))

        # Expect API to return JSON with 'text' field
        try:
            result = resp.json()
            text = result.get('text') if isinstance(result, dict) else None
        except ValueError:
            text = None

        if text is None:
            flash('Transcription API did not return text', 'error')
            # optionally keep file for debugging
            return redirect(url_for('upload'))

        # cleanup uploaded file unless configured to keep
        if not KEEP_UPLOADS:
            try:
                os.remove(saved_path)
            except Exception:
                pass

        return render_template('result.html', text=text)

    # GET
    return render_template('upload.html')

@app.context_processor
def inject_config():
    # make useful urls available in templates
    full_target = TRANSCRIBE_API_URL.rstrip('/') + TRANSCRIBE_ENDPOINT
    return dict(TRANSCRIBE_API_URL=TRANSCRIBE_API_URL, TRANSCRIBE_API_MANUAL=MANUAL_URL, TRANSCRIBE_TARGET_URL=full_target)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
