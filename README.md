# Gem

Asistente inteligente de escritorio para Windows con interfaz tipo isla dinamica en forma de trapezoide. En estado colapsado flota de forma persistente en la parte superior de la pantalla mostrando su mascota interactiva y el reloj; al presionarlo se expande en un panel dividido con navegacion lateral y chat conectado a modelos de inteligencia artificial locales y en la nube.

---

## Descripcion general del proyecto

Gem combina una ventana nativa ligera en el escritorio con un backend local en Python y un router inteligente de modelos de lenguaje:

- **Interfaz de escritorio (Isla Dinamica)**: Ventana sin bordes, transparente y siempre visible (`alwaysOnTop`), construida sobre **Tauri 2 (Rust)** y **JavaScript vanilla** (ES Modules y Custom Elements, sin frameworks ni bundlers).
- **Identidad y animaciones**: Incluye el componente animado `<ui-leopard>` y una esfera de pensamiento (`<ui-thinking-orb>`) que indica cuando el modelo esta procesando una respuesta, siguiendo transiciones suaves estilo macOS definidas en tokens CSS unicos.
- **Router hibrido de IA (Local + Nube)**:
  - **Ejecucion local** mediante `llama-server` (API compatible con OpenAI) con perfiles especializados, por ejemplo **Gemma 4 E4B QAT** para chat rapido y redaccion en espanol, y **Qwen 3.5 9B** para ejecucion de herramientas y acciones en el equipo.
  - **Escalamiento en la nube** opcional hacia **Google Gemini** mediante una capa de proveedores intercambiable, con solicitud explicita de autorizacion al usuario.
- **Seguridad y Harness de ejecucion**: Las acciones sensibles sobre el sistema (como creacion de carpetas o apertura de aplicaciones) pasan por una politica estricta y muestran una tarjeta de confirmacion interactiva dentro de la isla antes de ejecutarse. Las credenciales se almacenan en el Administrador de credenciales de Windows (`keyring`), nunca en codigo ni en SQLite.

---

## Arquitectura y tecnologias

| Capa | Tecnologia | Responsabilidad |
|---|---|---|
| Shell de escritorio | **Tauri 2 (Rust)** | Ventana nativa flotante, posicionamiento superior y puente de comandos |
| Frontend | **JavaScript vanilla + CSS Tokens** | Custom Elements modulares, vista de chat, tarjetas de confirmacion y animaciones |
| Backend | **Python + FastAPI** | API REST local (`127.0.0.1:8765`), router de perfiles de IA y ejecucion controlada |
| Base de datos | **SQLite** | Persistencia local de historial, configuracion y registro de acciones (`data/island.db`) |
| Inferencia local | **llama.cpp (`llama-server`)** | Servidor local en modo router para modelos GGUF |
| Metodologia | **SDD (Spec-Driven Development)** | Especificaciones, planes y tareas en `specs/`, reglas de diseno en `docs/harness/HARNESS.md` |

---

## Estructura del repositorio

```text
Gem/
|- AGENTS.md                  Punto de entrada y reglas para agentes de IA
|- README.md                  Documentacion general del proyecto
|- LICENSE                    Licencia MIT
|- start.bat                  Acceso directo para iniciar servicios e isla nativa
|- start_project.ps1          Script de arranque (llama-server, FastAPI, frontend y Tauri)
|- run_llama_dev.ps1          Configuracion de arranque para llama-server
|- docs/
|  |- harness/HARNESS.md      Reglas estrictas de diseno, colores, tipografia y modularidad
|  |- mcp/CODEBASE-MEMORY.md  Guia de uso del grafo de conocimiento codebase-memory-mcp
|  |- roles/                  Definicion de responsabilidades por rol (Arquitectura, Backend, Frontend)
|  `- sdd/METODOLOGIA-SDD.md  Flujo de trabajo basado en especificaciones
|- specs/                     Especificaciones tecnicas, planes y listas de tareas (001 - 008)
|- src-tauri/                 Shell nativo en Rust (Tauri 2)
|- frontend/                  Interfaz web modular en JS vanilla y CSS
|- backend/
|  |- app/
|  |  |- agent/               Orquestador de chat, herramientas y flujo de confirmacion
|  |  |- connections/         Capa aislada para conexiones externas (LLM local y nube)
|  |  |- db/                  Conexion SQLite y migraciones
|  |  `- routes/              Endpoints FastAPI (salud, chat, acciones, configuracion)
|  `- tests/                  Pruebas automatizadas con pytest
`- .github/workflows/         Flujos de integracion continua con GitHub Actions
```

---

## Requisitos y ejecucion local (Windows 10/11)

1. **Python 3.11+**: Instalar dependencias del backend:
   ```powershell
   pip install -r backend/requirements.txt
   ```
2. **Rust y Cargo** (opcional si deseas recompilar `src-tauri`):
   ```powershell
   cd src-tauri
   cargo build
   ```
3. **Inferencia local (opcional para IA offline)**: Tener `llama-server` (`llama.cpp`) y los modelos GGUF configurados en `run_llama_dev.ps1`.
4. **Iniciar Gem**:
   Ejecuta desde PowerShell o haciendo doble clic en `start.bat`:
   ```powershell
   .\start.bat
   ```

---

## Pruebas

Para ejecutar las pruebas unitarias e integracion del backend:

```powershell
$env:PYTHONPATH = "backend"
pytest backend/tests
```

---

## Autor

Desarrollado por **Maximiliano Santiago Felix**, estudiante de la carrera de **Ingenieria en Sistemas Computacionales** del **Instituto Tecnologico de Ciudad Madero**.

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para mas detalles.
