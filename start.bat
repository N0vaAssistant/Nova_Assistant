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
set GROQ_API_KEY=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
set GROQ_MODEL=llama-3.3-70b-versatile
set ELEVENLABS_API_KEY=sk_549565d5d6c77761d7c6f25931ff0b1bcb2cdaffcdf44e0e
set ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL

:: Lancer le script Python dans une nouvelle fenetre de console
:: Le "start cmd /k" ouvre une nouvelle fenetre et y execute la commande, puis la garde ouverte.
start cmd /k python nova_assistant.py

echo.
echo L'assistant vocal Nova est lance.
echo L'interface de configuration est accessible via votre navigateur a l'adresse : http://127.0.0.1:5000
echo.
pause
