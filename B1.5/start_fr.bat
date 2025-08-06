@echo off
echo Lancement de l'assistant vocal Nova...

:: --- Lancement du script Python de l'assistant local ---
echo.
echo Lancement du coeur de l'assistant Python (nova_assistant.py)...
echo Assurez-vous que Python est installe et que les dependances sont a jour (pip install SpeechRecognition requests pygame groq Flask pyautogui).
echo.


:: Definir les variables d'environnement pour le script Python
:: REMPLACER AVEC VOS VRAIES CLES API ET ID DE VOIX
set NOVA_HOTWORD=nova
set GROQ_API_KEY=VOTRE_KEY
set GROQ_MODEL=llama-3.3-70b-versatile
set ELEVENLABS_API_KEY=VOTRE_KEY
set ELEVENLABS_VOICE_ID=McVZB9hVxVSk3Equu8EH
:: Lancer le script Python dans une nouvelle fenetre de console
:: Le "start cmd /k" ouvre une nouvelle fenetre et y execute la commande, puis la garde ouverte.
start cmd /k python nova_assistant_fr.py

echo.
echo L'assistant vocal Nova est lance.
echo L'interface de configuration est accessible via votre navigateur a l'adresse : http://127.0.0.1:5000
echo.
pause
