import os
from pathlib import Path
from app.harness_ia.path_guard import resolve_in_zone
from app.harness_ia.policy import PolicyError

def execute_fs_rename(path_str: str, new_name: str) -> dict:
    source_path = resolve_in_zone(path_str, must_exist=True)

    if not new_name or "/" in new_name or "\\" in new_name:
        raise PolicyError("NOMBRE_INVALIDO", "El nuevo nombre no debe contener barras ni separadores")

    dest_path = source_path.parent / new_name

    # Validar la ruta destino resultante dentro de las zonas
    dest_path = resolve_in_zone(str(dest_path), must_exist=False)

    if dest_path.exists():
        raise PolicyError("DESTINO_EXISTE", f"Ya existe un elemento con el nuevo nombre: {dest_path}")

    try:
        os.rename(source_path, dest_path)
    except FileExistsError:
        raise PolicyError("DESTINO_EXISTE", f"Ya existe un elemento con el nuevo nombre: {dest_path}")
    except Exception as e:
        raise PolicyError("ERROR_RENOMBRADO", f"Error al renombrar: {e}")

    return {
        "source": str(source_path),
        "destination": str(dest_path)
    }

