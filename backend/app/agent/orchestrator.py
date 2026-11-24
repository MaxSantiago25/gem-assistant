import json
import re
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.agent.router import router as model_router
from app.connections.registry import registry
from app.harness_ia.schemas import ActionBatch, ActionOperation
from app.harness_ia.executor import executor
from app.harness_ia.policy import policy, PolicyError
from app.harness_ia.audit import record_action
from app.harness_ia.undo import undo_batch
from app.harness_ia.tools.fs_list import execute_fs_list
from app.services.conversation_service import conversation_service


# Almacén en memoria de lotes pendientes de confirmación del usuario
PENDING_BATCHES: Dict[str, Dict[str, Any]] = {}


def _get_user_zones_map() -> Dict[str, str]:
    home = Path.home()
    return {
        "escritorio": str((home / "Desktop").resolve()),
        "descargas": str((home / "Downloads").resolve()),
        "documentos": str((home / "Documents").resolve()),
    }


def _detect_task_type(user_text: str, requested_mode: str = "auto") -> str:
    if requested_mode in ("rapido", "herramientas", "nube"):
        return requested_mode

    lower = user_text.lower()
    if any(k in lower for k in ("usa la nube", "usar nube", "usa gemini", "escalar a la nube", "modelo en la nube")):
        return "nube"

    action_keywords = (
        "crea una carpeta", "crear carpeta", "crea la carpeta", "nueva carpeta", "mkdir",
        "mueve", "mover", "traslada",
        "renombra", "renombrar", "cambia el nombre", "cambiar nombre",
        "lista ", "listar", "qué archivos hay", "que archivos hay", "archivos en ", "mostrar archivos",
        "abre chrome", "abrir chrome", "abre google chrome", "abrir google chrome", "abre el navegador"
    )
    if any(k in lower for k in action_keywords):
        return "acciones_pc"

    return "chat"


def _build_system_prompt(profile: str) -> str:
    zones = _get_user_zones_map()
    if profile == "herramientas":
        return (
            "Eres Gem, un asistente inteligente integrado en el escritorio de Windows.\n"
            "Responde siempre en español de forma clara y concisa.\n"
            "Rutas reales del usuario autorizadas por el Harness:\n"
            f"- Escritorio: {zones['escritorio']}\n"
            f"- Descargas: {zones['descargas']}\n"
            f"- Documentos: {zones['documentos']}\n\n"
            "Cuando el usuario pida realizar una acción en su PC (listar archivos, crear carpeta, mover archivo, "
            "renombrar archivo o abrir Google Chrome), DEBES incluir al final de tu respuesta un bloque JSON "
            "con las operaciones propuestas usando exactamente este formato:\n"
            "```json\n"
            "{\n"
            '  "operations": [\n'
            '    {"tool": "fs_mkdir", "params": {"path": "RUTA_ABSOLUTA"}}\n'
            "  ]\n"
            "}\n"
            "```\n"
            "Herramientas permitidas únicamente:\n"
            '1. "fs_list": {"path": "C:\\\\Users\\\\...\\\\Downloads"}\n'
            '2. "fs_mkdir": {"path": "C:\\\\Users\\\\...\\\\Desktop\\\\NuevaCarpeta"}\n'
            '3. "fs_move": {"source": "C:\\\\...\\\\origen.pdf", "destination": "C:\\\\...\\\\destino.pdf"}\n'
            '4. "fs_rename": {"path": "C:\\\\...\\\\archivo.pdf", "new_name": "nuevo.pdf"}\n'
            '5. "os_open": {"app_id": "chrome"}\n'
            "Nunca inventes otras herramientas. Usa siempre rutas absolutas completas de Windows."
        )

    return (
        "Eres Gem, un asistente personal rápido, elegante y preciso integrado en una Isla Dinámica en Windows. "
        "Responde siempre en español de forma clara, bien estructurada y directa."
    )


def _extract_json_operations(text: str) -> Optional[List[Dict[str, Any]]]:
    """Extrae bloques JSON con 'operations' o 'tool' de la respuesta del modelo."""
    code_blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    candidates = list(code_blocks)

    if not candidates:
        brace_matches = re.findall(r"(\{[^{}]*\"(?:operations|tool)\"[^{}]*(?:\{[^{}]*\}[^{}]*)*\})", text, flags=re.DOTALL)
        candidates.extend(brace_matches)

    for raw in candidates:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                if "operations" in data and isinstance(data["operations"], list):
                    return data["operations"]
                if "tool" in data and "params" in data:
                    return [{"tool": data["tool"], "params": data["params"]}]
        except Exception:
            continue
    return None


def _clean_json_from_response(text: str) -> str:
    """Remueve el bloque JSON técnico del texto visible para el usuario."""
    cleaned = re.sub(r"```(?:json)?\s*\{.*?\}\s*```", "", text, flags=re.DOTALL).strip()
    return cleaned


def _resolve_zone_from_text(text: str) -> str:
    zones = _get_user_zones_map()
    lower = text.lower()
    if "descarga" in lower or "download" in lower:
        return zones["descargas"]
    if "documento" in lower or "document" in lower:
        return zones["documentos"]
    return zones["escritorio"]


def _fallback_parse_intent(user_text: str) -> Optional[List[Dict[str, Any]]]:
    """
    Respaldo determinista si el usuario pide claramente una herramienta del Harness
    y el modelo omitió el bloque JSON exacto.
    """
    lower = user_text.lower().strip()
    zones = _get_user_zones_map()

    # 1. Abrir Chrome
    if any(k in lower for k in ("abre chrome", "abrir chrome", "abre google chrome", "abrir google chrome", "abre el navegador")):
        return [{"tool": "os_open", "params": {"app_id": "chrome"}}]

    # 2. Listar directorio
    if any(k in lower for k in ("lista", "listar", "qué archivos hay", "que archivos hay", "archivos en", "mostrar archivos")):
        target_zone = _resolve_zone_from_text(user_text)
        return [{"tool": "fs_list", "params": {"path": target_zone}}]

    # 3. Crear carpeta
    if any(k in lower for k in ("crea una carpeta", "crear carpeta", "crea la carpeta", "nueva carpeta", "mkdir", "crea carpeta")):
        # Buscar ruta absoluta explícita primero
        abs_match = re.search(r"([A-Za-z]:\\[^\s\"'`]+)", user_text)
        if abs_match:
            return [{"tool": "fs_mkdir", "params": {"path": abs_match.group(1)}}]

        target_zone = _resolve_zone_from_text(user_text)
        # Buscar nombre después de 'llamada', 'nombre', o entre comillas
        quoted = re.search(r"[\"'«“]([^\"'»”]+)[\"'»”]", user_text)
        if quoted:
            folder_name = quoted.group(1).strip()
        else:
            name_match = re.search(
                r"(?:llamada|nombre|carpeta)\s+([A-Za-z0-9_\-\.]+)",
                user_text,
                flags=re.IGNORECASE
            )
            folder_name = name_match.group(1).strip() if name_match else "NuevaCarpeta_Island"
            if folder_name.lower() in ("en", "el", "la", "mi", "mis", "escritorio", "descargas", "documentos", "llamada"):
                after_llamada = re.search(r"llamada\s+([A-Za-z0-9_\-\.]+)", user_text, flags=re.IGNORECASE)
                folder_name = after_llamada.group(1).strip() if after_llamada else "NuevaCarpeta_Island"

        full_path = str(Path(target_zone) / folder_name)
        return [{"tool": "fs_mkdir", "params": {"path": full_path}}]

    return None


def _format_fs_list_output(path_str: str, items: List[Dict[str, Any]]) -> str:
    if not items:
        return f"La carpeta `{path_str}` está vacía."
    lines = [f"Contenido de `{path_str}` ({len(items)} elementos):"]
    for entry in items[:25]:
        kind = "[Carpeta]" if entry["is_dir"] else f"({entry['size']:,} bytes)"
        lines.append(f"- {entry['name']} {kind}")
    if len(items) > 25:
        lines.append(f"... y {len(items) - 25} elementos adicionales.")
    return "\n".join(lines)


class AgentOrchestrator:
    async def process_chat_turn(
        self,
        conversation_id: str,
        user_message: str,
        mode: str = "auto",
        allow_cloud: bool = False
    ) -> Dict[str, Any]:
        # Verificar conversación o crearla si no existe
        conv = conversation_service.get_conversation_detail(conversation_id)
        if not conv:
            raise ValueError("CONVERSACION_NO_ENCONTRADA")

        # Guardar mensaje del usuario
        user_msg_record = conversation_service.append_message(
            conv_id=conversation_id,
            role="user",
            content=user_message
        )

        task_type = _detect_task_type(user_message, requested_mode=mode)

        # Caso: Escalado a la nube (solicitar permiso cada ocasión)
        if task_type == "nube" and not allow_cloud:
            batch_id = f"cloud-{uuid.uuid4().hex[:10]}"
            PENDING_BATCHES[batch_id] = {
                "type": "cloud_escalation",
                "conversation_id": conversation_id,
                "user_message": user_message,
                "model_profile": "nube"
            }
            prompt_msg = (
                "Para responder esta consulta con el modelo en la nube (Google Gemini), "
                "confirma la autorización para esta ocasión en la tarjeta inferior."
            )
            assistant_msg = conversation_service.append_message(
                conv_id=conversation_id,
                role="assistant",
                content=prompt_msg
            )
            return {
                "user_message": user_msg_record,
                "assistant_message": assistant_msg,
                "profile_used": "nube",
                "model_used": "gemini-2.5-flash (pendiente)",
                "pending_batch": {
                    "batch_id": batch_id,
                    "type": "cloud_escalation",
                    "model_profile": "nube",
                    "operations": [
                        {
                            "tool": "cloud_escalation",
                            "source_path": "Consulta de Chat (sin rutas ni archivos locales)",
                            "dest_path": "Google Gemini API",
                            "params": {}
                        }
                    ]
                }
            }

        # Determinar perfil y configuración del modelo
        if task_type in ("rapido", "herramientas", "nube"):
            profile = task_type
        else:
            profile = model_router.resolve_profile(task_type)

        profile_cfg = model_router.get_profile_config(profile)
        provider_name = profile_cfg.get("provider", "llamacpp")
        model_name = profile_cfg.get("model", "gemma-4-E4B-it-qat")

        # Construir historial de contexto
        updated_conv = conversation_service.get_conversation_detail(conversation_id)
        history_msgs = updated_conv.get("messages", [])[-10:]
        llm_messages = [{"role": "system", "content": _build_system_prompt(profile)}]
        for m in history_msgs:
            if m["role"] in ("user", "assistant"):
                llm_messages.append({"role": m["role"], "content": m["content"]})

        # Llamar al proveedor LLM
        raw_reply = ""
        try:
            provider = registry.get(provider_name) or registry.get_active()
            raw_reply = await provider.chat(
                messages=llm_messages,
                model=model_name,
                temperature=0.3 if profile == "herramientas" else 0.6,
                max_tokens=768
            )
        except Exception as err:
            err_code = str(err)
            if profile == "herramientas":
                raw_reply = "He preparado la acción solicitada para validación del Harness."
            else:
                raw_reply = (
                    f"Aviso del motor de IA (`{err_code}`): "
                    "Verifica que `llama-server` esté activo en el puerto 8080 o revisa Ajustes."
                )

        # Extraer operaciones propuestas si aplica
        raw_ops = _extract_json_operations(raw_reply)
        if not raw_ops and profile == "herramientas":
            raw_ops = _fallback_parse_intent(user_message)

        visible_reply = _clean_json_from_response(raw_reply)
        pending_batch_payload = None

        if raw_ops:
            # Separar lecturas auto-aprobadas (fs_list) de operaciones que requieren confirmación
            all_fs_list = all(op.get("tool") == "fs_list" for op in raw_ops)
            if all_fs_list and policy.is_auto_approved("fs_list"):
                list_outputs = []
                for op in raw_ops:
                    target_path = op.get("params", {}).get("path", "")
                    try:
                        entries = execute_fs_list(target_path)
                        record_action(
                            batch_id=f"list-{uuid.uuid4().hex[:8]}",
                            tool="fs_list",
                            status="done",
                            source_path=target_path,
                            model_profile=profile
                        )
                        list_outputs.append(_format_fs_list_output(target_path, entries))
                    except PolicyError as pe:
                        list_outputs.append(f"Acción bloqueada por Harness (`{pe.code}`): {pe.message}")

                combined_list_text = "\n\n".join(list_outputs)
                visible_reply = f"{visible_reply}\n\n{combined_list_text}".strip()
            else:
                # Validar lote con HarnessExecutor y preparar tarjeta de confirmación
                batch_id = f"batch-{uuid.uuid4().hex[:10]}"
                try:
                    op_objs = [
                        ActionOperation(tool=o.get("tool", ""), params=o.get("params", {}))
                        for o in raw_ops
                    ]
                    batch = ActionBatch(
                        batch_id=batch_id,
                        operations=op_objs,
                        model_profile=profile
                    )
                    validated_ops = executor.validate_batch(batch)

                    # Registrar cada operación como 'proposed' en action_log
                    for vop in validated_ops:
                        record_action(
                            batch_id=batch_id,
                            tool=vop["tool"],
                            status="proposed",
                            source_path=vop["source_path"],
                            dest_path=vop["dest_path"],
                            model_profile=profile
                        )

                    PENDING_BATCHES[batch_id] = {
                        "type": "harness_action",
                        "conversation_id": conversation_id,
                        "batch": batch,
                        "validated_ops": validated_ops,
                        "model_profile": profile
                    }

                    if not visible_reply:
                        visible_reply = "He preparado la siguiente acción. Por favor confirma en la tarjeta para ejecutarla:"

                    pending_batch_payload = {
                        "batch_id": batch_id,
                        "type": "harness_action",
                        "model_profile": profile,
                        "operations": validated_ops
                    }

                except PolicyError as pe:
                    record_action(
                        batch_id=batch_id,
                        tool="batch_validation",
                        status="rejected",
                        error_code=pe.code,
                        model_profile=profile
                    )
                    visible_reply = (
                        f"{visible_reply}\n\n"
                        f"Acción bloqueada por el Harness de Seguridad (`{pe.code}`): {pe.message}"
                    ).strip()

        if not visible_reply:
            visible_reply = "Operación procesada."

        assistant_msg = conversation_service.append_message(
            conv_id=conversation_id,
            role="assistant",
            content=visible_reply
        )

        return {
            "user_message": user_msg_record,
            "assistant_message": assistant_msg,
            "profile_used": profile,
            "model_used": model_name,
            "pending_batch": pending_batch_payload
        }

    async def confirm_pending_batch(self, batch_id: str) -> Dict[str, Any]:
        entry = PENDING_BATCHES.pop(batch_id, None)
        if not entry:
            raise ValueError("LOTE_NO_ENCONTRADO")

        conv_id = entry["conversation_id"]

        if entry["type"] == "cloud_escalation":
            # Ejecutar turno con permiso de nube concedido para esta única ocasión
            user_message = entry["user_message"]
            try:
                provider = registry.get("gemini") or registry.get_active()
                reply = await provider.chat(
                    messages=[{"role": "user", "content": user_message}],
                    model="gemini-2.5-flash"
                )
            except RuntimeError as re_err:
                if "NUBE_SIN_CLAVE" in str(re_err):
                    reply = "Escalado autorizado, pero no hay clave de Google Gemini configurada en Ajustes (`NUBE_SIN_CLAVE`)."
                else:
                    reply = f"Error al consultar la nube: {re_err}"

            msg = conversation_service.append_message(
                conv_id=conv_id,
                role="assistant",
                content=reply
            )
            return {
                "batch_id": batch_id,
                "status": "done",
                "report": reply,
                "assistant_message": msg
            }

        # Lote de acciones de Harness en PC
        batch: ActionBatch = entry["batch"]
        result = executor.execute_batch(batch)
        report_text = result["report"]

        msg = conversation_service.append_message(
            conv_id=conv_id,
            role="assistant",
            content=report_text
        )

        return {
            "batch_id": batch_id,
            "status": "done",
            "executed_count": result["executed_count"],
            "report": report_text,
            "assistant_message": msg
        }

    def reject_pending_batch(self, batch_id: str) -> Dict[str, Any]:
        entry = PENDING_BATCHES.pop(batch_id, None)
        if not entry:
            raise ValueError("LOTE_NO_ENCONTRADO")

        conv_id = entry["conversation_id"]
        profile = entry.get("model_profile", "herramientas")

        if entry["type"] == "harness_action":
            for vop in entry.get("validated_ops", []):
                record_action(
                    batch_id=batch_id,
                    tool=vop["tool"],
                    status="rejected",
                    source_path=vop["source_path"],
                    dest_path=vop["dest_path"],
                    error_code="CANCELADO_POR_USUARIO",
                    model_profile=profile
                )

        cancel_text = "Acción cancelada por el usuario. No se realizó ningún cambio en el equipo."
        msg = conversation_service.append_message(
            conv_id=conv_id,
            role="assistant",
            content=cancel_text
        )
        return {
            "batch_id": batch_id,
            "status": "rejected",
            "report": cancel_text,
            "assistant_message": msg
        }

    def undo_executed_batch(self, batch_id: str) -> Dict[str, Any]:
        res = undo_batch(batch_id)
        return res


orchestrator = AgentOrchestrator()
