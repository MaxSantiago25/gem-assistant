from typing import List, Dict, Any

def format_action_report(executed_actions: List[Dict[str, Any]]) -> str:
    """
    Genera el reporte determinista para el usuario según HARNESS-IA.md §6.
    El texto sale del registro ejecutado, nunca del modelo.
    """
    lines = []
    for action in executed_actions:
        tool = action.get("tool")
        source = action.get("source_path") or action.get("source")
        dest = action.get("dest_path") or action.get("destination") or action.get("path")

        if tool == "fs_move":
            lines.append(f"Movido:  {source}\n      →  {dest}")
        elif tool == "fs_rename":
            lines.append(f"Renombrado: {source}\n         → {dest}")
        elif tool == "fs_mkdir":
            lines.append(f"Carpeta creada: {dest}")
        elif tool == "os_open":
            target = source or dest or action.get("params", {}).get("app_id") or "Google Chrome"
            lines.append(f"Abierto: {target}")

    return "\n\n".join(lines)

