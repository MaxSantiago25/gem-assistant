import os
from pathlib import Path
from typing import Dict, Any, List
from app.harness_ia.audit import get_batch_actions, record_action
from app.harness_ia.policy import PolicyError

def undo_batch(batch_id: str) -> List[Dict[str, Any]]:
    actions = get_batch_actions(batch_id)
    if not actions:
        raise PolicyError("LOTE_NO_ENCONTRADO", f"No se encontraron acciones para el lote: {batch_id}")

    undo_results = []
    # Revertir en orden inverso
    for action in reversed(actions):
        if action["status"] != "done":
            continue

        tool = action["tool"]
        source = action["source_path"]
        dest = action["dest_path"]

        if tool in ("fs_move", "fs_rename"):
            if not os.path.exists(dest):
                raise PolicyError("DESTINO_NO_EXISTE", f"No se puede revertir: el archivo {dest} ya no existe")
            if os.path.exists(source):
                raise PolicyError("ORIGEN_OCUPADO", f"No se puede revertir: la ruta original {source} está ocupada")

            try:
                os.rename(dest, source)
                record_id = record_action(
                    batch_id=f"undo_{batch_id}",
                    tool=tool,
                    status="undone",
                    source_path=dest,
                    dest_path=source,
                    undo_of=action["id"]
                )
                undo_results.append({
                    "action_id": action["id"],
                    "undo_id": record_id,
                    "reverted": f"{dest} -> {source}"
                })
            except Exception as e:
                raise PolicyError("ERROR_DESHACER", f"Fallo al revertir movimiento: {e}")

    return undo_results

