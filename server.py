from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import traceback

# ── Import your existing modules ──────────────────────────────
from brain import ask_jarvis, listen, speak
from task_manager import (
    init_db, add_task, get_all_tasks,
    update_task_status, delete_task, search_tasks)

init_db()

app = Flask(__name__, static_folder="UI", static_url_path="/")
CORS(app)  # Allow frontend (widget/UI) to call this server

# ── Lock so voice + chat don't overlap ───────────────────────
_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════
#  ROOT — serve the main UI
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/widget")
def widget():
    return app.send_static_file("widget.html")


# ═══════════════════════════════════════════════════════════════
#  STATUS
# ═══════════════════════════════════════════════════════════════

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "online", "assistant": "JARVIS"})


# ═══════════════════════════════════════════════════════════════
#  CHAT — text input → AI response
# ═══════════════════════════════════════════════════════════════

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = (data or {}).get("message", "").strip()

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        with _lock:
            response = ask_jarvis(user_input)
            # Speak the response in background so API returns fast
            threading.Thread(target=speak, args=(response,), daemon=True).start()
        return jsonify({"response": response, "input": user_input})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  VOICE — trigger mic recording → transcribe → AI response
# ═══════════════════════════════════════════════════════════════

@app.route("/voice", methods=["POST"])
def voice():
    try:
        with _lock:
            # 1. Record + transcribe
            transcript = listen()
            if not transcript:
                return jsonify({"error": "No speech detected"}), 400

            # 2. Get AI response
            response = ask_jarvis(transcript)

            # 3. Speak in background
            threading.Thread(target=speak, args=(response,), daemon=True).start()

        return jsonify({
            "transcript": transcript,
            "response": response
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  TASKS
# ═══════════════════════════════════════════════════════════════

@app.route("/tasks", methods=["GET"])
def get_tasks():
    status_filter = request.args.get("status")
    tasks = get_all_tasks(status=status_filter)
    task_list = []
    for t in tasks:
        task_list.append({
            "id":          t[0],
            "title":       t[1],
            "description": t[2],
            "status":      t[3],
            "priority":    t[4],
            "created_at":  t[5],
            "updated_at":  t[6],
            "due_date":    t[7]
        })
    return jsonify({"tasks": task_list})


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    title       = data.get("title", "").strip()
    description = data.get("description", "")
    priority    = data.get("priority", "medium")
    due_date    = data.get("due_date")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    task_id = add_task(title, description, priority, due_date)
    return jsonify({"message": "Task created", "id": task_id}), 201


@app.route("/tasks/search", methods=["GET"])  # Must be BEFORE /tasks/<int:task_id>
def search():
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return jsonify({"error": "Query param 'q' required"}), 400
    tasks = search_tasks(keyword)
    task_list = [{"id": t[0], "title": t[1], "status": t[3], "priority": t[4]} for t in tasks]
    return jsonify({"results": task_list})


@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def patch_task(task_id):
    data   = request.get_json() or {}
    status = data.get("status", "").strip()

    valid = {"pending", "in_progress", "done"}
    if status not in valid:
        return jsonify({"error": f"Status must be one of {valid}"}), 400

    update_task_status(task_id, status)
    return jsonify({"message": f"Task {task_id} updated to '{status}'"})


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    delete_task(task_id)
    return jsonify({"message": f"Task {task_id} deleted"})


# ═══════════════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "─" * 50)
    print("  JARVIS SERVER  |  http://localhost:5000")
    print("─" * 50 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)