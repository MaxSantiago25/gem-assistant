# ARQUITECTURA DE IA

## 1. Principios
1. **El modelo propone; el harness decide.** Ningún modelo ejecuta nada directamente.
2. **Local primero.** La nube es escalado opcional y con reglas de privacidad.
3. **Un modelo en memoria a la vez** (6 GB de VRAM).
4. **Reglas, no magia, para enrutar.** El router es determinista y depurable.
5. **Todo pasa por `connections/`.** Ningún otro módulo habla con un modelo.

## 2. Vista general
```
Isla (JS) ──► Backend FastAPI (127.0.0.1)
                 │
        ┌────────┴──────────────────────────────────┐
        │ Orquestador del agente  (backend/app/agent)│
        │  1. Router      → elige perfil             │
        │  2. Contexto    → historial + ajustes      │
        │  3. Bucle de herramientas                  │
        │        └──► HARNESS DE IA ──► Windows      │
        │  4. Validación  → reintento / escalado     │
        └────────┬──────────────────────────────────┘
                 │ backend/app/connections/llm/
      ┌──────────┴───────────────┐
 llamacpp.py                 gemini.py
      │                          │
 llama-server (sidecar)       API de Google
 modo router, 1 modelo
   ├ rapido:       Gemma 4 E4B QAT
   └ herramientas: Qwen 3.5 9B
```

## 3. Componentes

| Componente | Responsabilidad | Ubicación |
|---|---|---|
| Router | Decide el perfil (`rapido`, `herramientas`, `nube`) | `agent/router.py` |
| Orquestador | Arma el contexto, ejecuta el bucle de herramientas, valida | `agent/orchestrator.py` |
| Proveedor `llamacpp` | Habla con `llama-server` (API compatible con OpenAI) | `connections/llm/llamacpp.py` |
| Proveedor `gemini` | Habla con la API de Google | `connections/llm/gemini.py` |
| Gestor de sidecar | Arranca, vigila y detiene `llama-server` | `src-tauri/src/sidecar.rs` |
| Harness de IA | Valida y ejecuta acciones sobre archivos y apps | `harness_ia/` (ver `HARNESS-IA.md`) |
| Registro de acciones | Auditoría y deshacer | tabla `action_log` |

`lmstudio.py` se mantiene solo como proveedor de desarrollo (mismo protocolo que `llamacpp`).

## 4. Router: cómo decide

**Nivel 1 — por módulo (instantáneo).** Cada módulo declara su perfil en `models.json > routing`.
**Nivel 2 — por intención, solo si es ambiguo.** Lo clasifica el modelo que **ya está cargado**; nunca se cambia de modelo solo para decidir.
**Nivel 3 — escalado por fallo.** JSON inválido, herramienta inexistente o rechazo del harness → un reintento con el mismo modelo → siguiente capa (si la privacidad lo permite) → aviso al usuario.

**Inercia:** si el modelo cargado puede resolver la tarea, no se cambia. Cada cambio cuesta segundos.

**Privacidad** (`models.json > privacy`):
| Valor | Significado |
|---|---|
| `solo_local` | Nunca sale a la nube (Correo y MiPC por defecto) |
| `nube_con_permiso` | Puede escalar si el usuario lo acepta en esa conversación |
| `nube_libre` | Puede escalar sin preguntar (no recomendado) |

La nube **nunca** recibe rutas de archivos, listados ni contenido del sistema.

## 5. Ciclo de vida de `llama-server`
- Tauri lo lanza como sidecar con: `--host 127.0.0.1`, puerto aleatorio, `--api-key` aleatoria, `--models-dir`, `--models-max 1`.
- El puerto y la clave se pasan al backend por variables de entorno.
- Al cerrar la app, Tauri mata los procesos hijos (en Windows, con un **Job Object**) para no dejar VRAM retenida.
- Si el servidor cae: el proveedor reporta `LOCAL_NO_DISPONIBLE`, el backend intenta reiniciar una vez y luego avisa en la isla.
- Si falla la carga por VRAM: reintentar con menos capas en GPU (`-ngl` menor) o menor contexto.

## 6. Flujos de ejemplo

**A. Redacción** — "Redacta un correo para pedir una prórroga"
router(módulo Chat → `rapido`) → Gemma E4B responde en streaming → la isla muestra la insignia del modelo usado.

**B. Acción sobre archivos** — "Mueve los PDF de Descargas a Documentos/Facturas"
router(`acciones_pc` → `herramientas`) → Qwen 9B devuelve llamadas `fs_mkdir` + `fs_move` → **Harness valida** → tarjeta de vista previa (origen → destino) → usuario aprueba → harness ejecuta → reporte generado por el harness con las rutas reales → `action_log`.

**C. Escalado** — pregunta compleja del Chat
`rapido` insuficiente o el usuario pide "usar nube" → si `chat = nube_con_permiso`, la isla pide permiso → Gemini responde.

## 7. Observabilidad (local, sin enviar datos fuera)
Por cada petición se guarda: perfil usado, modelo, tokens/s, tiempo al primer token, reintentos, escalados y errores. Se muestra en Ajustes > Diagnóstico.

## 8. Errores y mensajes
| Código | Situación | Mensaje al usuario |
|---|---|---|
| `LOCAL_NO_DISPONIBLE` | `llama-server` caído | "El motor local no responde. Reintentando…" |
| `MODELO_NO_ENCONTRADO` | Falta el `.gguf` | "Falta el modelo X en la carpeta de modelos" |
| `VRAM_INSUFICIENTE` | Falla la carga | "Cargando con menos GPU; puede ir más lento" |
| `NUBE_SIN_CLAVE` | Sin clave de Gemini | "Configura tu clave en Ajustes" |
| `ACCION_RECHAZADA` | Harness bloquea | Ver `HARNESS-IA.md` |

## 9. Fases
| Fase | Entrega |
|---|---|
| IA-1 | `llama-server` embebido, un modelo local, proveedor `llamacpp`, chat con streaming |
| IA-2 | Harness de IA con pruebas de seguridad |
| IA-3 | Router y segundo modelo (`--models-max 1`) |
| IA-4 | Escalado a Gemini con privacidad |
| IA-5 | Descargador de modelos con verificación de hash (solo si se reparte) |

