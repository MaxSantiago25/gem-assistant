import os
import shutil
import tempfile
import uuid
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.db.migrator import run_migrations
from app.core.config import settings


@pytest.fixture
def client_and_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db = f.name

    original_db = settings.database_path
    settings.database_path = temp_db
    run_migrations(temp_db)

    client = TestClient(app)
    yield client, temp_db

    settings.database_path = original_db
    try:
        os.remove(temp_db)
    except Exception:
        pass


def test_chat_propose_and_reject_mkdir(client_and_db):
    client, _ = client_and_db
    headers = {"X-Island-Token": settings.session_token}
    folder_name = f"TestReject_{uuid.uuid4().hex[:6]}"
    target_path = Path.home() / "Desktop" / folder_name

    res = client.post(
        "/api/v1/chat",
        json={"message": f"Crea una carpeta llamada {folder_name} en Escritorio", "mode": "herramientas"},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["pending_batch"] is not None
    batch_id = data["pending_batch"]["batch_id"]
    assert data["pending_batch"]["operations"][0]["tool"] == "fs_mkdir"
    assert not target_path.exists()

    # Rechazar comando desde el widget
    res_reject = client.post(f"/api/v1/actions/{batch_id}/reject", headers=headers)
    assert res_reject.status_code == 200
    assert res_reject.json()["status"] == "rejected"
    assert not target_path.exists()


def test_chat_propose_and_confirm_mkdir(client_and_db):
    client, _ = client_and_db
    headers = {"X-Island-Token": settings.session_token}
    folder_name = f"TestConfirm_{uuid.uuid4().hex[:6]}"
    target_path = Path.home() / "Desktop" / folder_name

    try:
        res = client.post(
            "/api/v1/chat",
            json={"message": f"Crea una carpeta llamada {folder_name} en Escritorio", "mode": "herramientas"},
            headers=headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["pending_batch"] is not None
        batch_id = data["pending_batch"]["batch_id"]
        assert not target_path.exists()

        # Confirmar y ejecutar comando desde el widget
        res_confirm = client.post(f"/api/v1/actions/{batch_id}/confirm", headers=headers)
        assert res_confirm.status_code == 200
        confirm_data = res_confirm.json()
        assert confirm_data["status"] == "done"
        assert "Carpeta creada:" in confirm_data["report"]
        assert target_path.exists()
    finally:
        if target_path.exists():
            shutil.rmtree(target_path, ignore_errors=True)


def test_chat_cloud_escalation_requires_widget_confirmation(client_and_db):
    client, _ = client_and_db
    headers = {"X-Island-Token": settings.session_token}

    res = client.post(
        "/api/v1/chat",
        json={"message": "Analiza este texto con el modelo en la nube", "mode": "nube", "allow_cloud": False},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["pending_batch"] is not None
    assert data["pending_batch"]["type"] == "cloud_escalation"
    assert data["pending_batch"]["operations"][0]["tool"] == "cloud_escalation"

