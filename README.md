# AI Chatbot Server

This is a simple Flask-based backend server for an AI chatbot application. It integrates with [Ollama](https://ollama.com/) (a local AI model runner) to generate responses using the Mistral 7B model. The chatbot supports different response modes (neutral, girlfriend-like, professional, funny), special handling for math problems (prefix with `solve:` or `/solve`), code snippet reviews (prefix with `CODE_SNIPPET:`), and image uploads.

The frontend is a static HTML/JS file (e.g., `index.html`) served by the server, which handles chat interactions, mode selection, coding canvas, and image uploads via AJAX.

## Features
- **Chat Endpoint**: Streams AI responses from Ollama based on user messages and selected mode.
- **Modes**: Custom system prompts for different tones (neutral, caring/gf, professional, funny).
- **Special Handlers**:
  - Math solving with step-by-step explanations.
  - Code review with summaries, bug fixes, and improvements.
- **Image Uploads**: Allows uploading images (PNG, JPG, etc.) and serves them back.
- **CORS Support**: Enabled for cross-origin requests (useful for local development).
- **Static File Serving**: Serves the frontend HTML and any other static files.

## Prerequisites
- Python 3.8+ installed.
- [Ollama](https://ollama.com/) installed and running on `localhost:11434`.
- Pull the Mistral 7B model in Ollama: Run `ollama pull mistral:7b` in your terminal.

## Installation
1. Clone or download the repository.
2. Create a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install dependencies:
4. Ensure the `uploads` folder is created (the code handles this automatically).

## Running the Server
1. Start Ollama in a separate terminal/window: `ollama serve`.
2. Run the Flask app:
3. Open the frontend in your browser: `http://localhost:5000/` (or `http://0.0.0.0:5000` if accessing from another device).

The server runs on port 5000 by default with debug mode enabled. For production, set `debug=False` and consider using a WSGI server like Gunicorn.

## Usage
- **Chat**: Send POST requests to `/chat` with JSON body `{ "message": "Your query", "mode": "neutral" }`. Responses are streamed as JSON lines.
- **Image Upload**: POST to `/upload-image` with form-data including the `image` file. Returns JSON with the uploaded file URL.
- **Frontend Integration**: The provided `index.html` (from previous code) handles UI interactions, including mode selection, message sending, code canvas, and image uploads.

## Configuration
- **Ollama URL/Model**: Change `OLLAMA_URL` and `OLLAMA_MODEL` in the code if using a different setup.
- **Upload Folder**: Configured as `uploads/`; stores images with timestamped filenames for uniqueness.
- **Allowed Extensions**: Limited to images (PNG, JPG, JPEG, GIF, WEBP).

## Troubleshooting
- **Ollama Errors**: Ensure Ollama is running and the model is pulled. Check the Ollama logs for issues.
- **Timeout/Connection Issues**: Increase the timeout in the `requests.post` call if Ollama is slow.
- **CORS Issues**: Already enabled, but verify if your frontend origin matches.
- **File Not Found**: Ensure `index.html` and other static files are in the root directory.

## License
This project is open-source under the MIT License.

## Contributing
Feel free to fork and submit pull requests for improvements!