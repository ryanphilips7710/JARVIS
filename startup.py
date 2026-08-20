import pyaudio
import numpy as np
import time
import threading
import os


# ---------------- SETTINGS ---------------- #
THRESHOLD = 300      # Higher threshold usually helps filter background noise
WINDOW = 0.8         #time gap between windows
COOLDOWN = 3         # Seconds to wait before listening again
RATE = 44100
CHUNK = 1024


# ---------------- ACTION ON DOUBLE CLAP ---------------- #
def on_double_clap():
    print("Launching sequence...")

    def open_google():
        chrome_profile="Profile 13"
        url = "https://mail.google.com/mail/u/0/#inbox"
        url2 = "chrome://newtab/"
        try:
            os.system(f'start "" chrome --profile-directory="{chrome_profile}" --new-tab "{url}" "{url2}"')
        except Exception as e:
            pass

    apps = ['chrome', "code", "explorer", "spotify", "whatsapp:", "notion"]
    for app in apps:
        try:
            if app=="chrome":
                open_google()
                pass
            else:
                os.system(f"start {app}")
        except Exception as e:
            print(f"Could not launch {app}: {e}")

# ---------------- CLAP DETECTION ---------------- #
def listen_claps():
    last_clap_time = 0
    last_trigger_time = 0

    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
        channels=1, rate=RATE, input=True,
        frames_per_buffer=CHUNK)

    print(f"Detecting Wake sequence......")

    try:
        while True:
            # Read audio data
            data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
            
            # Calculate RMS (Root Mean Square) for energy
            rms = np.sqrt(np.mean(data.astype(float)**2))

            if rms > THRESHOLD:
                now = time.time()
                
                # Logic: If this clap is within the WINDOW of the last one
                if (now - last_clap_time < WINDOW) and (now - last_trigger_time > COOLDOWN):
                    last_trigger_time = now
                    threading.Thread(target=on_double_clap).start()
                    break
                
                last_clap_time = now
                time.sleep(0.1) 

    except KeyboardInterrupt:
        print("\nStopping gracefully...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

