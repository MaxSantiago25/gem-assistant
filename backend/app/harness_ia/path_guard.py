import os
from pathlib import Path
from typing import List
from app.harness_ia.policy import policy, PolicyError

RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}

def is_forbidden(real_path: Path, forbidden_zones: List[Path]) -> bool:
    for fz in forbidden_zones:
        try:
            if real_path == fz or real_path.is_relative_to(fz):
                return True
        except ValueError:
            continue
    # Prohibir también la raíz de cualquier unidad (ej. C:\)
    if real_path.parent == real_path:
        return True
    return False

def resolve_in_zone(raw: str, must_exist: bool = False) -> Path:
    """
    Valida y blinda una ruta según las políticas de HARNESS-IA.md §4 y §9.
    """
    if not raw or not isinstance(raw, str):
        raise PolicyError("RUTA_NO_ABSOLUTA", "Ruta vacía o no válida")

    raw = raw.strip()

    # 1. Rechazar rutas UNC (\\servidor\recurso)
    if raw.startswith("\\\\"):
        raise PolicyError("UNC_NO_PERMITIDO", "No se permiten rutas de red UNC")

    p = Path(raw)

    # 2. Obligar ruta absoluta
    if not p.is_absolute():
        raise PolicyError("RUTA_NO_ABSOLUTA", "La ruta debe ser absoluta")

    # 3. Flujos alternos de datos (ADS en NTFS: archivo.txt:stream)
    # En Windows, una ruta absoluta tiene letra de disco (ej. C:\), pero no debe tener dos puntos en el nombre
    if ":" in p.name:
        raise PolicyError("ADS_NO_PERMITIDO", "No se permiten flujos alternos de datos")

    # 4. Nombres reservados de Windows
    stem_upper = p.stem.upper()
    if stem_upper in RESERVED_NAMES:
        raise PolicyError("NOMBRE_RESERVADO", f"Nombre reservado de Windows no permitido: {stem_upper}")

    # 5. Resolver enlace simbólico, junction y ..
    try:
        real = Path(os.path.realpath(p))
    except Exception as e:
        raise PolicyError("RUTA_NO_ABSOLUTA", f"Error resolviendo ruta: {e}")

    # 6. Zonas prohibidas
    forbidden_zones = policy.get_forbidden_zones()
    if is_forbidden(real, forbidden_zones):
        raise PolicyError("ZONA_PROHIBIDA", f"Acceso a zona prohibida del sistema: {real}")

    # 7. Zonas permitidas
    permitted_zones = policy.get_permitted_zones()
    in_zone = False
    for pz in permitted_zones:
        try:
            if real == pz or real.is_relative_to(pz):
                in_zone = True
                break
        except ValueError:
            continue

    if not in_zone:
        raise PolicyError("FUERA_DE_ZONA", f"La ruta está fuera de las zonas autorizadas del usuario: {real}")

    # 8. Existencia previa si se requiere
    if must_exist and not real.exists():
        raise PolicyError("ORIGEN_NO_EXISTE", f"El archivo o directorio no existe: {real}")

    return real

