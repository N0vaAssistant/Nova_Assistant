<a href="https://zupimages.net/viewer.php?id=25/31/xgq5.png"><img src="https://zupimages.net/up/25/31/xgq5.png" alt="" /></a>
*This project is in Beta 1.0 and was primarily developed in French. Some commands in English may not work properly yet.*

# Nova AI Assistant (100% Python)
*Nova is an intelligent, local, and customizable voice assistant, fully developed in Python. It combines speech recognition, speech synthesis, artificial intelligence, and a simple web interface for easy configuration.

## Main Features
**Local voice assistant**: listens to your commands without relying on the cloud.

**System actions**: open applications, type text, launch web searches, open the configuration interface.

**Customizable conversation modes**: fast, normal, or chatty (story mode).

**Integrated web interface**: easily configure the assistant via http://127.0.0.1:5000.

**Privacy-focused**: no voice data is sent without consent (AI and TTS services activated only with API keys).

## Technologies Used
**Python 3.8+**

**Flask (local web server)**

**SpeechRecognition (STT)**

**Pygame (audio playback)**

**Groq SDK (generative AI)**

**ElevenLabs API (natural voice synthesis)**

**PyAutoGUI (keyboard/mouse automation)**

**Subprocess & Tempfile (process and temporary file management)**

# Quick Installation
## Prerequisites

Python 3.8 or higher

**pip (Python package manager)**

## Steps
```
git clone https://github.com/N0vaAssistant/Nova_Assistant.git
cd nova-ai-assistant
```
*Create and activate a virtual environment (optional but recommended):*

## Windows:
```
python -m venv venv
.\venv\Scripts\activate
```
Install the dependencies manually listed in the Technologies section.

## Configuration
**Edit start.bat with your API keys and environment settings:**
```
set NOVA_HOTWORD=nova
set GROQ_API_KEY="your_groq_api_key"
set GROQ_MODEL="llama-3.3-70b-versatile"
set ELEVENLABS_API_KEY="your_elevenlabs_api_key"
set ELEVENLABS_VOICE_ID="EXAVITQu4vr4xnSDxMaL"
```
# How to get API keys
### 1. GROQ_API_KEY (Groq AI service):

**- Create an account on https://www.groq.com/**

**- Go to your developer dashboard**

**- Generate a new API key in the API Keys section**

**- Copy it and add it to your environment file under the GROQ_API_KEY variable**

### 2. ELEVENLABS_API_KEY (ElevenLabs speech synthesis):

**- Sign up at https://elevenlabs.io/**

**- Access your account and find the API section**

**- Create an API key and copy it**

**- Add it to your environment file under the ELEVENLABS_API_KEY variable**

# Launch
Double-click **start.bat** or run from a terminal:

python nova_assistant.py
**You will see two consoles:**

- Voice assistant (listening and responding)

- Flask server (web interface)

## Usage
**Talk to Nova: say the activation keyword (default is "nova"), then your command.**

**Example voice commands:**

**"Nova, open Chrome"**

**"Nova, write hello everyone"**

**"Nova, settings" (opens the configuration interface)**

**"Nova, search weather"**

*Configure Nova: open http://127.0.0.1:5000 in your browser to change modes and check status, or say "Nova settings".*

## Project Structure
```
 nova-ai-assistant/  
├── CONDITIONS.txt          # Contains the terms of use, legal conditions, or specific rules related to the project.

├── CONTRIBUTING.md         # Guide for contributors explaining how to participate: contribution rules, best practices, and how to propose changes.

├── LICENSE                 # Specifies the project license, detailing the rights and restrictions for using, modifying, and distributing the software.

├── Nova Luncher.lnk        # Windows shortcut (.lnk) likely used to launch the Nova application or a related script. Windows-specific file.

├── README.md               # Main project documentation with description, installation instructions, usage guidelines, and general info.

├── nova_assistant.py       # Primary Python script containing the source code for the Nova voice assistant.

└── start.bat               # Windows batch script (.bat) to easily launch the project or its components from the Windows command line.
```
**Plugin system integration for extending actions**

**Improved web interface with text chat and history**

**Visual notifications for user feedback**

**Global keyboard shortcuts for quick activation**

**Cross-platform installer for easy end-user setup**

# Contribution
*The project is 100% open source. Contributions, ideas, and feedback are welcome.
Please respect the GPL v3.0 license.*

# License
**This project is licensed under the GNU General Public License v3.0 (GPLv3).
For more information, see LICENSE or https://www.gnu.org/licenses/gpl-3.0.html.**
