from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "todo.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        ''')

init_db()

@app.route("/")
def index():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT id, content, completed FROM tasks")
        tasks = cursor.fetchall()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task")
    if task:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO tasks (content) VALUES (?)", (task,))
    return redirect(url_for("index"))


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
        current = cursor.fetchone()
        if current:
            new_status = 0 if current[0] else 1
            conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080)
