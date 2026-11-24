from typing import List, Dict, Any
from app.harness_ia.schemas import ActionBatch, ActionOperation
from app.harness_ia.policy import policy, PolicyError
from app.harness_ia.path_guard import resolve_in_zone
from app.harness_ia.tools.fs_list import execute_fs_list
from app.harness_ia.tools.fs_mkdir import execute_fs_mkdir
from app.harness_ia.tools.fs_move import execute_fs_move
from app.harness_ia.tools.fs_rename import execute_fs_rename
from app.harness_ia.tools.os_open import execute_os_open
from app.harness_ia.audit import record_action
from app.harness_ia.report import format_action_report

class HarnessExecutor:
    def validate_batch(self, batch: ActionBatch) -> List[Dict[str, Any]]:
        """
        Valida todas las operaciones del lote. Si una sola falla, ninguna se ejecuta (HARNESS-IA.md §4.9).
        """
        max_batch = policy.get_limits().get("max_batch_operations", 50)
        if len(batch.operations) > max_batch:
            raise PolicyError("LIMITE_EXCEDIDO", f"El lote excede el límite de {max_batch} operaciones")

        validated = []
        for op in batch.operations:
            tool = op.tool
            params = op.params

            if tool == "fs_list":
                path = resolve_in_zone(params.get("path"), must_exist=True)
                validated.append({"tool": tool, "source_path": str(path), "dest_path": None, "params": params})

            elif tool == "fs_mkdir":
                path = resolve_in_zone(params.get("path"), must_exist=False)
                if path.exists():
                    raise PolicyError("DESTINO_EXISTE", f"La carpeta ya existe: {path}")
                validated.append({"tool": tool, "source_path": None, "dest_path": str(path), "params": params})

            elif tool == "fs_move":
                src = resolve_in_zone(params.get("source"), must_exist=True)
                dst = resolve_in_zone(params.get("destination"), must_exist=False)
                if src.drive.upper() != dst.drive.upper():
                    raise PolicyError("OTRO_VOLUMEN", "No se permite mover entre diferentes unidades")
                if dst.exists():
                    raise PolicyError("DESTINO_EXISTE", f"El archivo o carpeta de destino ya existe: {dst}")
                validated.append({"tool": tool, "source_path": str(src), "dest_path": str(dst), "params": params})

            elif tool == "fs_rename":
                src = resolve_in_zone(params.get("path"), must_exist=True)
                new_name = params.get("new_name")
                if not new_name or "/" in new_name or "\\" in new_name:
                    raise PolicyError("NOMBRE_INVALIDO", "Nombre de archivo inválido")
                dst = resolve_in_zone(str(src.parent / new_name), must_exist=False)
                if dst.exists():
                    raise PolicyError("DESTINO_EXISTE", f"Ya existe un archivo con ese nombre: {dst}")
                validated.append({"tool": tool, "source_path": str(src), "dest_path": str(dst), "params": params})

            elif tool == "os_open":
                app_id = params.get("app_id")
                file_path = params.get("file_path")
                if app_id and not policy.get_app(app_id):
                    raise PolicyError("APP_NO_AUTORIZADA", f"App no autorizada: {app_id}")
                if file_path:
                    fp = resolve_in_zone(file_path, must_exist=True)
                    if policy.is_extension_blocked(fp.name):
                        raise PolicyError("EXTENSION_BLOQUEADA", f"Extensión no permitida: {fp.suffix}")
                validated.append({"tool": tool, "source_path": file_path, "dest_path": None, "params": params})

            else:
                raise PolicyError("HERRAMIENTA_NO_PERMITIDA", f"Herramienta no reconocida: {tool}")

        return validated

    def execute_batch(self, batch: ActionBatch) -> Dict[str, Any]:
        """
        Ejecuta el lote previamente validado y genera el reporte.
        """
        try:
            validated_ops = self.validate_batch(batch)
        except PolicyError as e:
            # Registrar el rechazo atómico en action_log
            record_action(
                batch_id=batch.batch_id,
                tool="batch_validation",
                status="rejected",
                error_code=e.code,
                model_profile=batch.model_profile
            )
            raise e

        executed = []
        for op in validated_ops:
            tool = op["tool"]
            params = op["params"]
            src = op["source_path"]
            dst = op["dest_path"]

            try:
                if tool == "fs_list":
                    res = execute_fs_list(params["path"])
                elif tool == "fs_mkdir":
                    res = execute_fs_mkdir(params["path"])
                elif tool == "fs_move":
                    res = execute_fs_move(params["source"], params["destination"])
                elif tool == "fs_rename":
                    res = execute_fs_rename(params["path"], params["new_name"])
                elif tool == "os_open":
                    res = execute_os_open(params.get("app_id"), params.get("file_path"))

                record_action(
                    batch_id=batch.batch_id,
                    tool=tool,
                    status="done",
                    source_path=src,
                    dest_path=dst,
                    model_profile=batch.model_profile
                )
                executed.append(op)
            except Exception as e:
                err_code = getattr(e, "code", "ERROR_EJECUCION")
                record_action(
                    batch_id=batch.batch_id,
                    tool=tool,
                    status="failed",
                    source_path=src,
                    dest_path=dst,
                    error_code=err_code,
                    model_profile=batch.model_profile
                )
                raise e

        report_text = format_action_report(executed)
        return {
            "batch_id": batch.batch_id,
            "status": "success",
            "executed_count": len(executed),
            "report": report_text
        }

executor = HarnessExecutor()

