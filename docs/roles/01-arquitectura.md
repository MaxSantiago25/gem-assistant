# Rol 01 — Arquitectura

## Misión
Definir y proteger la estructura del sistema. Escribe las specs y los contratos entre Frontend y Backend; no escribe features.

## Entradas
Ideas y necesidades del producto · `HARNESS.md` · grafo de codebase-memory.

## Salidas
`spec.md` y `plan.md` de cada capacidad · diagramas · decisiones (ADR) · contratos de API.

## 1. Vista general
```
┌────────────────────────── Windows ───────────────────────────┐
│  Tauri (Rust)                                                 │
│  ├─ Ventana: sin bordes, transparente, siempre visible        │
│  ├─ Lanza y vigila el backend (sidecar)                       │
│  └─ Genera token de sesión y puerto → los pasa a ambos lados  │
│                                                               │
│  Frontend (JS vanilla, WebView2) ◄── HTTP/SSE ──► Backend     │
│                                       127.0.0.1    (FastAPI)  │
│                                                      │        │
│                                  ┌───────────────────┼─────┐  │
│                                  │ SQLite (data/)    │     │  │
│                                  │ connections/      ▼     │  │
│                                  │  ├─ LM Studio (local)   │  │
│                                  │  └─ Gemini (nube)       │  │
│                                  └─────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## 2. Decisiones clave (ADR resumidos)
| # | Decisión | Motivo |
|---|---|---|
| ADR-1 | Tauri 2 | Ligero, ventanas transparentes y siempre visibles nativas |
| ADR-2 | Backend Python como proceso local | Ecosistema de IA y fácil conexión con LLMs |
| ADR-3 | HTTP + SSE en `127.0.0.1` | Simple, depurable, permite streaming de tokens |
| ADR-4 | Token de sesión por arranque | Evita que otros procesos locales usen el backend |
| ADR-5 | SQLite | Un archivo, cero instalación, suficiente para uso personal |
| ADR-6 | Capa de proveedores LLM | Cambiar LM Studio ↔ Gemini sin tocar el resto |
| ADR-7 | Ventana de tamaño variable con animación CSS | Ver sección 3 |

## 3. La isla: estrategia de ventana (ADR-7)
Una ventana nativa no se anima con suavidad al cambiar de tamaño. Por eso:
- **Expandir**: 1) Tauri agranda la ventana (transparente, instantáneo) → 2) CSS anima la píldora hasta el panel.
- **Contraer**: 1) CSS anima el panel hasta la píldora → 2) al terminar, Tauri reduce la ventana.
- El fondo de la ventana es transparente; solo la isla es visible.
- Posición: centrada arriba en el monitor principal, con un margen superior pequeño.

Configuración base de la ventana (`tauri.conf.json`, validar contra la documentación vigente de Tauri 2):
```json
{
  "app": {
    "withGlobalTauri": true,
    "windows": [{
      "label": "island",
      "decorations": false,
      "transparent": true,
      "alwaysOnTop": true,
      "skipTaskbar": true,
      "resizable": false,
      "shadow": false,
      "width": 360, "height": 72
    }]
  }
}
```
Permisos mínimos en `capabilities`: set-size, set-position, center, start-dragging, close. Nada más.

## 4. Estructura del repositorio
```
island-agent/
├─ src-tauri/
│  ├─ src/            ← main.rs, sidecar.rs, window.rs
│  ├─ capabilities/
│  └─ tauri.conf.json
├─ frontend/          ← ver rol 03
├─ backend/           ← ver rol 02
├─ data/              ← island.db (git-ignored)
├─ docs/  specs/  AGENTS.md  .mcp.json
```

## 5. Módulos funcionales
| Módulo | Qué hace | Fase |
|---|---|---|
| Inicio | Resumen del día: tareas, hábitos, enfoque, estado del agente | 1 |
| Chat | Conversación con el LLM, streaming, historial | 2 |
| Tareas | CRUD, prioridades, fechas; el agente puede crearlas | 3 |
| Hábitos | Rachas y registro diario | 3 |
| Enfoque | Temporizador tipo pomodoro y sesiones registradas | 3 |
| Correo | Lectura, resumen y borradores (Gmail) | 6 |
| MiPC | Estado del sistema y acciones con confirmación | 5 |
| Ajustes | Proveedor LLM, claves, apariencia, atajos | 2+ |
| Salir | Cerrar sesión (ver 7) | 1 |

## 6. Contratos transversales
- **Base URL**: `http://127.0.0.1:{puerto}/api/v1`
- **Autenticación**: cabecera `X-Island-Token` en cada petición.
- **Errores**: `{ "error": { "code": "string", "message": "string" } }`
- **Streaming de chat**: `POST /chat/stream` → eventos SSE `token`, `done`, `error`.
- **CORS**: solo el origen de la app Tauri (en Windows, `http://tauri.localhost`; verificar).
- **Versionado**: prefijo `/v1`; los cambios incompatibles requieren nueva spec.

## 7. Sesión y "Salir"
Definición propuesta [NECESITA ACLARACIÓN]: **Salir = cerrar sesión** → invalida el token de sesión, borra claves en memoria, colapsa la isla y muestra pantalla de bloqueo. **No** borra datos. Cerrar la aplicación por completo se ofrece aparte (menú de bandeja o Ajustes).

## 8. Seguridad
- Backend escucha solo en `127.0.0.1`, puerto aleatorio.
- Claves de API en Windows Credential Manager (`keyring`), nunca en SQLite ni en logs.
- Acciones peligrosas del agente (borrar, ejecutar, enviar correo) requieren **confirmación explícita** del usuario.
- Lista blanca de herramientas que el agente puede invocar.

## 9. Fases
F0 andamiaje → F1 isla y shell → F2 backend + chat LM Studio → F3 tareas/hábitos/enfoque → F4 Gemini → F5 MiPC → F6 correo.

## Definición de terminado (Arquitectura)
- [ ] La spec tiene criterios verificables y sin tecnología.
- [ ] El plan define contratos de API y tablas.
- [ ] Frontend y Backend firmaron el contrato.
- [ ] No contradice el Harness ni las ADR.

