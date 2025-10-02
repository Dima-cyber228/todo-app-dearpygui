import sqlite3
from typing import List, Optional
from src.models.task import Task

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    completed BOOLEAN DEFAULT 0,
    category TEXT DEFAULT 'Общее',
    due_date TEXT,
    section TEXT DEFAULT 'Сегодня',
    parent_id INTEGER,
    notified BOOLEAN DEFAULT 0,
    description TEXT DEFAULT '',
    FOREIGN KEY (parent_id) REFERENCES tasks(id)
);
    """)
    conn.commit()
    conn.close()

def get_tasks(section: str = "Сегодня", parent_id: Optional[int] = None) -> List[Task]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if parent_id is None:
        cursor.execute("SELECT * FROM tasks WHERE section = ? AND parent_id IS NULL", (section,))
    else:
        cursor.execute("SELECT * FROM tasks WHERE parent_id = ?", (parent_id,))
    rows = cursor.fetchall()
    tasks = [
        Task(
            id=row["id"],
            title=row["title"],
            completed=bool(row["completed"]),
            category=row["category"],
            due_date=row["due_date"],
            section=row["section"],
            parent_id=row["parent_id"],
            notified=bool(row["notified"]),
            description=row["description"]
        )
        for row in rows
    ]
    conn.close()
    return tasks

def add_task(task: Task) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, completed, category, due_date, section, parent_id, notified, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (task.title, task.completed, task.category, task.due_date, task.section, task.parent_id, task.notified, task.description))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"[DEBUG] Добавлена задача в БД с ID: {task_id}")
    return task_id or 0

def update_task(task: Task):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET title = ?, completed = ?, category = ?, due_date = ?, section = ?, notified = ?, description = ?
        WHERE id = ?
    """, (task.title, task.completed, task.category, task.due_date, task.section, task.notified, task.description, task.id))
    conn.commit()
    conn.close()
    print(f"[DEBUG] Задача {task.id} обновлена: completed = {task.completed}")

def delete_task(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Удаляем также подзадачи
    cursor.execute("DELETE FROM tasks WHERE parent_id = ?", (task_id,))
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_task_by_id(task_id: int) -> Task:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise ValueError(f"Task with id {task_id} not found")

    task = Task(
        id=row["id"],
        title=row["title"],
        completed=bool(row["completed"]),
        category=row["category"],
        due_date=row["due_date"],
        section=row["section"],
        parent_id=row["parent_id"],
        notified=bool(row["notified"]),
        description=row["description"]
    )
    print(f"[DEBUG] Загружена задача {task.id}: completed = {task.completed}")
    return task