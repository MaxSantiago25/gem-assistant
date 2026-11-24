import os
import tempfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.db.migrator import run_migrations
from app.core.config import settings

@pytest.fixture
def test_client_and_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db = f.name

    original_db = settings.database_path
    settings.database_path = temp_db

    # Ejecutar migraciones en la base de prueba
    run_migrations(temp_db)

    client = TestClient(app)
    yield client, temp_db

    settings.database_path = original_db
    try:
        os.remove(temp_db)
    except Exception:
        pass

def test_health_endpoint(test_client_and_db):
    client, _ = test_client_and_db
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "provider" in data

def test_security_token_rejected_without_header(test_client_and_db):
    client, _ = test_client_and_db
    res = client.get("/api/v1/settings")
    assert res.status_code == 401

def test_settings_crud(test_client_and_db):
    client, _ = test_client_and_db
    headers = {"X-Island-Token": settings.session_token}

    # Leer ajustes iniciales
    res = client.get("/api/v1/settings", headers=headers)
    assert res.status_code == 200

    # Actualizar ajustes
    payload = {"settings": {"theme": "dark", "cloud_allowed": False}}
    res_put = client.put("/api/v1/settings", json=payload, headers=headers)
    assert res_put.status_code == 200
    data = res_put.json()
    assert data["settings"]["theme"] == "dark"
    assert data["settings"]["cloud_allowed"] is False

def test_conversations_flow(test_client_and_db):
    client, _ = test_client_and_db
    headers = {"X-Island-Token": settings.session_token}

    # Crear conversación
    res = client.post("/api/v1/conversations", json={"title": "Test Chat", "provider": "llamacpp"}, headers=headers)
    assert res.status_code == 201
    conv = res.json()
    conv_id = conv["id"]
    assert conv["title"] == "Test Chat"

    # Agregar mensaje
    res_msg = client.post(f"/api/v1/conversations/{conv_id}/messages", json={"role": "user", "content": "Hola"}, headers=headers)
    assert res_msg.status_code == 201

    # Consultar detalle
    res_detail = client.get(f"/api/v1/conversations/{conv_id}", headers=headers)
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert len(detail["messages"]) == 1
    assert detail["messages"][0]["content"] == "Hola"

