from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from pathlib import Path
from datetime import date

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("study_planner.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT NOT NULL DEFAULT '#4f46e5'
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            subject_id INTEGER,
            deadline TEXT,
            priority TEXT NOT NULL DEFAULT 'Medium'
                CHECK(priority IN ('High','Medium','Low')),
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK(status IN ('Pending','Completed')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL
        );
        """)
        count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO subjects(name,color) VALUES(?,?)",
                [
                    ("Data Structures", "#7c3aed"),
                    ("Python", "#16a34a"),
                    ("Computer Organization", "#ea580c"),
                    ("Mathematics", "#2563eb"),
                    ("Others", "#64748b"),
                ],
            )
        task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if task_count == 0:
            subjects = {r["name"]: r["id"] for r in conn.execute("SELECT id,name FROM subjects")}
            conn.executemany("""
                INSERT INTO tasks(title,description,subject_id,deadline,priority,status)
                VALUES(?,?,?,?,?,?)
            """, [
                ("Revise Data Structures", "Review trees, linked lists and arrays", subjects["Data Structures"], date.today().isoformat(), "High", "Completed"),
                ("Practice Python", "Functions, OOP and exception handling", subjects["Python"], date.today().isoformat(), "Medium", "Completed"),
                ("Complete COA notes", "Finish today's notes", subjects["Computer Organization"], date.today().isoformat(), "High", "Pending"),
                ("Solve Maths problems", "Practice calculus questions", subjects["Mathematics"], date.today().isoformat(), "Low", "Pending"),
                ("Build mini project", "Work on Study Planner", subjects["Python"], date.today().isoformat(), "Medium", "Pending"),
                ("Read Git chapter", "Review Git basics", subjects["Others"], date.today().isoformat(), "Low", "Pending"),
            ])

@app.route("/")
def dashboard():
    filter_status = request.args.get("status", "All")
    with get_db() as conn:
        subjects = conn.execute("""
            SELECT s.id, s.name, s.color,
                   COUNT(t.id) AS total,
                   SUM(CASE WHEN t.status='Completed' THEN 1 ELSE 0 END) AS completed
            FROM subjects s LEFT JOIN tasks t ON t.subject_id=s.id
            GROUP BY s.id ORDER BY s.id
        """).fetchall()

        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'").fetchone()[0]
        pending = total - completed
        progress = round((completed / total) * 100) if total else 0

        query = """
            SELECT t.*, s.name AS subject_name, s.color AS subject_color
            FROM tasks t LEFT JOIN subjects s ON s.id=t.subject_id
        """
        params = []
        if filter_status in ("Pending", "Completed"):
            query += " WHERE t.status=?"
            params.append(filter_status)
        query += """
            ORDER BY CASE t.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
                     CASE WHEN t.deadline IS NULL OR t.deadline='' THEN 1 ELSE 0 END,
                     t.deadline ASC, t.id DESC
        """
        tasks = conn.execute(query, params).fetchall()
        all_subjects = conn.execute("SELECT id,name FROM subjects ORDER BY name").fetchall()
        weak_topics = conn.execute("""
            SELECT s.name, s.color, COUNT(t.id) AS pending_count
            FROM subjects s LEFT JOIN tasks t ON t.subject_id=s.id AND t.status='Pending'
            GROUP BY s.id ORDER BY pending_count DESC, s.name LIMIT 4
        """).fetchall()

    return render_template(
        "index.html", subjects=subjects, tasks=tasks, all_subjects=all_subjects,
        total=total, completed=completed, pending=pending, progress=progress,
        filter_status=filter_status, weak_topics=weak_topics, today=date.today()
    )

@app.post("/tasks/add")
def add_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    subject_id = request.form.get("subject_id") or None
    deadline = request.form.get("deadline") or None
    priority = request.form.get("priority", "Medium")
    if not title:
        return redirect(url_for("dashboard"))
    if priority not in ("High", "Medium", "Low"):
        priority = "Medium"
    with get_db() as conn:
        conn.execute("""
            INSERT INTO tasks(title,description,subject_id,deadline,priority)
            VALUES(?,?,?,?,?)
        """, (title, description, subject_id, deadline, priority))
    return redirect(url_for("dashboard"))

@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with get_db() as conn:
        conn.execute("""
            UPDATE tasks
            SET status = CASE WHEN status='Completed' THEN 'Pending' ELSE 'Completed' END
            WHERE id=?
        """, (task_id,))
    return redirect(request.referrer or url_for("dashboard"))

@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    with get_db() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    return redirect(url_for("dashboard"))

@app.post("/tasks/<int:task_id>/edit")
def edit_task(task_id):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    subject_id = request.form.get("subject_id") or None
    deadline = request.form.get("deadline") or None
    priority = request.form.get("priority", "Medium")
    if title and priority in ("High", "Medium", "Low"):
        with get_db() as conn:
            conn.execute("""
                UPDATE tasks SET title=?, description=?, subject_id=?,
                    deadline=?, priority=? WHERE id=?
            """, (title, description, subject_id, deadline, priority, task_id))
    return redirect(url_for("dashboard"))

@app.get("/api/tasks")
def api_tasks():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT t.id,t.title,t.description,t.deadline,t.priority,t.status,
                   s.name AS subject
            FROM tasks t LEFT JOIN subjects s ON s.id=t.subject_id
            ORDER BY t.id DESC
        """).fetchall()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
