import os
import io
import json
import requests
from flask import Flask, request, Response, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXT = {'png','jpg','jpeg','gif','webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='.', static_url_path='/')
CORS(app)


MODE_PROMPTS = {
    "neutral": "You are a highly knowledgeable AI assistant. Answer questions clearly, concisely, and accurately. Keep tone neutral, friendly, and respectful. Avoid jokes, sarcasm, or emotional language. Focus on clarity and useful information. Provide examples or step-by-step explanations when relevant.",
    "gf": "You are a caring, affectionate AI assistant, responding with warmth and empathy, like a supportive girlfriend. Use sweet and loving language.",
    "professional": "You are a professional AI assistant. Provide clear, concise, and accurate answers. Use formal and polished language suitable for workplace or academic discussions. Structure responses logically, with numbered points or bullet lists where applicable. Avoid jokes, slang, or casual phrases. Be thorough and precise.",
    "funny": "You are a humorous AI assistant, responding with wit and lighthearted jokes to entertain the user."
}

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:7b"  

def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in ALLOWED_EXT

def build_prompt(message, mode):
    """
    Build a system prompt and user prompt for various message types:
    - math solving when message starts with 'solve:' or '/solve'
    - code snippet when message starts with 'CODE_SNIPPET:'
    - regular messages otherwise
    """
    system = MODE_PROMPTS.get(mode, MODE_PROMPTS['neutral'])

    # detect special types
    if message.strip().lower().startswith(('solve:', '/solve')):
        problem = message.split(':', 1)[-1].strip() if ':' in message else message.split(' ',1)[-1].strip()
        user_prompt = f"User asked for a step-by-step mathematical solution. Provide extremely clear, step-by-step reasoning. Use numbered steps, show intermediate calculations, and if helpful include short explanations for why each step is valid. Do not skip steps. Problem: {problem}\n\nAssistant:"
        system = system + " When solving math problems, ALWAYS provide step-by-step reasoning and show intermediate steps clearly. Use numbered steps and explain why."
        return system, user_prompt

    if message.startswith('CODE_SNIPPET:'):
        code = message.split(':',1)[1].strip()
        user_prompt = f"User provided a code snippet. Provide a readable review: point out bugs, suggest improvements, explain what it does, and optionally provide a cleaned-up version if appropriate. Reply with: 1) Short summary 2) Issues/bugs (if any) 3) Recommended improvements 4) Example improved code. Code:\n\n{code}\n\nAssistant:"
        system = system + " When reviewing code, be concise, constructive, and include corrected example code if you recommend changes."
        return system, user_prompt

    # normal conversational message
    user_prompt = f"User: {message}\nAssistant:"
    return system, user_prompt

def ask_ai_stream(prompt_message, mode):
    """
    Streams responses from Ollama. Sends prompts built by build_prompt.
    Yields JSON-lines: {"reply":"..."}\n
    """
    system_prompt, user_prompt = build_prompt(prompt_message, mode)
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": True,
        "options": {"temperature": 0.2, "top_p": 0.9}
    }
    headers = {"Content-Type": "application/json"}

    try:
        with requests.post(OLLAMA_URL, data=json.dumps(payload), headers=headers, stream=True, timeout=60) as resp:
            if not resp.ok:
                yield json.dumps({"reply": f"Ollama error: HTTP {resp.status_code}. Ensure Ollama is running and model pulled."}) + "\n"
                return
            for line in resp.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                    
                        chunk = ""
                        if isinstance(data, dict):
                           
                            chunk = data.get("response") or data.get("output") or data.get("text") or ""
                            
                            if data.get("done", False):
                                break
                        if chunk:
                            yield json.dumps({"reply": chunk}) + "\n"
                    except Exception:
                        
                        try:
                            text = line.decode("utf-8")
                            if text.strip():
                                yield json.dumps({"reply": text}) + "\n"
                        except Exception:
                            continue
    except requests.exceptions.Timeout:
        yield json.dumps({"reply": "Error: Request to Ollama timed out. It may be slow or unresponsive."}) + "\n"
    except Exception as e:
        yield json.dumps({"reply": f"Error: Failed to connect to Ollama at {OLLAMA_URL}. Exception: {str(e)}"}) + "\n"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    message = data.get('message', '')
    mode = data.get('mode', 'neutral')
    if not message.strip():
        return Response(json.dumps({"reply":"Please enter a message."}), mimetype='application/json')

    return Response(ask_ai_stream(message, mode), mimetype='text/plain')

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    f = request.files['image']
    if f.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    if not allowed_file(f.filename):
        return jsonify({'error':'File type not allowed'}), 400

    fname = secure_filename(f.filename)
  
    base, ext = os.path.splitext(fname)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    saved_name = f"{base}_{timestamp}{ext}"
    path = os.path.join(UPLOAD_FOLDER, saved_name)
    f.save(path)

    file_url = f"/{UPLOAD_FOLDER}/{saved_name}"
    return jsonify({'url': file_url})

# serve uploaded images
@app.route(f'/{UPLOAD_FOLDER}/<path:filename>')
def uploaded_file(filename):
    full = os.path.join(UPLOAD_FOLDER)
    if os.path.exists(os.path.join(full, filename)):
        return send_from_directory(full, filename)
    return ("Not found", 404)

@app.route('/<path:filename>')
def static_proxy(filename):
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return ("Not found", 404)

if __name__ == '__main__':
    print("Starting simplified AI Chatbot server on http://0.0.0.0:5000")
    print("Ensure Ollama is running on localhost:11434 and mistral:7b is pulled.")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)