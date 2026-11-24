import sqlite3
import os
from pathlib import Path
from app.core.config import settings

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"

def run_migrations(db_path: str = None) -> list[str]:
    """
    Aplica automáticamente todas las migraciones SQL pendientes en la base de datos (02-backend.md §6).
    Retorna la lista de versiones aplicadas en esta ejecución.
    """
    target_path = db_path or settings.database_path
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    applied_now = []
    with sqlite3.connect(target_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_migrations")
        already_applied = {row[0] for row in cursor.fetchall()}

        if MIGRATIONS_DIR.exists():
            migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"), key=lambda p: p.name)
            for m_file in migration_files:
                version = m_file.stem
                if version not in already_applied:
                    with open(m_file, "r", encoding="utf-8") as f:
                        sql_script = f.read()
                    conn.executescript(sql_script)
                    conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
                    applied_now.append(version)
                    print(f"[Migrator] Migración aplicada: {version}")

        conn.commit()

    return applied_now

