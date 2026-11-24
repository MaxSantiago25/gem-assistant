import os
import subprocess
from pathlib import Path
from typing import Optional
from app.harness_ia.path_guard import resolve_in_zone
from app.harness_ia.policy import policy, PolicyError

def execute_os_open(app_id: Optional[str] = None, file_path: Optional[str] = None) -> dict:
    if not app_id and not file_path:
        raise PolicyError("PARAMETROS_INSUFICIENTES", "Debe proporcionar app_id o file_path")

    # Caso 1: Abrir aplicación registrada de lista blanca
    if app_id:
        app_def = policy.get_app(app_id)
        if not app_def:
            raise PolicyError("APP_NO_AUTORIZADA", f"Aplicación no registrada en lista blanca: {app_id}")

        executable = app_def.get("executable")
        if not executable or not os.path.exists(executable):
            raise PolicyError("EJECUTABLE_NO_ENCONTRADO", f"Ejecutable no encontrado: {executable}")

        args = [executable]
        if file_path:
            real_file = resolve_in_zone(file_path, must_exist=True)
            if policy.is_extension_blocked(real_file.name):
                raise PolicyError("EXTENSION_BLOQUEADA", f"Extensión no permitida: {real_file.suffix}")
            args.append(str(real_file))

        subprocess.Popen(args, shell=False)
        return {"opened": app_id, "args": args}

    # Caso 2: Abrir archivo con su programa predeterminado
    if file_path:
        real_file = resolve_in_zone(file_path, must_exist=True)
        if policy.is_extension_blocked(real_file.name):
            raise PolicyError("EXTENSION_BLOQUEADA", f"Extensión ejecutable o de script bloqueada: {real_file.suffix}")

        # En Windows os.startfile abre con el manejador registrado de forma segura sin shell
        if hasattr(os, "startfile"):
            os.startfile(str(real_file))
        else:
            subprocess.Popen(["explorer", str(real_file)], shell=False)

        return {"opened_file": str(real_file)}

    raise PolicyError("PARAMETROS_INVALIDOS")

