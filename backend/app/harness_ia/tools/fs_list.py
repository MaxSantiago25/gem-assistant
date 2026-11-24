import os
from pathlib import Path
from typing import List, Dict, Any
from app.harness_ia.path_guard import resolve_in_zone
from app.harness_ia.policy import PolicyError

def execute_fs_list(path_str: str) -> List[Dict[str, Any]]:
    real_path = resolve_in_zone(path_str, must_exist=True)
    if not real_path.is_dir():
        raise PolicyError("RUTA_NO_ES_DIRECTORIO", f"La ruta no es un directorio: {real_path}")

    results = []
    try:
        with os.scandir(real_path) as it:
            for entry in it:
                try:
                    stat = entry.stat()
                    results.append({
                        "name": entry.name,
                        "is_dir": entry.is_dir(),
                        "size": stat.st_size if not entry.is_dir() else 0,
                        "modified": stat.st_mtime
                    })
                except Exception:
                    continue
    except Exception as e:
        raise PolicyError("ERROR_LECTURA", f"Error listando directorio: {e}")

    return sorted(results, key=lambda x: (not x["is_dir"], x["name"].lower()))

