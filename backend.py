from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import threading
from pyht import Client
from pyht.client import TTSOptions
import time

# Flask App for Backend
app = Flask(__name__)

# Static folder for audio responses
STATIC_AUDIO_FOLDER = "static/audio_responses"
os.makedirs(STATIC_AUDIO_FOLDER, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PLAYHT_USER_ID = os.getenv("PLAYHT_USER_ID")
PLAYHT_API_KEY = os.getenv("PLAYHT_API_KEY")

if not GEMINI_API_KEY or not PLAYHT_USER_ID or not PLAYHT_API_KEY:
    raise EnvironmentError("Missing required environment variables.")


GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# PlayHT TTS Client Configuration
PLAYHT_CLIENT = Client(
    user_id=PLAYHT_USER_ID,
    api_key=PLAYHT_API_KEY,
)

PLAYHT_OPTIONS = TTSOptions(
    voice="s3://voice-cloning-zero-shot/ab083835-3175-4f26-bc5a-b6a27d0cc4b5/elonmusk-voice/manifest.json"
)

# Cache for generated responses
response_cache = {}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Elon Musk AI Chat Backend",
        "endpoints": {
            "chat": "/chat (POST)",
            "serve_audio": "/static/audio_responses/<filename>"
        }
    })

# Function to fetch response from Gemini API
def get_gemini_response(prompt):
    if prompt in response_cache:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Using cached Gemini response for prompt: {prompt}")
        return response_cache[prompt]

    url = f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": f"You are Elon Musk. Respond concisely in 5-6 lines and in a tone Elon Musk would use. Question: {prompt}"}]}
        ]
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        try:
            response_json = response.json()
            text_response = response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            response_cache[prompt] = text_response
            return text_response
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error parsing Gemini API response: {e}")
            return "Error parsing response from Gemini API."
    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Gemini API Error: {response.status_code}")
        return f"Error fetching response from Gemini API: {response.status_code}"

# Function to generate Elon Musk's voice using PlayHT
def generate_elon_voice(text, filename):
    filepath = os.path.join(STATIC_AUDIO_FOLDER, filename)
    with open(filepath, "wb") as audio_file:
        for chunk in PLAYHT_CLIENT.tts(text, PLAYHT_OPTIONS, voice_engine="PlayDialog-http"):
            audio_file.write(chunk)
    return filepath

# Cache for generated audio responses
audio_cache = {}

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("question", "")
    if not user_input:
        return jsonify({"error": "No question provided."}), 400

    # Generate response from Gemini API
    gemini_response = get_gemini_response(user_input)

    # Check if audio response is already cached
    audio_filename = f"response_audio_{hash(gemini_response)}.wav"
    if gemini_response in audio_cache:
        audio_filepath = audio_cache[gemini_response]
    else:
        # Generate audio response using PlayHT
        audio_filepath = generate_elon_voice(gemini_response, audio_filename)
        audio_cache[gemini_response] = audio_filepath

    return jsonify({
        "text_response": gemini_response,
        "audio_response": f"/static/audio_responses/{audio_filename}"
    })
    
@app.route("/static/audio_responses/<path:filename>")
def serve_audio(filename):
    return send_from_directory(STATIC_AUDIO_FOLDER, filename)

if __name__ == "__main__":
    # Get the PORT environment variable assigned by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
