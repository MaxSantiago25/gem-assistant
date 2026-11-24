import json
import sqlite3
from typing import Dict, Any
from app.db.connection import get_db_connection

class SettingsRepository:
    def get_all(self, conn: sqlite3.Connection = None) -> Dict[str, Any]:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                k, v = row[0], row[1]
                try:
                    result[k] = json.loads(v)
                except Exception:
                    result[k] = v
            return result
        finally:
            if close_conn:
                conn.close()

    def update_many(self, settings_dict: Dict[str, Any], conn: sqlite3.Connection = None) -> int:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True

        try:
            cursor = conn.cursor()
            updated_count = 0
            for k, v in settings_dict.items():
                val_str = json.dumps(v) if not isinstance(v, str) else v
                cursor.execute("""
                    INSERT INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = CURRENT_TIMESTAMP
                """, (k, val_str))
                updated_count += 1
            conn.commit()
            return updated_count
        finally:
            if close_conn:
                conn.close()

settings_repo = SettingsRepository()

