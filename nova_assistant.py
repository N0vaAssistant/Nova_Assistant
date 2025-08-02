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
import tempfile # <-- Nouvelle importation

# --- CONFIGURATION GLOBALE ---
# Ces variables seront lues depuis les variables d'environnement pour plus de sécurité
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
print("GNU GENERAL PUBLIC LICENSE v3")
HOTWORD = os.getenv("NOVA_HOTWORD", "nova")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL") # Voix par défaut ElevenLabs

# --- INITIALISATION ---
app = Flask(__name__)
r = sr.Recognizer()
groq_client = None
current_mode = "normal" # Mode par défaut
conversation_history = [] # Pour maintenir le contexte de la conversation
audio_queue = queue.Queue() # File d'attente pour la lecture audio

# Initialisation de Pygame Mixer pour la lecture audio
pygame.mixer.init()

# Désactiver les logs de Flask pour ne pas polluer la console de l'assistant
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def init_groq_client():
    global groq_client
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
    else:
        print("GROQ_API_KEY non configurée. Les fonctions IA ne seront pas disponibles.")
init_groq_client()

# --- SYNTHÈSE VOCALE (TTS) ---
def synthese_vocale(texte):
    if not ELEVEN_API_KEY:
        print("ELEVENLABS_API_KEY non configurée. La synthèse vocale est désactivée.")
        print("Nova (texte) :", texte)
        return
    print("Nova :", texte)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": texte,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.75
        },
        "model_id": "eleven_multilingual_v2" # Modèle multilingue recommandé
    }
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP
        if not response.content:
            print("Réponse audio vide de ElevenLabs.")
            return
        # Utiliser une file d'attente pour la lecture audio non bloquante
        audio_queue.put(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Erreur TTS (requête) : {e}")
    except Exception as e:
        print(f"Erreur TTS inattendue : {e}")

def audio_playback_thread():
    while True:
        if not audio_queue.empty():
            audio_content = audio_queue.get()
            temp_file_path = None # Initialiser le chemin du fichier temporaire
            try:
                # Créer un fichier temporaire qui sera automatiquement supprimé à la fermeture
                # delete=False pour pouvoir le charger avec pygame, puis le supprimer manuellement
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                    temp_audio_file.write(audio_content)
                    temp_file_path = temp_audio_file.name # Récupérer le chemin du fichier
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10) # Limite la boucle pour ne pas consommer trop de CPU
                pygame.mixer.music.stop()
                pygame.mixer.music.unload() # Décharger explicitement la musique pour libérer le fichier
                # Donner un court instant au système d'exploitation pour libérer le handle du fichier
                time.sleep(0.1)
                # Tenter de supprimer le fichier temporaire
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Erreur de lecture audio ou de suppression de fichier : {e}")
                if temp_file_path and os.path.exists(temp_file_path):
                    print(f"Impossible de supprimer le fichier temporaire : {temp_file_path}. Veuillez le supprimer manuellement si nécessaire.")
            finally:
                audio_queue.task_done()
        time.sleep(0.1) # Petite pause pour éviter une boucle trop rapide

# Démarrer le thread de lecture audio
threading.Thread(target=audio_playback_thread, daemon=True).start()

# --- RECONNAISSANCE VOCALE (STT) ---
def ecouter():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source) # Ajuste le niveau de bruit ambiant
            print("Écoute...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5) # Limite le temps d'écoute
            texte = r.recognize_google(audio, language="fr-FR")
        print("Tu as dit :", texte)
        return texte.lower()
    except sr.WaitTimeoutError:
        # print("Pas de parole détectée.")
        return ""
    except sr.UnknownValueError:
        print("Impossible de comprendre l'audio.")
        return ""
    except sr.RequestError as e:
        print(f"Erreur de service Google Speech Recognition; {e}")
        return ""
    except Exception as e:
        print(f"Erreur micro inattendue : {e}")
        return ""

# --- INTERACTION IA (GROQ) ---
def get_system_prompt(mode: str):
    base_prompt = "Tu es Nova, un assistant vocal créé par un jeune développeur français nommé Guylann. La première version date du 01/08/25.Tu es sur windows et la personne en face est probablement en situation de handicape."
    if mode == "rapide":
        return "Tu es Nova, un assistant vocal concis et direct. Réponds de manière brève et précise, droit au but.Tu es sur windows et la personne en face est probablement en situation de handicape."
    elif mode == "histoire":
        return "Tu es Nova, un assistant vocal très bavard et aime raconter des anecdotes et des détails supplémentaires. Parle beaucoup et enrichis tes réponses.Tu es sur windows et la personne en face est probablement en situation de handicape."
    else: # normal
        return base_prompt

def parler_en_texte(prompt):
    if not groq_client:
        return "Je ne peux pas me connecter au service d'intelligence artificielle car la clé API Groq n'est pas configurée."
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
        print(f"Erreur IA: {e}")
        return "Je rencontre un problème avec le serveur d'intelligence artificielle."

# --- ACTIONS SYSTÈME ---
def executer_action_systeme(commande: str):
    commande_lower = commande.lower()
    if "ouvrir" in commande_lower:
        app_name = commande_lower.replace("ouvrir", "").strip()
        if "chrome" in app_name:
            synthese_vocale("J'ouvre Google Chrome.")
            subprocess.Popen(["start", "chrome"], shell=True) # Pour Windows
            return True
        elif "firefox" in app_name:
            synthese_vocale("J'ouvre Mozilla Firefox.")
            subprocess.Popen(["start", "firefox"], shell=True) # Pour Windows
            return True
        elif "notepad" in app_name or "bloc-notes" in app_name:
            synthese_vocale("J'ouvre le Bloc-notes.")
            subprocess.Popen(["notepad.exe"])
            return True
        elif "calculatrice" in app_name:
            synthese_vocale("J'ouvre la calculatrice.")
            subprocess.Popen(["calc.exe"])
            return True
        # Ajoutez d'autres applications ici
        else:
            synthese_vocale(f"Je ne sais pas comment ouvrir {app_name}.")
            return False
    elif "écrire" in commande_lower:
        text_to_type = commande_lower.replace("écrire", "").strip()
        if text_to_type:
            synthese_vocale(f"J'écris : {text_to_type}")
            pyautogui.write(text_to_type)
            return True
        else:
            synthese_vocale("Que voulez-vous que j'écrive ?")
            return False
    elif "rechercher" in commande_lower and ("google" in commande_lower or "web" in commande_lower):
        query = commande_lower.replace("rechercher sur google", "").replace("rechercher sur le web", "").strip()
        if query:
            synthese_vocale(f"Je recherche {query} sur Google.")
            subprocess.Popen(["start", f"https://www.google.com/search?q={query}"], shell=True)
            return True
        else:
            synthese_vocale("Que voulez-vous que je recherche ?")
            return False
    elif "paramètres" in commande_lower or "parametre" in commande_lower:
        synthese_vocale("J'ouvre l'interface de configuration.")
        subprocess.Popen(["start", "http://127.0.0.1:5000"], shell=True) # Ouvre l'URL de l'interface web
        return True
    return False # Aucune action système reconnue

# --- INTERFACE WEB EMBARQUÉE ---
HTML_CONTENT = """<!DOCTYPE html><html lang="fr"><head>    <meta charset="UTF-8">    <meta name="viewport" content="width=device-width, initial-scale=1.0">    <title>Nova Assistant Configuration</title>    <link rel="stylesheet" href="/style.css">    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet"></head><body>    <div class="container">        <h1>Nova Assistant Configuration</h1>        <p class="description">Configurez le comportement de votre assistant vocal local.</p>        <div class="card">            <div class="card-header">                <h2>Paramètres de Nova</h2>            </div>            <div class="card-content">                <div class="status-section">                    <span>Statut de l'Assistant Local :</span>                    <span id="connection-status" class="status connecting">                        <span class="spinner"></span> Connexion...                    </span>                </div>                <div class="form-group">                    <label for="mode-select">Mode de Conversation</label>                    <select id="mode-select">                        <option value="rapide">Rapide (clair, précis, droit au but)</option>                        <option value="normal">Normal (par défaut)</option>                        <option value="histoire">Histoire (raconte des anecdotes, parle beaucoup)</option>                    </select>                </div>                <div class="form-group">                    <label for="hotword-input">Mot-clé d'activation (Hotword)</label>                    <input type="text" id="hotword-input" value="nova" disabled class="disabled-input">                    <p class="hint">Le hotword est configuré via les variables d'environnement.</p>                </div>            </div>            <div class="card-footer">                <button id="apply-config-btn">Appliquer la Configuration</button>            </div>        </div>    </div>    <script src="/script.js"></script></body></html>"""
CSS_CONTENT = """body {  font-family: "Inter", sans-serif;  margin: 0;  padding: 0;  background: linear-gradient(to bottom right, #f0f4f8, #d9e2ec);  display: flex;  justify-content: center;  align-items: center;  min-height: 100vh;  color: #333;}.container {  text-align: center;  padding: 20px;  max-width: 500px;  width: 100%;}h1 {  font-size: 2.5em;  color: #2c3e50;  margin-bottom: 10px;}.description {  font-size: 1.1em;  color: #555;  margin-bottom: 30px;}.card {  background-color: #fff;  border-radius: 12px;  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);  overflow: hidden;}.card-header {  background-color: #f8f9fa;  padding: 20px;  border-bottom: 1px solid #e0e6ed;}.card-header h2 {  font-size: 1.8em;  color: #34495e;  margin: 0;}.card-content {  padding: 30px;  text-align: left;  display: flex;  flex-direction: column;  gap: 25px;}.status-section {  display: flex;  justify-content: space-between;  align-items: center;  font-weight: 600;  color: #4a5568;}.status {  display: flex;  align-items: center;  font-weight: 600;}.status.connecting {  color: #3498db;}.status.connected {  color: #27ae60;}.status.disconnected {  color: #e74c3c;}.status .icon {  margin-right: 8px;  width: 20px;  height: 20px;}.spinner {  border: 3px solid rgba(255, 255, 255, 0.3);  border-top: 3px solid #3498db;  border-radius: 50%;  width: 16px;  height: 16px;  animation: spin 1s linear infinite;  margin-right: 8px;  display: inline-block;  vertical-align: middle;}@keyframes spin {  0% {    transform: rotate(0deg);  }  100% {    transform: rotate(360deg);  }}.form-group {  display: flex;  flex-direction: column;}.form-group label {  margin-bottom: 8px;  font-weight: 600;  color: #4a5568;}.form-group select,.form-group input {  padding: 12px 15px;  border: 1px solid #cbd5e0;  border-radius: 8px;  font-size: 1em;  color: #2d3748;  background-color: #f7fafc;  transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;}.form-group select:focus,.form-group input:focus {  border-color: #3498db;  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);  outline: none;}.form-group .disabled-input {  background-color: #e9ecef;  cursor: not-allowed;}.form-group .hint {  font-size: 0.85em;  color: #718096;  margin-top: 5px;}.card-footer {  padding: 20px;  border-top: 1px solid #e0e6ed;  background-color: #f8f9fa;  text-align: center;}.card-footer button {  width: 100%;  padding: 15px 25px;  background-color: #3498db;  color: white;  border: none;  border-radius: 8px;  font-size: 1.1em;  font-weight: 700;  cursor: pointer;  transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out;}.card-footer button:hover {  background-color: #2980b9;  transform: translateY(-2px);}.card-footer button:active {  transform: translateY(0);}"""
JS_CONTENT = """document.addEventListener("DOMContentLoaded", () => {  const connectionStatusSpan = document.getElementById("connection-status");  const modeSelect = document.getElementById("mode-select");  const hotwordInput = document.getElementById("hotword-input");  const applyConfigBtn = document.getElementById("apply-config-btn");  const LOCAL_ASSISTANT_URL = "http://127.0.0.1:5000"; // URL du serveur Flask local  // Function to update connection status in the UI  function updateConnectionStatus(status) {    connectionStatusSpan.className = `status ${status}`;    if (status === "connecting") {      connectionStatusSpan.innerHTML = '<span class="spinner"></span> Connexion...';    } else if (status === "connected") {      connectionStatusSpan.innerHTML =        '<svg class="icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg> Connecté';    } else {      connectionStatusSpan.innerHTML =        '<svg class="icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg> Déconnecté';    }  }  // Function to check connection and sync status/mode from local assistant  async function checkConnectionAndSync() {    updateConnectionStatus("connecting");    try {      const response = await fetch(`${LOCAL_ASSISTANT_URL}/status`, { cache: "no-store" });      if (response.ok) {        const data = await response.json();        modeSelect.value = data.current_mode || "normal";        hotwordInput.value = data.hotword || "nova";        updateConnectionStatus("connected");      } else {        updateConnectionStatus("disconnected");      }    } catch (error) {      console.error("Failed to connect to local assistant:", error);      updateConnectionStatus("disconnected");    }  }  // Function to apply configuration to the local assistant  applyConfigBtn.addEventListener("click", async () => {    const selectedMode = modeSelect.value;    try {      const response = await fetch(`${LOCAL_ASSISTANT_URL}/config`, {        method: "POST",        headers: {          "Content-Type": "application/json",        },        body: JSON.stringify({ mode: selectedMode }),
      });
      if (response.ok) {
        alert("Configuration appliquée avec succès !");
      } else {
        const errorText = await response.text();
        alert(`Échec de l'application de la configuration: ${errorText}`);
      }
    } catch (error) {
      console.error("Erreur lors de l'envoi de la configuration:", error);
      alert("Impossible de se connecter à l'assistant local pour appliquer la configuration.");
    }
  });
  // Initial check and periodic checks
  checkConnectionAndSync();
  setInterval(checkConnectionAndSync, 5000); // Check every 3 seconds
});"""

# --- SERVEUR FLASK POUR L'INTERFACE ET LA CONFIGURATION ---
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
            print(f"Mode de conversation mis à jour : {current_mode}")
            synthese_vocale(f"Mon mode de conversation est maintenant réglé sur {current_mode}.")
            return jsonify({"status": "success", "mode": current_mode}), 200
        else:
            return jsonify({"status": "error", "message": "Mode invalide"}), 400
    return jsonify({"status": "error", "message": "Paramètre 'mode' manquant"}), 400

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
    print("Serveur de configuration Flask démarré sur http://127.0.0.1:5000")
    app.run(port=5000, debug=False, use_reloader=False)

# --- BOUCLE PRINCIPALE DE L'ASSISTANT ---
def main_assistant_loop():
    print(f"Assistant vocal Nova lancé. Dites '{HOTWORD}' pour commencer une commande.")
    synthese_vocale("Bonjour, je suis Nova. Dites mon nom pour commencer.")
    while True:
        texte = ecouter()
        if texte == "":
            continue
        if HOTWORD in texte:
            texte = texte.replace(HOTWORD, "").strip()
            if texte == "":
                synthese_vocale("Oui ? Que puis-je faire ?")
                continue
            
            # Tenter d'exécuter une action système d'abord
            if executer_action_systeme(texte):
                continue # Si une action système est exécutée, on ne passe pas par l'IA
            
            # Si aucune action système n'est reconnue, passer à l'IA
            reponse = parler_en_texte(texte)
            synthese_vocale(reponse)

if __name__ == "__main__":
    # Démarrer le serveur Flask dans un thread séparé
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    # Démarrer la boucle principale de l'assistant
    main_assistant_loop()
