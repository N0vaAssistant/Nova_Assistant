# 🚀 Nova AI Assistant (Tout en Python)

Bienvenue sur Nova, votre assistant vocal intelligent et personnalisable, entièrement développé en Python ! Ce projet combine un assistant vocal local puissant avec une interface web de configuration simple, le tout dans un ensemble compact.

## ✨ Fonctionnalités

*   **Assistant Vocal Local** : Écoute vos commandes en arrière-plan.
*   **Actions Système** : Ouvre des applications, écrit du texte, recherche sur le web, **et ouvre l'interface de configuration**.
*   **Modes de Conversation** : "Rapide", "Normal", "Histoire" pour adapter les réponses de l'IA.
*   **Interface Web de Configuration** : Accédez à `http://127.0.0.1:5000` pour changer le mode et vérifier le statut.

## 🛠️ Technologies Utilisées

*   **Python 3.x** : Langage de programmation principal.
*   **Flask** : Micro-framework web pour servir l'interface de configuration.
*   **SpeechRecognition** : Pour la reconnaissance vocale (Speech-to-Text).
*   **Pygame** : Pour la lecture audio de la synthèse vocale.
*   **Groq (`groq` SDK)** : Service d'inférence IA haute performance pour la génération de texte rapide.
*   **ElevenLabs (`requests` pour l'API)** : Service de synthèse vocale (Text-to-Speech) pour des voix naturelles et expressives.
*   **PyAutoGUI** : Pour l'automatisation des interactions avec le système (écrire du texte).
*   **Subprocess** : Pour lancer des applications externes.
*   **tempfile** : Pour la gestion robuste des fichiers temporaires audio.

## 🚀 Démarrage Rapide

Suivez ces étapes pour lancer le projet sur votre machine locale.

### Prérequis

Assurez-vous d'avoir les éléments suivants installés :

*   **Python 3.x** (version 3.8 ou supérieure recommandée)
*   **pip** (généralement inclus avec Python)

### 1. Cloner le dépôt

\`\`\`bash
git clone <URL_DU_DEPOT>
cd nova-ai-assistant
\`\`\`

### 2. Installation des dépendances Python

Il est fortement recommandé d'utiliser un environnement virtuel.

\`\`\`bash
# Créer un environnement virtuel (une seule fois)
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
.\venv\Scripts\activate
# Sur macOS/Linux:
source venv/bin/activate

# Installer les dépendances
pip install SpeechRecognition requests pygame groq Flask pyautogui
\`\`\`

### 3. Configuration des Variables d'Environnement

Ce projet utilise des services externes (Groq et ElevenLabs) qui nécessitent des clés API. Vous devez définir ces variables d'environnement **avant de lancer le script Python**.

**TRÈS IMPORTANT** : Ouvrez le fichier `start.bat` et remplacez les placeholders par vos vraies clés API et ID de voix :

\`\`\`batch
:: REMPLACER AVEC VOS VRAIES CLÉS API ET ID DE VOIX
set NOVA_HOTWORD=nova
set GROQ_API_KEY="votre_cle_api_groq"
set GROQ_MODEL="llama-3.3-70b-versatile"
set ELEVENLABS_API_KEY="votre_cle_api_elevenlabs"
set ELEVENLABS_VOICE_ID="EXAVITQu4vr4xnSDxMaL"
\`\`\`

### 4. Lancer l'Assistant

Double-cliquez simplement sur le fichier `start.bat` à la racine de votre projet.

Deux fenêtres de console s'ouvriront :
*   Une pour le cœur de l'assistant Python (où vous verrez les logs d'écoute et de réponse).
*   Une autre pour le serveur Flask qui sert l'interface web.

### 5. Accéder à l'Interface de Configuration

Ouvrez votre navigateur web et naviguez vers : `http://127.0.0.1:5000`

## 💡 Utilisation

1.  **Lancer** : Exécutez `start.bat`. L'assistant vocal commencera à écouter en arrière-plan.
2.  **Configurer** : Utilisez l'interface web pour choisir le mode de conversation et appliquer les changements.
3.  **Parler** : Dites le mot-clé d'activation (par défaut : "Nova"), puis votre commande ou question.
    *   Ex: "Nova, ouvre Chrome"
    *   Ex: "Nova, écris bonjour"
    *   Ex: "Nova, **paramètres**" (pour ouvrir l'interface de configuration)
    *   Ex: "Nova, quelle est la météo ?"

## 📂 Structure du Projet

```
nova-ai-assistant/
├── icon/
     └── N.ico
├── public/
      └── images/
            └── nova_logo.png
├── luncher.py               
├── Nova Luncher.lnk
├── nova_assistant_en.py
├── nova_assistant_fr.py
├── README.fr.md
├── README.md
├── start_en.bat
└── start_fr.bat
```

## 💡 Améliorations Futures Possibles

*   **Plus d'Actions Système** : Étendre les capacités du script Python pour ouvrir d'autres applications, contrôler la musique, gérer des fichiers, etc.
*   **Système de Plugins** : Mettre en place une architecture de plugins pour ajouter facilement de nouvelles actions ou intégrations sans modifier le cœur de l'assistant.
*   **Interface de Chat Textuel** : Ajouter une zone de texte dans l'interface web pour permettre aux utilisateurs de taper des commandes en plus de l'entrée vocale.
*   **Historique de Session** : Implémenter une base de données légère (ex: SQLite) pour sauvegarder l'historique des conversations et des actions.
*   **Notifications Visuelles** : Ajouter des notifications (pop-ups) dans l'interface web pour confirmer les actions ou signaler les erreurs.
*   **Raccourcis Clavier Globaux** : Permettre d'activer l'assistant ou des actions spécifiques via des raccourcis clavier qui fonctionnent même lorsque l'interface n'est pas au premier plan.
*   **Installeur** : Créer un installeur (ex: avec PyInstaller) pour simplifier le déploiement du script Python et de ses dépendances pour les utilisateurs finaux.


N'hésitez pas à explorer le code, à contribuer ou à suggérer des améliorations !
