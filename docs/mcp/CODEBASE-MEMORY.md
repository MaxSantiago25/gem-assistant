# MCP de contexto: codebase-memory-mcp

Da a los agentes un **grafo de conocimiento del código** (funciones, clases, llamadas, rutas HTTP) para que entiendan el proyecto sin leer archivo por archivo. Es un binario único, sin Docker ni API keys, con base SQLite local.
Repositorio oficial: `github.com/DeusData/codebase-memory-mcp`

> No incluye un LLM: usa el del agente cliente (Claude Code, Cursor, etc.) como capa de inteligencia.

## Instalación en Windows (PowerShell)
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1 -OutFile install.ps1
notepad install.ps1        # recomendado: revisar el script antes de ejecutarlo
.\install.ps1
codebase-memory-mcp install   # detecta y registra el MCP en tus agentes (Claude Code, Cursor, etc.)
```
Reinicia tu agente después. Si Windows SmartScreen muestra una advertencia por binario sin firmar, verifica el hash con `checksums.txt` de la release.

Alternativa manual: copiar el bloque de `.mcp.json` (raíz del repo) y apuntar `command` a la ruta completa del `.exe` si no está en el `PATH`.

## Configuración recomendada
```powershell
codebase-memory-mcp config set auto_index true     # indexa al iniciar sesión del agente
codebase-memory-mcp update                         # actualizar
```
Variante con visualizador 3D del grafo (opcional): `codebase-memory-mcp --ui=true --port=9749` y abrir `http://localhost:9749`.

## Uso en este proyecto
1. Abrir el repo con el agente y pedir: *"Indexa este repositorio con codebase-memory"*.
2. Antes de implementar, consultar el grafo: *"¿Qué componentes de UI ya existen?"*, *"¿Dónde se registran los proveedores LLM?"*.
3. Tras cada tarea terminada, **reindexar** para mantener el contexto al día.
4. Desde terminal también se puede invocar: `codebase-memory-mcp cli search_graph '{"name_pattern": ".*Provider.*"}'`.

## Rol dentro del Harness
El MCP es la defensa contra la duplicación: el agente **debe** consultar si ya existe un componente, servicio o conexión antes de crear otro.

## Nota
Las instrucciones de instalación pueden cambiar entre versiones. Ante cualquier diferencia, manda el README del repositorio oficial.

