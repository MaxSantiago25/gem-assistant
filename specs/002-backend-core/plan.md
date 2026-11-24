# Plan de Implementación — 002 Backend Core y Persistencia

## 1. Contratos de API (`/api/v1`)

### Autenticación y Seguridad
- Todas las rutas privadas requieren la cabecera `X-Island-Token`.
- En caso de token inválido o ausente:
  ```json
  {
    "error": {
      "code": "UNAUTHORIZED",
      "message": "Token de sesión inválido o ausente"
    }
  }
  ```

### Endpoints
| Método | Ruta | Autenticación | Entrada | Salida |
|---|---|---|---|---|
| `GET` | `/health` | Pública | Ninguna | `status`, `service`, `version`, `provider` |
| `POST` | `/auth/logout` | Requerida | Ninguna | `status: "logged_out"` |
| `GET` | `/settings` | Requerida | Ninguna | `{ "settings": { key: value } }` |
| `PUT` | `/settings` | Requerida | `{ "settings": { key: value } }` | `{ "updated": int, "settings": { ... } }` |
| `GET` | `/conversations` | Requerida | Ninguna | `{ "conversations": [ ... ] }` |
| `POST` | `/conversations` | Requerida | `{ "title": str, "provider": str }` | `{ "id": str, "title": str, ... }` |
| `GET` | `/conversations/{id}/messages` | Requerida | Ninguna | `{ "conversation_id": str, "messages": [ ... ] }` |
| `POST` | `/conversations/{id}/messages` | Requerida | `{ "role": "user"|"assistant", "content": str }` | `{ "id": str, "role": str, ... }` |

## 2. Sistema de Migraciones Automáticas (`app/db/migrator.py`)
- Se ejecuta en el ciclo de vida de FastAPI (`lifespan`).
- Lee los archivos en `backend/app/db/migrations/` ordenados lexicográficamente.
- Asegura la tabla `schema_migrations(version TEXT PRIMARY KEY, applied_at TIMESTAMP)`.
- Aplica cada migración pendiente dentro de una transacción segura.

## 3. Capas del Backend
```
API (routers delgados, inyección de dependencias)
  ↓
Services (lógica de negocio pura, sin SQL ni FastAPI)
  ↓
Repositories (único lugar con sentencias SQL a SQLite)
```

## 4. Pruebas
Suite completa con `pytest`:
- Prueba de migrador en base SQLite en memoria.
- Prueba de repositorios (CRUD settings, conversaciones, mensajes).
- Prueba de endpoints con cliente de prueba (`httpx.AsyncClient` / `TestClient`).

