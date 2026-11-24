import datetime
from typing import Optional, List, Dict, Any
from app.db.connection import get_db_connection

def record_action(
    batch_id: str,
    tool: str,
    status: str,
    source_path: Optional[str] = None,
    dest_path: Optional[str] = None,
    error_code: Optional[str] = None,
    model_profile: str = "herramientas",
    undo_of: Optional[int] = None
) -> int:
    ts = datetime.datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO action_log (batch_id, ts, tool, source_path, dest_path, status, error_code, model_profile, undo_of)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (batch_id, ts, tool, source_path, dest_path, status, error_code, model_profile, undo_of)
        )
        conn.commit()
        return cursor.lastrowid

def get_batch_actions(batch_id: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM action_log WHERE batch_id = ? ORDER BY id ASC",
            (batch_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_recent_actions(limit: int = 50) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM action_log ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

