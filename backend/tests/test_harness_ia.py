import os
import tempfile
import pytest
from pathlib import Path
from app.harness_ia.policy import HarnessPolicy, PolicyError
from app.harness_ia.path_guard import resolve_in_zone
from app.harness_ia.schemas import ActionBatch, ActionOperation
from app.harness_ia.executor import HarnessExecutor

@pytest.fixture
def temp_environment():
    with tempfile.TemporaryDirectory() as base_dir:
        base = Path(base_dir)
        zone1 = base / "Downloads"
        zone2 = base / "Documents"
        forbidden = base / "Windows"

        zone1.mkdir()
        zone2.mkdir()
        forbidden.mkdir()

        # Configurar política temporal
        policy_inst = HarnessPolicy()
        policy_inst.get_permitted_zones = lambda: [zone1, zone2]
        policy_inst.get_forbidden_zones = lambda: [forbidden]
        policy_inst.is_extension_blocked = lambda fn: Path(fn).suffix.lower() in [".exe", ".bat", ".ps1"]

        yield {
            "base": base,
            "zone1": zone1,
            "zone2": zone2,
            "forbidden": forbidden,
            "policy": policy_inst
        }

def test_path_guard_rejects_unc(temp_environment):
    with pytest.raises(PolicyError) as exc:
        resolve_in_zone(r"\\servidor\carpeta\archivo.txt")
    assert exc.value.code == "UNC_NO_PERMITIDO"

def test_path_guard_rejects_relative(temp_environment):
    with pytest.raises(PolicyError) as exc:
        resolve_in_zone("archivo.txt")
    assert exc.value.code == "RUTA_NO_ABSOLUTA"

def test_path_guard_rejects_ads(temp_environment):
    z1 = temp_environment["zone1"]
    with pytest.raises(PolicyError) as exc:
        resolve_in_zone(str(z1 / "archivo.txt:stream"))
    assert exc.value.code == "ADS_NO_PERMITIDO"

def test_path_guard_rejects_reserved_names(temp_environment):
    z1 = temp_environment["zone1"]
    with pytest.raises(PolicyError) as exc:
        resolve_in_zone(str(z1 / "con.txt"))
    assert exc.value.code == "NOMBRE_RESERVADO"

def test_static_forbidden_functions_audit():
    """Prueba estática (HARNESS-IA.md §10): verifica que no haya comandos destructivos en harness_ia."""
    pkg_dir = Path(__file__).resolve().parent.parent / "app" / "harness_ia"
    forbidden_tokens = [
        "os.remove", "os.unlink", "os.rmdir",
        "shutil.rmtree", "shutil.move", "os.replace",
        "shell=True"
    ]

    for py_file in pkg_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
            for token in forbidden_tokens:
                assert token not in content, f"Token prohibido '{token}' encontrado en {py_file.name}"

