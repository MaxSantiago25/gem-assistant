import uuid
import sqlite3
from typing import List, Dict, Any, Optional
from app.db.connection import get_db_connection

class ConversationRepository:
    def list_all(self, conn: sqlite3.Connection = None) -> List[Dict[str, Any]]:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, provider, created_at FROM conversations ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            if close_conn:
                conn.close()

    def get_by_id(self, conv_id: str, conn: sqlite3.Connection = None) -> Optional[Dict[str, Any]]:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, provider, created_at FROM conversations WHERE id = ?", (conv_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            if close_conn:
                conn.close()

    def create(self, title: str, provider: str = "llamacpp", conn: sqlite3.Connection = None) -> Dict[str, Any]:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True

        conv_id = str(uuid.uuid4())
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (id, title, provider, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (conv_id, title, provider))
            conn.commit()
            return self.get_by_id(conv_id, conn)
        finally:
            if close_conn:
                conn.close()

    def get_messages(self, conv_id: str, conn: sqlite3.Connection = None) -> List[Dict[str, Any]]:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, conversation_id, role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
            """, (conv_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            if close_conn:
                conn.close()

    def add_message(self, conv_id: str, role: str, content: str, conn: sqlite3.Connection = None) -> Dict[str, Any]:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True

        msg_id = str(uuid.uuid4())
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (id, conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (msg_id, conv_id, role, content))
            conn.commit()

            cursor.execute("SELECT id, conversation_id, role, content, created_at FROM messages WHERE id = ?", (msg_id,))
            return dict(cursor.fetchone())
        finally:
            if close_conn:
                conn.close()

conversation_repo = ConversationRepository()

