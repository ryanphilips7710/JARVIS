import asyncio
import io
import numpy as np
import sounddevice as sd
import time, sys
from colorama import Fore, Style, init
from pyfiglet import figlet_format

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

import pyttsx3
import edge_tts
import whisper
from ollama import Client

from system_info import SYSTEM_PROMPT 
from web_automation import automator
from system_function import (
    date_time, open_app, get_system_info, get_system_summary)
from weather import get_current_weather, get_weather_forecast

from task_manager import (
    init_db, add_task, get_all_tasks,
    update_task_status, delete_task,
    search_tasks, format_tasks_for_ai)
init_db()


#=========CONFIGURATINOS============
SAMPLE_RATE    = 16000              # Whisper expects 16kHz
RECORD_SECONDS = 7                  # seconds to listen per turn
WHISPER_MODEL  = "base"             # tiny | base | small | medium
EDGE_VOICE     = "en-GB-RyanNeural" # British male — closest to JARVIS
USE_EDGE_TTS   = True               # False = always use offline pyttsx3
OLLAMA_MODEL   = "gpt-oss:120b-cloud"


# ═══════════════════════════════════════════════════════════════
#  TTS — TEXT TO SPEECH
# ═══════════════════════════════════════════════════════════════

pygame.mixer.init()
def _clean(text: str) -> str:
    """Strip markdown symbols so TTS does not read them aloud."""
    for ch in ["**", "*", "##", "#", "`", "_"]:
        text = text.replace(ch, "")
    return text.strip()


def _offline_speak(text: str):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # 0 = David (Male)
    engine.setProperty('rate', 170)
    engine.say(text)
    engine.runAndWait()


async def _edge_speak_async(text: str):
    communicate = edge_tts.Communicate(text, EDGE_VOICE)
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    pygame.mixer.music.load(io.BytesIO(audio_bytes))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def speak(text: str):
    """Speak text aloud — edge-tts online, pyttsx3 as fallback."""
    clean_text = _clean(text)
    if USE_EDGE_TTS:
        try:
            _offline_speak(clean_text)
            #asyncio.run(_edge_speak_async(clean_text))
        except Exception:
            _offline_speak(clean_text)
    else:
        _offline_speak(clean_text)


# ═══════════════════════════════════════════════════════════════
#  STT — SPEECH TO TEXT (Whisper, direct numpy, no temp files)
# ═══════════════════════════════════════════════════════════════

#print("[JARVIS] Loading Whisper model... ", end="", flush=True)
stt_model = whisper.load_model(WHISPER_MODEL)


def listen() -> str:
    print(f"\n[🎙  Listening for {RECORD_SECONDS}s...]")
    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32')
    sd.wait()  # block until recording is complete

    # sounddevice returns shape (samples, channels) — Whisper needs 1D (samples,)
    audio_flat = audio.flatten()

    result = stt_model.transcribe(audio_flat, language="en", fp16=False)
    return result["text"].strip()


# ═══════════════════════════════════════════════════════════════
#  TASK MANAGER — SQLite database 
# ═══════════════════════════════════════════════════════════════

def build_system_prompt():
    """Fetch latest tasks from SQLite and inject into system prompt"""
    tasks = get_all_tasks()
    task_text = format_tasks_for_ai(tasks)
    return SYSTEM_PROMPT.format(task_context=task_text)


def handle_commands(ai_response: str):
    """Parse CMD lines from AI response and execute task operations"""
    for line in ai_response.splitlines():
        line = line.strip()

        if line.startswith("CMD:ADD_TASK|"):
            parts = line.split("|")
            title = parts[1] if len(parts) > 1 else "New Task"
            desc  = parts[2] if len(parts) > 2 else ""
            prio  = parts[3] if len(parts) > 3 else "medium"
            task_id = add_task(title, desc, prio)
            print(f"\n[JARVIS Tasks] ✅ Added — ID:{task_id} | {title} | {prio} priority")

        elif line.startswith("CMD:UPDATE_TASK|"):
            parts = line.split("|")
            try:
                task_id = int(parts[1])
                status  = parts[2]
                update_task_status(task_id, status)
                print(f"\n[JARVIS Tasks] 🔄 Task {task_id} → '{status}'")
            except Exception as e:
                print(f"\n[Task Update Error] {e}")

        elif line.startswith("CMD:DELETE_TASK|"):
            parts = line.split("|")
            try:
                task_id = int(parts[1])
                delete_task(task_id)
                print(f"\n[JARVIS Tasks] 🗑  Task {task_id} deleted")
            except Exception as e:
                print(f"\n[Task Delete Error] {e}")

        # --- System Function CMDs ---
        elif line.startswith("CMD:GET_DATETIME"):
            day, time = date_time()
            print(f"\n {day} {time}")
            speak(f"{day} {time}")

        elif line.startswith("CMD:OPEN_APP|"):
            app_name = line.split("|")[1]
            open_app(app_name)

        elif line.startswith("CMD:GET_SYSTEM_INFO"):
            get_system_info()
            summary = get_system_summary()
            speak(summary)

        # --- Weather CMDs ---
        elif line.startswith("CMD:GET_CURRENT_WEATHER|"):
            city = line.split("|")[1]
            summary = asyncio.run(get_current_weather(city))
            speak(summary)

        elif line.startswith("CMD:GET_WEATHER_FORECAST|"):
            parts = line.split("|")
            city = parts[1]
            days = int(parts[2]) if len(parts) > 2 else 3
            forecast = asyncio.run(get_weather_forecast(city, days))
            forecast_summary = f"Here is the weather forecast for {city} for the next {days} days. " + " ".join(forecast)
            summary=ask_jarvis(f'give me the summary of the weather{forecast}')
            print(f'\n{summary}')
            speak(summary)

        # --- Web Automation CMDs ---
        elif line.startswith("CMD:BROWSER_OPEN|"):
            url = line.split("|")[1]
            automator.open_website(url)

        elif line.startswith("CMD:GOOGLE_SEARCH|"):
            query = line.split("|")[1]
            automator.google_search(query)

        elif line.startswith("CMD:YOUTUBE_PLAY|"):
            video = line.split("|")[1]
            automator.youtube_play(video)
            
        elif line.startswith("CMD:CLOSE_BROWSER"):
            automator.close_browser()

    

# ═══════════════════════════════════════════════════════════════
#  AI BRAIN — OLLAMA
# ═══════════════════════════════════════════════════════════════

ollama_client = Client()
messages = [{"role": "system", "content": build_system_prompt()}]
EXIT_PHRASES = {"exit", "quit", "q", "goodbye", "shut down", "shutting down"}


def ask_jarvis(user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})
    print("\nJARVIS: ", end="", flush=True)
    full_response = ""

    stream_buffer = ""
    for part in ollama_client.chat(OLLAMA_MODEL, messages=messages, stream=True):
        chunk = part.message.content or ""
        full_response += chunk
        stream_buffer += chunk

        while "\n" in stream_buffer:
            line, stream_buffer = stream_buffer.split("\n", 1)
            if not line.strip().startswith("CMD:"):
                print(line, flush=True)

    if stream_buffer and not stream_buffer.strip().startswith("CMD:"):
        print(stream_buffer, end="", flush=True)

    print()
    messages.append({"role": "assistant", "content": full_response})
    
    # Execute any task commands AI issued
    handle_commands(full_response)

    clean_response = ""
    for line in full_response.splitlines():
        if line.strip().startswith("CMD:"):
            pass
        else:
            clean_response += line + "\n"

    return clean_response


# ═══════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════

init(autoreset=True)
def type_out(text, color=Fore.WHITE, delay=0.03):
    for ch in text:
        sys.stdout.write(color + ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_bar(label, color=Fore.CYAN, steps=20, delay=0.05):
    sys.stdout.write(color + f"  {label}: [")
    for i in range(steps):
        time.sleep(delay)
        sys.stdout.write(color + "█")
        sys.stdout.flush()
    print(color + "] DONE")

# ── Boot sequence ────────────────────────────────────

def brain():
    print(Fore.CYAN + "\n" + "─" * 55)
    print(Fore.CYAN + figlet_format("J.A.R.V.I.S", font="slant"))
    print(Fore.CYAN + "─" * 55)

    type_out("\n  Initializing JARVIS boot sequence...", Fore.YELLOW, 0.04)
    time.sleep(0.3)

    loading_bar("Neural Core        ", Fore.CYAN)
    loading_bar("Voice Synthesis    ", Fore.MAGENTA)
    loading_bar("Security Protocols ", Fore.GREEN)
    loading_bar("Arc Reactor Link   ", Fore.RED)

    time.sleep(0.3)
    print()
    type_out("  All systems operational.", Fore.GREEN, 0.05)
    type_out("  Welcome back sir, how can i help u today?", Fore.WHITE, 0.04)
    print(Fore.CYAN + "\n" + "─" * 55 + "\n")

    print(f"\n{'─' * 50}")
    print(f"  JARVIS ONLINE  |  Model: {OLLAMA_MODEL}")
    print(f"{'─' * 50}\n")
    print("\n[Enter] to speak  |  type a message and hit Enter to skip recording")

    speak("Welcome back sir. How can I help you today?")

    while True:
        try:
            mode = input(">>> ").strip()

            if mode == "":
                # ── Voice input ──
                user_input = listen()
                if not user_input:
                    print("[No speech detected — try again]")
                    continue
                print(f"You (voice): {user_input}")
            else:
                # ── Text input ──
                user_input = mode

            # Check for exit
            if user_input.lower() in EXIT_PHRASES:
                speak("Shutting down. Goodbye sir.")
                break

            # Get AI response and speak it
            response = ask_jarvis(user_input)
            speak(response)

        except KeyboardInterrupt:
            speak("Shutting down. Goodbye.")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
            # Remove last user message if request failed to keep history clean
            if len(messages) > 1 and messages[-1]["role"] == "user":
                messages.pop()


if __name__ == "__main__":
    brain()