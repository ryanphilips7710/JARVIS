# JARVIS

JARVIS is a local Python-based personal assistant project currently in development. It combines voice interaction, AI chat, task management, web automation, and a simple browser UI.

> 🚧 This project is in development stage — stay tuned to see how it grows.

## Overview

- `server.py`: Flask app exposing endpoints for chat, voice, task management, and a web UI.
- `brain.py`: Core assistant logic, including speech-to-text, text-to-speech, AI interaction, task commands, and system automation.
- `startup.py`: Optional wake-word-like clap listener that can launch the assistant sequence and open common apps.
- `task_manager.py`: SQLite-backed task database and CRUD helper functions.
- `UI/`: Static web interface files for frontend access.

## Features

- Voice input via Whisper and `sounddevice`
- Text-to-speech playback with `edge-tts` and offline `pyttsx3`
- AI chat using Ollama models
- Task creation, search, update, and deletion via SQLite
- Web automation helpers for browser actions
- Simple Flask UI served from `UI/index.html` and `UI/widget.html`

## Requirements

- Python 3.11+ recommended
- Windows environment (project uses Windows `start` commands in `startup.py`)
- Required packages include:
  - `flask`
  - `flask-cors`
  - `pyaudio`
  - `numpy`
  - `sounddevice`
  - `colorama`
  - `pyfiglet`
  - `pygame`
  - `pyttsx3`
  - `edge-tts`
  - `whisper`
  - `ollama`

## Install

1. Create and activate a virtual environment.

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
python -m pip install flask flask-cors pyaudio numpy sounddevice colorama pyfiglet pygame pyttsx3 edge-tts whisper ollama
```

## Build Stage

In the build stage, prepare the environment and verify dependencies before running the assistant.

1. Ensure the Python environment is active.
2. Install the required Python packages.
3. If you want a reproducible dependency list, create a `requirements.txt` file:

```powershell
python -m pip freeze > requirements.txt
```

4. Optionally, package the project into a standalone executable using a tool such as `pyinstaller`:

```powershell
python -m pip install pyinstaller
python -m pyinstaller --onefile server.py
```

This build stage helps ensure the project runs consistently across machines and can be packaged for deployment.

## Run

### Start the web server

```powershell
python server.py
```

Then open `http://localhost:5000` in your browser.

### Start the clap wake listener

```powershell
python startup.py
```

### Start the assistant directly

```powershell
python brain.py
```

## Project Structure

- `brain.py` — assistant core and AI integration
- `server.py` — Flask API and UI server
- `startup.py` — clap listener and app launcher
- `task_manager.py` — SQLite task CRUD
- `system_function.py` — system utilities and app commands
- `system_info.py` — system prompt and info generation
- `weather.py` — weather lookup helpers
- `web_automation.py` — browser automation utilities
- `UI/` — static web interface assets

## Notes

- `tasks.db` is created automatically by `task_manager.py`.
- Adjust paths and profiles in `startup.py` to match your local Windows environment.
- Make sure `ollama` is configured and reachable if using the AI model in `brain.py`.
