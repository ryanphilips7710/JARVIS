import sqlite3
from datetime import datetime

DB_PATH = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS TASKS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',   -- pending, in_progress, done
            priority TEXT DEFAULT 'medium',  -- low, medium, high
            created_at TEXT,
            updated_at TEXT,
            due_date TEXT
        )
    ''')
    conn.commit()
    conn.close()
    

def add_task(title, description="", priority="medium", due_date=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO tasks (title, description, priority, created_at, updated_at, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, priority, now, now, due_date))
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return task_id

def get_all_tasks(status=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if status:
        c.execute('SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC', (status,))
    else:
        c.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def update_task_status(task_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?', (status, now, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def search_tasks(keyword):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ?',
              (f'%{keyword}%', f'%{keyword}%'))
    rows = c.fetchall()
    conn.close()
    return rows

def format_tasks_for_ai(tasks):
    """Convert task rows into readable text for AI context"""
    if not tasks:
        return "No tasks found."
    lines = []
    for t in tasks:
        lines.append(f"[ID:{t[0]}] {t[1]} | Status: {t[3]} | Priority: {t[4]} | Due: {t[7] or 'N/A'}")
    return "\n".join(lines)
