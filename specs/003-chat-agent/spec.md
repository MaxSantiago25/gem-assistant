# Spec 003 — Chat Real con IA, Orquestador y Widget de Confirmación de Comandos

- **Estado**: APROBADA
- **Fecha**: 2026-11-07
- **Autor**: Agente (SDD)

## 1. Objetivo y Contexto
Conectar el módulo de Chat de la Isla Dinámica con los modelos de IA locales (`Gemma 4 E4B QAT` para perfil `rapido` y `Qwen 3.5 9B` para perfil `herramientas`) a través del Orquestador del Backend y el Harness de IA, permitiendo conversaciones reales y lanzando un widget interactivo de confirmación (`<ui-confirmation-card>`) dentro del chat cada vez que una acción requiera validación del usuario (crear carpeta, mover archivo, renombrar, abrir Google Chrome o escalar a la nube). Además, asegurar que la ventana nativa de escritorio (Tauri) sea visible y redimensionable sobre el escritorio de Windows.

## 2. Alcance
### Incluye
- Corrección de visibilidad y carga de la ventana nativa de escritorio en Tauri (`devUrl` + `custom-protocol` + posicionamiento físico y foco inicial).
- Orquestador del agente (`backend/app/agent/orchestrator.py`) integrado con `ModelRouter`, `LlamaCppProvider` y `HarnessExecutor`.
- Endpoints REST en `backend/app/api/chat.py`:
  - `POST /api/v1/chat` para enviar mensajes, recibir respuesta del modelo y, cuando aplique, recibir un lote pendiente de confirmación (`pending_batch`).
  - `POST /api/v1/actions/{batch_id}/confirm` para aprobar y ejecutar un lote validado.
  - `POST /api/v1/actions/{batch_id}/reject` para cancelar/rechazar un lote propuesto.
  - `POST /api/v1/actions/{batch_id}/undo` para revertir un lote ejecutado.
- Interfaz completa de Chat (`frontend/src/modules/chat/chat-view.js` y `chat-view.css`) con historial de mensajes, selector de modo/perfil, insignia del modelo utilizado y renderizado en línea del widget `<ui-confirmation-card>` para permitir o cancelar comandos.

### No incluye (Fuera de alcance)
- Ejecución de comandos arbitrarios de terminal/shell (prohibido por `HARNESS-IA.md`).
- Borrado o edición de contenido de archivos.

## 3. Criterios de Aceptación
- **CA-1 (Isla visible en el escritorio)**: Al iniciar la aplicación nativa de Tauri (`island-agent.exe`), la píldora flotante se muestra en la parte superior central del escritorio de Windows (`alwaysOnTop`), y al hacer clic se expande a 960×620 px y se contrae a 360×80 px.
- **CA-2 (Chat real con modelos locales)**: Al enviar un mensaje de conversación o redacción en el módulo Chat, el backend enruta al perfil `rapido` (`gemma-4-E4B-it-qat`), persiste los mensajes en SQLite y devuelve la respuesta mostrando la insignia del modelo y perfil usado.
- **CA-3 (Propuesta de comandos y validación por Harness)**: Cuando el usuario solicita una acción en el PC (crear carpeta, mover archivo, renombrar archivo, abrir Chrome), el orquestador enruta al perfil `herramientas` (`qwen3.5-9b`), valida las rutas/políticas con `HarnessExecutor.validate_batch` y registra la propuesta (`status = 'proposed'`).
- **CA-4 (Widget interactivo de confirmación)**: Si la acción requiere confirmación (`fs_mkdir`, `fs_move`, `fs_rename`, `os_open`, o `cloud_escalation`), el chat muestra un widget `<ui-confirmation-card>` con el detalle de la operación y botones para **Permitir (Aprobar y Ejecutar)** o **Cancelar (Rechazar)**.
- **CA-5 (Ejecución y reporte determinista / Cancelación)**: Al pulsar permitir en el widget, se ejecuta la acción real en el sistema de archivos/OS, se muestra el reporte determinista generado por el Harness (`report.py`) y se habilita la opción de deshacer. Al pulsar cancelar, la acción no se ejecuta y queda registrada como `rejected`.
- **CA-6 (Cumplimiento de Harness visual)**: Cero colores hexadecimales fuera de `tokens.css`, cero emojis en la interfaz (solo iconos SVG del sprite), tipografías Montserrat/Inter/Lato y animaciones con `--ease-mac`.

## 4. Impacto en Datos y Conexiones
- **Base de datos**: Uso de tablas existentes `conversations`, `messages` y `action_log`.
- **Conexiones (`backend/app/connections/`)**: Uso de `LlamaCppProvider` y `GeminiProvider` desde el registro de proveedores.

