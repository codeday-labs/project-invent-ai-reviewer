import os
import subprocess
import base64
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)

    try:
        content = []

        if ext in ('.png', '.jpg', '.jpeg'):
            media_type = 'image/png' if ext == '.png' else 'image/jpeg'
            with open(filepath, 'rb') as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            content = [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
                {"type": "text", "text": "Review this presentation slide. Give feedback on clarity, design, and messaging."}
            ]

        elif ext == '.pdf':
            with open(filepath, 'rb') as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            content = [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}},
                {"type": "text", "text": "Review this presentation. Give feedback on clarity, design, and messaging for each slide."}
            ]

        elif ext == '.pptx':
            # Convert pptx -> pdf using LibreOffice headless
            subprocess.run(
                ["soffice", "--headless", "--convert-to", "pdf", "--outdir", UPLOAD_DIR, filepath],
                check=True, capture_output=True
            )
            pdf_path = os.path.splitext(filepath)[0] + ".pdf"
            with open(pdf_path, 'rb') as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            content = [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}},
                {"type": "text", "text": "Review this presentation. Give feedback on clarity, design, and messaging for each slide."}
            ]
            os.remove(pdf_path)

        else:
            return jsonify({"error": "Unsupported file type"}), 415

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": content}]
        )

        return jsonify({"feedback": response.content[0].text})

    except subprocess.CalledProcessError:
        return jsonify({"error": "PPTX conversion failed. Is LibreOffice installed?"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Something went wrong evaluating the file."}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True, port=3000)