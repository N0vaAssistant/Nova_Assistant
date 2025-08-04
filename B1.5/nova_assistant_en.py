import speech_recognition as sr
import requests
import pygame
import os
import subprocess
import pyautogui
from groq import Groq
from flask import Flask, request, jsonify, render_template_string, Response
import threading
import time
import queue
import logging
import tempfile # New import

# --- GLOBAL CONFIGURATION ---
# These variables will be read from environment variables for security
print(" ▄▄    ▄ ▄▄▄▄▄▄▄ ▄▄   ▄▄ ▄▄▄▄▄▄▄ ")
time.sleep(0.1)
print("█  █  █ █       █  █ █  █       █")
time.sleep(0.1)
print("█   █▄█ █   ▄   █  █▄█  █   ▄   █")
time.sleep(0.1)
print("█       █  █ █  █       █  █▄█  █")
time.sleep(0.1)
print("█  ▄    █  █▄█  █       █       █")
time.sleep(0.1)
print("█ █ █   █       ██     ██   ▄   █")
time.sleep(0.1)
print("█▄█  █▄▄█▄▄▄▄▄▄▄█ █▄▄▄█ █▄▄█ █▄▄█")
time.sleep(0.1)
print("GNU GENERAL PUBLIC LICENSE v3")
time.sleep(0.3)
print("--------------------------")
time.sleep(0.2)
print("By using this software, you agree to the TERMS OF USE.")
time.sleep(0.1)
print("Please read the CONDITIONS.txt file located next to this executable.")
time.sleep(0.1)
print("--------------------------")

HOTWORD = os.getenv("NOVA_HOTWORD", "nova")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL") # Default ElevenLabs voice

# --- INITIALIZATION ---
app = Flask(__name__)
recognizer = sr.Recognizer()
groq_client = None
current_mode = "normal" # Default mode
conversation_history = [] # To maintain conversation context
audio_queue = queue.Queue() # Queue for audio playback

# Initialize Pygame Mixer for audio playback
pygame.mixer.init()

# Disable Flask logs to avoid cluttering the assistant's console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def init_groq_client():
    global groq_client
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
    else:
        print("GROQ_API_KEY not configured. AI functions will not be available.")

init_groq_client()

# --- TEXT-TO-SPEECH (TTS) ---
def text_to_speech(text):
    if not ELEVEN_API_KEY:
        print("ELEVENLABS_API_KEY not configured. Text-to-speech is disabled.")
        print("Nova (text):", text)
        return
    print("Nova:", text)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.75
        },
        "model_id": "eleven_multilingual_v2" # Recommended multilingual model
    }
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status() # Raise an exception for HTTP error codes
        if not response.content:
            print("Empty audio response from ElevenLabs.")
            return
        # Use a queue for non-blocking audio playback
        audio_queue.put(response.content)
    except requests.exceptions.RequestException as e:
        print(f"TTS Error (request): {e}")
    except Exception as e:
        print(f"Unexpected TTS error: {e}")

def audio_playback_thread():
    while True:
        if not audio_queue.empty():
            audio_content = audio_queue.get()
            temp_file_path = None # Initialize temporary file path
            try:
                # Create a temporary file that will be automatically deleted upon closing
                # delete=False to be able to load it with pygame, then delete it manually
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                    temp_audio_file.write(audio_content)
                    temp_file_path = temp_audio_file.name # Get the file path
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10) # Limit the loop to not consume too much CPU
                pygame.mixer.music.stop()
                pygame.mixer.music.unload() # Explicitly unload music to release the file
                # Give the operating system a short moment to release the file handle
                time.sleep(0.1)
                # Attempt to delete the temporary file
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Audio playback or file deletion error: {e}")
                if temp_file_path and os.path.exists(temp_file_path):
                    print(f"Could not delete temporary file: {temp_file_path}. Please delete it manually if necessary.")
            finally:
                audio_queue.task_done()
        time.sleep(0.1) # Small pause to avoid too fast a loop

# Start the audio playback thread
threading.Thread(target=audio_playback_thread, daemon=True).start()

# --- SPEECH-TO-TEXT (STT) ---
def listen_for_speech():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source) # Adjust for ambient noise
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5) # Limit listening time
            text = recognizer.recognize_google(audio, language="en-US") # Changed to en-US for English
        print("You said:", text)
        return text.lower()
    except sr.WaitTimeoutError:
        # print("No speech detected.")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Google Speech Recognition service error; {e}")
        return ""
    except Exception as e:
        print(f"Unexpected microphone error: {e}")
        return ""

# --- AI INTERACTION (GROQ) ---
def get_system_prompt(mode: str):
    base_prompt = "You are Nova, a voice assistant created by a young French developer named Guylann. The first version dates from 08/01/25. You are on Windows and the person in front of you is probably disabled."
    if mode == "rapide": # Keeping "rapide" as it's a mode name, but translating its description
        return "You are Nova, a concise and direct voice assistant. Respond briefly and precisely, straight to the point. You are on Windows and the person in front of you is probably disabled."
    elif mode == "histoire": # Keeping "histoire" as it's a mode name, but translating its description
        return "You are Nova, a very talkative voice assistant who loves to tell anecdotes and extra details. Talk a lot and enrich your answers. You are on Windows and the person in front of you is probably disabled."
    else: # normal
        return base_prompt

def get_ai_response(prompt):
    if not groq_client:
        return "I cannot connect to the artificial intelligence service because the Groq API key is not configured."
    global conversation_history
    conversation_history.append({"role": "user", "content": prompt})
    messages = [{"role": "system", "content": get_system_prompt(current_mode)}] + conversation_history
    try:
        chat_completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        ai_response = chat_completion.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        print(f"AI Error: {e}")
        return "I am encountering a problem with the artificial intelligence server."

# --- SYSTEM ACTIONS ---
def execute_system_action(command: str):
    command_lower = command.lower()
    if "open" in command_lower:
        app_name = command_lower.replace("open", "").strip()
        if "chrome" in app_name:
            text_to_speech("Opening Google Chrome.")
            subprocess.Popen(["start", "chrome"], shell=True) # For Windows
            return True
        elif "firefox" in app_name:
            text_to_speech("Opening Mozilla Firefox.")
            subprocess.Popen(["start", "firefox"], shell=True) # For Windows
            return True
        elif "notepad" in app_name or "bloc-notes" in app_name: # Keeping "bloc-notes" as a possible French input
            text_to_speech("Opening Notepad.")
            subprocess.Popen(["notepad.exe"])
            return True
        elif "calculator" in app_name:
            text_to_speech("Opening the calculator.")
            subprocess.Popen(["calc.exe"])
            return True
        # Add other applications here
        else:
            text_to_speech(f"I don't know how to open {app_name}.")
            return False
    elif "write" in command_lower:
        text_to_type = command_lower.replace("write", "").strip()
        if text_to_type:
            text_to_speech(f"Writing: {text_to_type}")
            pyautogui.write(text_to_type)
            return True
        else:
            text_to_speech("What do you want me to write?")
            return False
    elif "search" in command_lower and ("google" in command_lower or "web" in command_lower):
        query = command_lower.replace("search on google", "").replace("search on the web", "").strip()
        if query:
            text_to_speech(f"Searching for {query} on Google.")
            subprocess.Popen(["start", f"https://www.google.com/search?q={query}"], shell=True)
            return True
        else:
            text_to_speech("What do you want me to search for?")
            return False
    elif "settings" in command_lower or "parameter" in command_lower: # Keeping "parameter" as a possible French input
        text_to_speech("Opening the configuration interface.")
        subprocess.Popen(["start", "http://127.0.0.1:5000"], shell=True) # Opens the web interface URL
        return True
    return False # No recognized system action

# --- EMBEDDED WEB INTERFACE ---
HTML_CONTENT = """<!DOCTYPE html><html lang="en"><head>    <meta charset="UTF-8">    <meta name="viewport" content="width=device-width, initial-scale=1.0">    <title>Nova Assistant Configuration</title>    <link rel="stylesheet" href="/style.css">    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet"></head><body>    <div class="container">        <h1>Nova Assistant Configuration</h1>        <p class="description">Configure the behavior of your local voice assistant.</p>        <div class="card">            <div class="card-header">                <h2>Nova Settings</h2>            </div>            <div class="card-content">                <div class="status-section">                    <span>Local Assistant Status:</span>                    <span id="connection-status" class="status connecting">                        <span class="spinner"></span> Connecting...                    </span>                </div>                <div class="form-group">                    <label for="mode-select">Conversation Mode</label>                    <select id="mode-select">                        <option value="rapide">Fast (clear, precise, straight to the point)</option>                        <option value="normal">Normal (default)</option>                        <option value="histoire">Story (tells anecdotes, talks a lot)</option>                    </select>                </div>                <div class="form-group">                    <label for="hotword-input">Activation Keyword (Hotword)</label>                    <input type="text" id="hotword-input" value="nova" disabled class="disabled-input">                    <p class="hint">The hotword is configured via environment variables.</p>                </div>            </div>            <div class="card-footer">                <button id="apply-config-btn">Apply Configuration</button>            </div>        </div>    </div>    <script src="/script.js"></script></body></html>"""
CSS_CONTENT = """body {  font-family: "Inter", sans-serif;  margin: 0;  padding: 0;  background: linear-gradient(to bottom right, #f0f4f8, #d9e2ec);  display: flex;  justify-content: center;  align-items: center;  min-height: 100vh;  color: #333;}.container {  text-align: center;  padding: 20px;  max-width: 500px;  width: 100%;}h1 {  font-size: 2.5em;  color: #2c3e50;  margin-bottom: 10px;}.description {  font-size: 1.1em;  color: #555;  margin-bottom: 30px;}.card {  background-color: #fff;  border-radius: 12px;  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);  overflow: hidden;}.card-header {  background-color: #f8f9fa;  padding: 20px;  border-bottom: 1px solid #e0e6ed;}.card-header h2 {  font-size: 1.8em;  color: #34495e;  margin: 0;}.card-content {  padding: 30px;  text-align: left;  display: flex;  flex-direction: column;  gap: 25px;}.status-section {  display: flex;  justify-content: space-between;  align-items: center;  font-weight: 600;  color: #4a5568;}.status {  display: flex;  align-items: center;  font-weight: 600;}.status.connecting {  color: #3498db;}.status.connected {  color: #27ae60;}.status.disconnected {  color: #e74c3c;}.status .icon {  margin-right: 8px;  width: 20px;  height: 20px;}.spinner {  border: 3px solid rgba(255, 255, 255, 0.3);  border-top: 3px solid #3498db;  border-radius: 50%;  width: 16px;  height: 16px;  animation: spin 1s linear infinite;  margin-right: 8px;  display: inline-block;  vertical-align: middle;}@keyframes spin {  0% {    transform: rotate(0deg);  }  100% {    transform: rotate(360deg);  }}.form-group {  display: flex;  flex-direction: column;}.form-group label {  margin-bottom: 8px;  font-weight: 600;  color: #4a5568;}.form-group select,.form-group input {  padding: 12px 15px;  border: 1px solid #cbd5e0;  border-radius: 8px;  font-size: 1em;  color: #2d3748;  background-color: #f7fafc;  transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;}.form-group select:focus,.form-group input:focus {  border-color: #3498db;  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);  outline: none;}.form-group .disabled-input {  background-color: #e9ecef;  cursor: not-allowed;}.form-group .hint {  font-size: 0.85em;  color: #718096;  margin-top: 5px;}.card-footer {  padding: 20px;  border-top: 1px solid #e0e6ed;  background-color: #f8f9fa;  text-align: center;}.card-footer button {  width: 100%;  padding: 15px 25px;  background-color: #3498db;  color: white;  border: none;  border-radius: 8px;  font-size: 1.1em;  font-weight: 700;  cursor: pointer;  transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out;}.card-footer button:hover {  background-color: #2980b9;  transform: translateY(-2px);}.card-footer button:active {  transform: translateY(0);}"""
JS_CONTENT = """document.addEventListener("DOMContentLoaded", () => {  const connectionStatusSpan = document.getElementById("connection-status");  const modeSelect = document.getElementById("mode-select");  const hotwordInput = document.getElementById("hotword-input");  const applyConfigBtn = document.getElementById("apply-config-btn");  const LOCAL_ASSISTANT_URL = "http://127.0.0.1:5000"; // URL of the local Flask server  // Function to update connection status in the UI  function updateConnectionStatus(status) {    connectionStatusSpan.className = `status ${status}`;    if (status === "connecting") {      connectionStatusSpan.innerHTML = '<span class="spinner"></span> Connecting...';    } else if (status === "connected") {      connectionStatusSpan.innerHTML =        '<svg class="icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg> Connected';    } else {      connectionStatusSpan.innerHTML =        '<svg class="icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg> Disconnected';    }  }  // Function to check connection and sync status/mode from local assistant  async function checkConnectionAndSync() {    updateConnectionStatus("connecting");    try {      const response = await fetch(`${LOCAL_ASSISTANT_URL}/status`, { cache: "no-store" });      if (response.ok) {        const data = await response.json();        modeSelect.value = data.current_mode || "normal";        hotwordInput.value = data.hotword || "nova";        updateConnectionStatus("connected");      } else {        updateConnectionStatus("disconnected");      }    } catch (error) {      console.error("Failed to connect to local assistant:", error);      updateConnectionStatus("disconnected");    }  }  // Function to apply configuration to the local assistant  applyConfigBtn.addEventListener("click", async () => {    const selectedMode = modeSelect.value;    try {      const response = await fetch(`${LOCAL_ASSISTANT_URL}/config`, {        method: "POST",        headers: {          "Content-Type": "application/json",        },        body: JSON.stringify({ mode: selectedMode }),      });      if (response.ok) {        alert("Configuration applied successfully!");      } else {        const errorText = await response.text();        alert(`Failed to apply configuration: ${errorText}`);      }    } catch (error) {      console.error("Error sending configuration:", error);      alert("Could not connect to the local assistant to apply the configuration.");    }  });  // Initial check and periodic checks  checkConnectionAndSync();  setInterval(checkConnectionAndSync, 5000); // Check every 3 seconds});"""

# --- FLASK SERVER FOR INTERFACE AND CONFIGURATION ---
@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

@app.route('/style.css')
def serve_css():
    return Response(CSS_CONTENT, mimetype='text/css')

@app.route('/script.js')
def serve_js():
    return Response(JS_CONTENT, mimetype='application/javascript')

@app.route('/config', methods=['POST'])
def set_config():
    global current_mode
    data = request.json
    if 'mode' in data:
        new_mode = data['mode']
        if new_mode in ["rapide", "normal", "histoire"]:
            current_mode = new_mode
            print(f"Conversation mode updated: {current_mode}")
            text_to_speech(f"My conversation mode is now set to {current_mode}.")
            return jsonify({"status": "success", "mode": current_mode}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid mode"}), 400
    return jsonify({"status": "error", "message": "Missing 'mode' parameter"}), 400

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "running",
        "current_mode": current_mode,
        "hotword": HOTWORD,
        "groq_client_initialized": groq_client is not None,
        "elevenlabs_api_key_configured": ELEVEN_API_KEY is not None
    }), 200

def run_flask_app():
    print("Flask configuration server started on http://127.0.0.1:5000")
    app.run(port=5000, debug=False, use_reloader=False)

# --- MAIN ASSISTANT LOOP ---
def main_assistant_loop():
    print(f"Nova voice assistant launched. Say '{HOTWORD}' to start a command.")
    text_to_speech("Hello, I am Nova. Say my name to start.")
    while True:
        text = listen_for_speech()
        if text == "":
            continue
        if HOTWORD in text:
            text = text.replace(HOTWORD, "").strip()
            if text == "":
                text_to_speech("Yes? How can I help?")
                continue
                        
            # Try to execute a system action first
            if execute_system_action(text):
                continue # If a system action is executed, we don't go through the AI
                        
            # If no system action is recognized, pass to AI
            response = get_ai_response(text)
            text_to_speech(response)

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    # Start the main assistant loop
    main_assistant_loop()