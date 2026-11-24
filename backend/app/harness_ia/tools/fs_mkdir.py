import os
from pathlib import Path
from app.harness_ia.path_guard import resolve_in_zone
from app.harness_ia.policy import PolicyError

def execute_fs_mkdir(path_str: str) -> str:
    real_path = resolve_in_zone(path_str, must_exist=False)
    if real_path.exists():
        raise PolicyError("DESTINO_EXISTE", f"La carpeta ya existe: {real_path}")

    parent = real_path.parent
    if not parent.exists():
        raise PolicyError("PADRE_NO_EXISTE", f"La carpeta superior no existe: {parent}")

    try:
        os.mkdir(real_path)
    except FileExistsError:
        raise PolicyError("DESTINO_EXISTE", f"La carpeta ya existe: {real_path}")
    except Exception as e:
        raise PolicyError("ERROR_CREACION", f"No se pudo crear la carpeta: {e}")

    return str(real_path)

