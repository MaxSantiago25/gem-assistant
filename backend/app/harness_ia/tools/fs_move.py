import os
from pathlib import Path
from app.harness_ia.path_guard import resolve_in_zone
from app.harness_ia.policy import PolicyError

def execute_fs_move(source_str: str, dest_str: str) -> dict:
    source_path = resolve_in_zone(source_str, must_exist=True)
    dest_path = resolve_in_zone(dest_str, must_exist=False)

    # 1. Verificar mismo volumen
    if source_path.drive.upper() != dest_path.drive.upper():
        raise PolicyError("OTRO_VOLUMEN", "No se permite mover archivos entre distintos discos o unidades")

    # 2. Verificar que destino no exista (nunca sobrescribir)
    if dest_path.exists():
        raise PolicyError("DESTINO_EXISTE", f"El destino ya existe: {dest_path}")

    # 3. Verificar que la carpeta contenedora de destino exista
    if not dest_path.parent.exists():
        raise PolicyError("PADRE_NO_EXISTE", f"El directorio contenedor de destino no existe: {dest_path.parent}")

    # 4. Usar estrictamente os.rename (falla si el destino existe y no copia ni borra entre volúmenes)
    try:
        os.rename(source_path, dest_path)
    except FileExistsError:
        raise PolicyError("DESTINO_EXISTE", f"El destino ya existe: {dest_path}")
    except OSError as e:
        if "different device" in str(e).lower() or getattr(e, "winerror", None) == 17:
            raise PolicyError("OTRO_VOLUMEN", "No se puede mover entre diferentes volúmenes")
        raise PolicyError("ERROR_MOVIMIENTO", f"Fallo al mover: {e}")

    return {
        "source": str(source_path),
        "destination": str(dest_path)
    }

