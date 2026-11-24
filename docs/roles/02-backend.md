# Rol 02 — Backend

## Misión
Construir el servicio local en Python que da lógica, datos y conexión con LLMs. Expone una API estable al frontend.

## Entradas
`plan.md` (contratos y tablas) · `01-arquitectura.md` · `HARNESS.md`.

## Salidas
Código en `backend/` · migraciones SQL · pruebas · documentación de endpoints.

## Stack
Python 3.11+ · **FastAPI** + Uvicorn · Pydantic · `sqlite3` de la librería estándar · `httpx` · `keyring` · `psutil` (MiPC) · `pytest`.

## Estructura
```
backend/
├─ app/
│  ├─ main.py                  ← crea la app, registra routers
│  ├─ core/                    ← config.py, security.py (token), logging.py
│  ├─ api/                     ← routers delgados: health, auth, chat, tasks,
│  │                              habits, focus, mail, pc, settings
│  ├─ services/                ← lógica de negocio (sin HTTP ni SQL)
│  ├─ repositories/            ← único lugar con SQL
│  ├─ schemas/                 ← modelos Pydantic de entrada/salida
│  ├─ db/
│  │  ├─ connection.py
│  │  └─ migrations/           ← 0001_init.sql, 0002_...sql
│  ├─ agent/
│  │  ├─ orchestrator.py       ← bucle del agente
│  │  └─ tools/                ← herramientas (crear tarea, info del PC…), con registro
│  └─ connections/             ← ★ TODAS las conexiones externas
│     ├─ base.py               ← interfaz LLMProvider
│     ├─ registry.py           ← elige proveedor activo según Ajustes
│     ├─ llm/
│     │  ├─ lmstudio.py
│     │  └─ gemini.py
│     ├─ mail/                 ← gmail.py (fase 6)
│     └─ README.md             ← cómo añadir una conexión nueva
├─ tests/
├─ requirements.txt
└─ run.py                      ← lee puerto y token del entorno
```

## Reglas de capas
`api` → `services` → `repositories` / `connections`. Un router no contiene lógica ni SQL. Un servicio no importa FastAPI.

## Carpeta `connections/`
Todo contacto con el exterior pasa por aquí. Cada conexión implementa una interfaz común y se registra en `registry.py`.

```python
class LLMProvider(ABC):
    name: str
    async def list_models(self) -> list[str]: ...
    async def chat(self, messages: list[Message], **opts) -> str: ...
    async def stream(self, messages: list[Message], **opts) -> AsyncIterator[str]: ...
    async def health(self) -> bool: ...
```

| Conexión | Detalles |
|---|---|
| **LM Studio** | Servidor local compatible con OpenAI. URL por defecto `http://localhost:1234/v1` (configurable). `GET /models`, `POST /chat/completions` con `stream: true`. Cliente `httpx`. Manejar "servidor apagado" con mensaje claro. |
| **Gemini** | API de Google. SDK oficial `google-genai` (verificar contra su documentación vigente). Clave desde `keyring`. **El nombre del modelo va en Ajustes, no en el código.** |
| **Correo (futuro)** | Gmail API con OAuth; tokens en `keyring`. |

Añadir una conexión = nuevo archivo + registro + entrada en `connections/README.md` + prueba con doble simulado.

## Base de datos (SQLite, `data/island.db`)
- Migraciones numeradas; se aplican al iniciar y se registran en `schema_migrations`.
- Activar `PRAGMA foreign_keys = ON` y modo WAL.
- Esquema inicial propuesto:

| Tabla | Campos principales |
|---|---|
| `settings` | `key` PK, `value`, `updated_at` |
| `conversations` | `id`, `title`, `provider`, `created_at` |
| `messages` | `id`, `conversation_id` FK, `role`, `content`, `created_at` |
| `tasks` | `id`, `title`, `notes`, `status`, `priority`, `due_at`, `created_at`, `done_at` |
| `habits` | `id`, `name`, `frequency`, `archived`, `created_at` |
| `habit_logs` | `id`, `habit_id` FK, `log_date`, `done` · único `(habit_id, log_date)` |
| `focus_sessions` | `id`, `task_id` FK nulo, `started_at`, `ended_at`, `planned_min`, `completed` |
| `schema_migrations` | `version` PK, `applied_at` |

Las claves de API **no** van en esta base de datos.

## Endpoints iniciales (`/api/v1`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio y del proveedor activo |
| POST | `/auth/logout` | Invalida la sesión |
| GET/PUT | `/settings` | Leer y guardar ajustes |
| GET | `/llm/models` | Modelos del proveedor activo |
| POST | `/chat/stream` | Respuesta en SSE |
| GET | `/conversations` | Historial |
| CRUD | `/tasks`, `/habits`, `/focus` | Módulos |
| GET | `/pc/status` | CPU, RAM, disco, batería |

## Seguridad
- Escuchar solo en `127.0.0.1`; puerto y token recibidos por variables de entorno desde Tauri.
- Rechazar toda petición sin `X-Island-Token` válido.
- Sin secretos en logs. Validar toda entrada con Pydantic.
- Herramientas del agente: lista blanca + confirmación para acciones destructivas.

## Pruebas
`pytest` con base SQLite en memoria; proveedores LLM simulados. Cada endpoint tiene al menos un caso feliz y uno de error.

## Definición de terminado (Backend)
- [ ] Cumple los criterios de aceptación de la spec.
- [ ] Capas respetadas y SQL solo en repositories.
- [ ] Conexión externa solo en `connections/`.
- [ ] Migración incluida y probada desde cero.
- [ ] Pruebas pasan.
- [ ] Sin secretos en código ni logs.
- [ ] Grafo de codebase-memory reindexado.

