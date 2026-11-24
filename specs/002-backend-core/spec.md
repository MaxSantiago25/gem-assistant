# 002 — Backend Core y Persistencia

## Problema
El frontend del Island Agent necesita conectarse a un servicio local seguro y persistente que gestione la configuración, el token de sesión, la ejecución automática de migraciones en SQLite y la persistencia de conversaciones y mensajes.

## Historias de usuario
- Como usuario, quiero que la aplicación inicialice y mantenga actualizada su base de datos local SQLite de forma transparente al iniciar.
- Como frontend, quiero consultar la salud del servicio (`/health`) y saber qué proveedor de inteligencia artificial está activo y disponible.
- Como frontend, quiero consultar y guardar preferencias de usuario en un almacén persistente clave-valor (`/settings`).
- Como usuario, quiero que mis conversaciones con el agente queden guardadas localmente para poder consultar su historial.
- Como usuario, quiero que toda comunicación entre el frontend y el backend esté protegida por un token de sesión de arranque (`X-Island-Token`), impidiendo que otros procesos de la máquina interactúen con el agente.

## Criterios de aceptación
- [x] CA-1 El backend inicia en `127.0.0.1` en el puerto especificado por la variable de entorno `ISLAND_PORT` (por defecto `8765`).
- [x] CA-2 El endpoint público `GET /api/v1/health` responde sin requerir autenticación, indicando el estado del servicio y del proveedor activo.
- [x] CA-3 Todas las demás rutas de la API bajo `/api/v1` requieren la cabecera `X-Island-Token`. Si el token falta o es incorrecto, responde `401 Unauthorized` con formato de error estándar `{ "error": { "code": "UNAUTHORIZED", "message": "..." } }`.
- [x] CA-4 Al iniciar la aplicación, se aplican automáticamente todas las migraciones SQL pendientes en `data/island.db` y se registran en la tabla `schema_migrations`.
- [x] CA-5 Modo WAL (`PRAGMA journal_mode = WAL`) y claves foráneas (`PRAGMA foreign_keys = ON`) quedan activados en cada conexión a SQLite.
- [x] CA-6 El endpoint `GET /api/v1/settings` devuelve todos los ajustes como un mapa JSON.
- [x] CA-7 El endpoint `PUT /api/v1/settings` actualiza o inserta claves de ajuste con validación mediante Pydantic.
- [x] CA-8 El endpoint `GET /api/v1/conversations` devuelve la lista de conversaciones ordenadas por fecha de creación descendente.
- [x] CA-9 El endpoint `POST /api/v1/conversations` crea una nueva conversación asignándole un identificador único (UUID).
- [x] CA-10 El endpoint `GET /api/v1/conversations/{id}/messages` devuelve los mensajes de una conversación ordenados cronológicamente.
- [x] CA-11 Arquitectura en capas estricta: `api` (routers delgados) → `services` (lógica de negocio pura) → `repositories` (único lugar con sentencias SQL).
- [x] CA-12 Suite de pruebas con `pytest` que verifica endpoints, migraciones y repositorios usando base de datos aislada en memoria.

## Fuera de alcance
Streaming en tiempo real de tokens LLM (corresponde a Spec 003 — Chat LM Studio).
CRUD de tareas, hábitos y sesiones de enfoque (Spec 004).

