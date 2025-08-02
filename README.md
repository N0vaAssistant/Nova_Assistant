# Nova AI Assistant (100% Python)
Nova est un assistant vocal intelligent, local et personnalisable, entièrement développé en Python. Il combine reconnaissance vocale, synthèse vocale, intelligence artificielle, et une interface web simple pour une configuration facile.

## Fonctionnalités principales
**Assistant vocal en local** : écoute vos commandes sans dépendre du cloud.

**Actions système** : ouvrir des applications, écrire du texte, lancer des recherches web, ouvrir l’interface de configuration.

**Modes de conversation** personnalisables : rapide, normal, ou bavard (histoire).

**Interface web intégrée** : configurer l’assistant facilement via http://127.0.0.1:5000.

**Respect de la vie privée** : aucune donnée vocale envoyée sans consentement (service IA et TTS activables uniquement avec clés API).

## Technologies utilisées

-Python 3.8+
-Flask (serveur web local)
-SpeechRecognition (STT)
-Pygame (lecture audio)
-Groq SDK (IA générative)
-ElevenLabs API (synthèse vocale naturelle)
-PyAutoGUI (automatisation clavier/souris)
-Subprocess & Tempfile (gestion des processus et fichiers temporaires)

## Installation rapide
### Prérequis

**- Python 3.8 ou supérieur**
**- pip (gestionnaire de paquets Python)**

### Étapes

**git clone https://github.com/N0vaAssistant/Nova_Assistant.git**
**cd nova-ai-assistant**

# Créer et activer un environnement virtuel (optionnel mais recommandé)
python -m venv venv
# Windows

.\venv\Scripts\activate

# Installer les dépendances

**installer manuellement les paquets listés dans la section Technologies.**

## Configuration
Modifiez le fichier **start.bat** avec tes clefs API et paramètres d’environnement :

set NOVA_HOTWORD=nova
set GROQ_API_KEY="ta_clef_api_groq"
set GROQ_MODEL="llama-3.3-70b-versatile"
set ELEVENLABS_API_KEY="ta_clef_api_elevenlabs"
set ELEVENLABS_VOICE_ID="EXAVITQu4vr4xnSDxMaL"
Lancement

### Comment récuperer les clefs API
**1. GROQ_API_KEY (service d’IA Groq) :**

Créez un compte sur https://www.groq.com/.

Une fois connecté, rendez-vous dans votre tableau de bord développeur.

Dans la section API Keys, générez une nouvelle clé.

Copiez-la et ajoutez-la dans votre fichier d’environnement sous la variable GROQ_API_KEY.

**2. ELEVENLABS_API_KEY (synthèse vocale ElevenLabs) :**

Inscrivez-vous sur https://elevenlabs.io/.

Accédez à votre compte et trouvez la section API.

Créez une clé API et copiez-la.

Placez cette clé dans votre fichier d’environnement sous la variable ELEVENLABS_API_KEY.


## Lancer
Double-clique sur start.bat ou lance depuis un terminal :

python nova_assistant.py
**Tu verras deux consoles** :

Assistant vocal (écoute et réponses)

Serveur Flask (interface web)

# Utilisation
**Parle à Nova** : dis le mot-clé d’activation (par défaut nova), puis ta commande.

Commandes vocales exemples :

"Nova, ouvre Chrome"

"Nova, écris bonjour à tous"

"Nova, paramètres" (ouvre l’interface de configuration)

"Nova, recherche la météo"

Configure Nova : ouvre http://127.0.0.1:5000 dans ton navigateur pour changer le mode et voir le statut ou dit **"Nova Paramettre"**.

# Structure du projet

nova-ai-assistant/

├── nova_assistant.py          # Script principal de l’assistant et serveur web

├── start.bat                  # Script de lancement Windows (configuration variables d’environnement)

├── README.md                  # Documentation du projet

├── requirements.txt           # Liste des dépendances Python (optionnel à ajouter)


**Intégration d’un système de plugins pour étendre les actions**

**Interface web améliorée avec chat textuel et historique**

**Notifications visuelles pour feedback utilisateur**

**Raccourcis clavier globaux pour activation rapide**

**Installeur multiplateforme pour faciliter l’usage final**

# Contribution
***Le projet est 100 % open source, contributions, idées et retours sont les bienvenus.
Merci de respecter la licence GPL v3.0.***

# Licence
**Ce projet est sous licence GNU General Public License v3.0 (GPLv3).
Pour plus d’informations, consulte LICENSE ou https://www.gnu.org/licenses/gpl-3.0.html.**
