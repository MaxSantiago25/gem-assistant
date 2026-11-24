import sqlite3
import os
from app.core.config import settings

def get_db_connection() -> sqlite3.Connection:
    """
    Retorna una conexión a SQLite configurada con WAL y foreign keys activas (02-backend.md §6).
    """
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.row_factory = sqlite3.Row
    return conn

