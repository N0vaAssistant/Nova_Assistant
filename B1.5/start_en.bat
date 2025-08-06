@echo off
echo Starting the Nova voice assistant...

:: --- Launching the local Python assistant script ---
echo.
echo Starting the core of the Python assistant (nova_assistant.py)...
echo Make sure Python is installed and that all dependencies are up to date (pip install SpeechRecognition requests pygame groq Flask pyautogui).
echo.

:: Set environment variables for the Python script
:: REPLACE WITH YOUR ACTUAL API KEYS AND VOICE ID
set NOVA_HOTWORD=nova
set GROQ_API_KEY=YOUR_KEY
set GROQ_MODEL=llama-3.3-70b-versatile
set ELEVENLABS_API_KEY=YOUR_KEY
set ELEVENLABS_VOICE_ID=9BWtsMINqrJLrRacOk9x

:: Launch the Python script in a new command window
:: "start cmd /k" opens a new window, runs the command, and keeps it open
start cmd /k python nova_assistant_en.py

echo.
echo The Nova voice assistant has been started.
echo The configuration interface is available in your browser at: http://127.0.0.1:5000
echo.
pause
