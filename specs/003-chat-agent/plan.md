# Plan Técnico — Spec 003: Chat Real con IA y Widget de Confirmación

## 1. Corrección de la Isla Nativa en Escritorio (Tauri)
- **`src-tauri/tauri.conf.json`**:
  - Añadir `"devUrl": "http://127.0.0.1:3000"` dentro de `"build"` para que el binario en modo desarrollo cargue inmediatamente el servidor local de `frontend/`.
  - Ajustar dimensiones iniciales de ventana a `360x80` (suficiente para la píldora de `340x48` más sombra y margen).
- **`src-tauri/Cargo.toml`**:
  - Añadir feature `"custom-protocol"` en `tauri` para que también soporte carga embebida cuando no se use servidor externo.
- **`src-tauri/src/lib.rs`**:
  - En `.setup()`, posicionar la ventana en el centro superior (`y = 8 * scale_factor`), invocar `window.show()`, `window.set_always_on_top(true)` y `window.set_focus()`.
  - En el comando `set_island_expanded`, redimensionar a `960x620` (expandido) o `360x80` (colapsado) manteniendo la posición superior centrada.
- **`frontend/src/core/tauri-bridge.js`**:
  - Invocar el comando nativo `set_island_expanded` mediante `window.__TAURI__.core.invoke('set_island_expanded', { expanded })` con respaldo a `windowApi.setSize`.

## 2. Orquestador del Agente y Endpoints (`backend/`)
- **`backend/app/agent/orchestrator.py`**:
  - Detectar intención de tarea (`chat`, `redaccion`, `acciones_pc`, `nube`).
  - Construir prompt de sistema con herramientas del Harness (`fs_list`, `fs_mkdir`, `fs_move`, `fs_rename`, `os_open`) y las zonas reales del usuario (`Descargas`, `Documentos`, `Escritorio`).
  - Extraer bloques JSON de llamadas a herramientas de la respuesta del modelo (además de un parser asistido determinista de respaldo si el usuario pide acciones directas y claras como crear carpeta, listar archivos o abrir Chrome).
  - Si la herramienta es `fs_list` (lectura auto-aprobada), ejecutarla y devolver el listado formateado.
  - Si la herramienta modifica estado o abre aplicación (`fs_mkdir`, `fs_move`, `fs_rename`, `os_open`), validar con `executor.validate_batch(batch)`, almacenar el lote en memoria (`PENDING_BATCHES`) y registrar en `action_log` como `proposed`.
- **`backend/app/api/chat.py`**:
  - `POST /api/v1/chat`: Ejecuta un turno de conversación y retorna el mensaje del asistente junto con `model_used`, `profile_used` y `pending_batch` (si requiere confirmación).
  - `POST /api/v1/actions/{batch_id}/confirm`: Ejecuta el lote pendiente con `executor.execute_batch`, guarda el reporte oficial en la conversación y devuelve el resultado.
  - `POST /api/v1/actions/{batch_id}/reject`: Rechaza el lote pendiente, registra `rejected` en `action_log` y guarda nota en la conversación.
  - `POST /api/v1/actions/{batch_id}/undo`: Ejecuta `undo_batch(batch_id)` y devuelve el resultado.

## 3. Frontend: Vista de Chat Real y Widget (`frontend/`)
- **`frontend/src/components/ui-confirmation-card/ui-confirmation-card.js` y `.css`**:
  - Eliminar colores hexadecimales en línea (`#22c55e`) y usar exclusivamente variables de `tokens.css`.
  - Soportar múltiples operaciones dentro de un mismo lote (`operations` en JSON o atributos `action`, `source`, `destination`) y conectar los eventos `action-approve`, `action-reject` y `action-undo` con el backend.
- **`frontend/src/modules/chat/chat-view.js` y `chat-view.css`**:
  - Cabecera del chat con selector de conversación, botón "Nueva conversación" y selector de perfil (`Auto`, `Rápido · Gemma 4`, `Herramientas · Qwen 3.5`, `Nube · Gemini`).
  - Lista de mensajes con auto-scroll, burbujas diferenciadas (`usuario` vs `agente`), insignia `<ui-badge>` con el modelo/perfil empleado y sugerencias rápidas clicables.
  - Renderizado del widget `<ui-confirmation-card>` cuando una respuesta contiene `pending_batch`, conectando los botones **Permitir (Aprobar y Ejecutar)** y **Cancelar (Rechazar)** con `/api/v1/actions/{batch_id}/confirm` y `/reject`.

