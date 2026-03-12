import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "bridge.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            client_task_id TEXT,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            input_json TEXT NOT NULL,
            result_json TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cols = [row[1] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    if 'agent_id' not in cols:
        conn.execute("ALTER TABLE tasks ADD COLUMN agent_id TEXT")
    conn.commit()
    conn.close()


def insert_task(task: dict) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO tasks (task_id, client_task_id, agent_id, action, status, input_json, result_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            task["task_id"],
            task.get("client_task_id"),
            task.get("agent_id"),
            task["action"],
            task["status"],
            json.dumps(task["input"], ensure_ascii=False),
            json.dumps(task.get("result"), ensure_ascii=False) if task.get("result") is not None else None,
            task["created_at"],
            task["updated_at"],
        ),
    )
    conn.commit()
    conn.close()


def update_task(task_id: str, status: str, result: dict | None, updated_at: str) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE tasks SET status = ?, result_json = ?, updated_at = ? WHERE task_id = ?",
        (status, json.dumps(result, ensure_ascii=False) if result is not None else None, updated_at, task_id),
    )
    conn.commit()
    conn.close()


def get_task(task_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "task_id": row["task_id"],
        "client_task_id": row["client_task_id"],
        "agent_id": row["agent_id"] if "agent_id" in row.keys() else None,
        "action": row["action"],
        "status": row["status"],
        "input": json.loads(row["input_json"]),
        "result": json.loads(row["result_json"]) if row["result_json"] else None,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
