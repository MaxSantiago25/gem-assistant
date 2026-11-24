# CONEXIÓN CON LOS MODELOS — Qué necesita el agente constructor

## 1. Respuesta corta
**Para los modelos locales no hace falta ninguna API key ni cuenta.** `llama.cpp` es un programa de código abierto que corre en tu PC; el backend se conecta directamente a su servidor local por HTTP. No es una API de Meta ni "de tu perfil de Llama".

La única clave involucrada en lo local es un **token interno aleatorio** que genera la propia app en cada arranque para que otros programas de tu PC no usen el servidor. No lo creas ni lo guardas tú.

Solo **Gemini** necesita una clave real.

## 2. Qué necesita cada conexión

| Conexión | Cuenta / clave | Cómo se conecta | Qué hay que darle al agente |
|---|---|---|---|
| `llama-server` (local) | Ninguna | `http://127.0.0.1:{puerto}/v1` (API compatible con OpenAI) | Ruta del ejecutable, carpeta de modelos, nombres de los `.gguf`, parámetros |
| LM Studio (solo desarrollo) | Ninguna | `http://localhost:1234/v1` | Nada; se mantiene como alternativa |
| Gemini (nube) | **API key** de Google AI Studio | SDK `google-genai` | Una variable de entorno en desarrollo; nunca la clave en texto |

## 3. Instalar el motor en Windows (una sola vez)
1. Instalar `llama.cpp` con winget (`winget install llama.cpp`) o descargar la build **CUDA** para Windows desde las releases oficiales (con las DLL de CUDA que acompañan).
2. Comprobar el ejecutable con `--help`. Según el paquete puede llamarse `llama-server` o usarse como subcomando; **el agente debe verificar el nombre y los parámetros reales con `--help`** antes de escribir código.
3. Confirmar que existen las opciones del modo router: `--models-dir`, `--models-max`, `--models-preset`.
4. Crear la carpeta de modelos: `%APPDATA%\IslandAgent\models\` y copiar ahí los `.gguf`.

Prueba manual:
```powershell
llama-server --models-dir "$env:APPDATA\IslandAgent\models" --models-max 1 -c 8192 -ngl 99 --host 127.0.0.1 --port 8080
# en otra terminal:
curl http://127.0.0.1:8080/v1/models
```
Debe listar los modelos. Si responde, la conexión es directa; el agente no necesita nada más.

## 4. Clave de Gemini
1. Crear una API key en **Google AI Studio** (cuenta de Google).
2. **Desarrollo:** archivo `backend/.env` (ignorado por git) con `GEMINI_API_KEY=...`. Ver `.env.example`.
3. **Producción:** se escribe en Ajustes y se guarda en el Administrador de credenciales de Windows (`keyring`).
4. El nombre del modelo de Gemini se elige en Ajustes, no en el código.
5. **Nunca** pegues la clave en el chat con el agente, en un `.md` ni en un commit.

`.env.example`:
```
GEMINI_API_KEY=
LLAMA_SERVER_PATH=C:\ruta\a\llama-server.exe
MODELS_DIR=%APPDATA%\IslandAgent\models
```

## 5. Checklist: qué darle al agente constructor
- [ ] El repositorio con `AGENTS.md` y `docs/` (incluida esta carpeta `docs/ia/`).
- [ ] Ruta del ejecutable de `llama.cpp` (`LLAMA_SERVER_PATH`).
- [ ] Carpeta de modelos y nombres exactos de los archivos `.gguf`.
- [ ] Límites del equipo: 6 GB de VRAM, 16 GB de RAM, Windows.
- [ ] `backend/.env` con la clave de Gemini (solo si se llega a la fase IA-4).
- [ ] Acceso al MCP `codebase-memory-mcp` ya indexado.
- [ ] Las specs 005 y 008 aprobadas.

## 6. Prompt para el agente constructor
```
Lee AGENTS.md y luego docs/ia/ARQUITECTURA-IA.md, docs/ia/MODELOS.md y docs/ia/HARNESS-IA.md.
Consulta primero el MCP codebase-memory para ver qué existe.

Objetivo de esta tarea: fase IA-1 de ARQUITECTURA-IA.md.
- Crea backend/app/connections/llm/base.py (interfaz LLMProvider) y llamacpp.py.
- llamacpp.py se conecta por HTTP a http://127.0.0.1:{LLAMA_PORT}/v1 con la cabecera
  Authorization: Bearer {LLAMA_API_KEY}. No hay cuentas ni claves externas para lo local.
- Lee puerto y token desde variables de entorno (los define Tauri en producción;
  en desarrollo, un script run_llama_dev.ps1 que tú crearás).
- Implementa list_models, chat, stream (SSE) y health. Maneja LOCAL_NO_DISPONIBLE,
  MODELO_NO_ENCONTRADO y VRAM_INSUFICIENTE según ARQUITECTURA-IA.md §8.
- Antes de escribir parámetros de llama-server, ejecuta --help y verifica los nombres reales.
- Perfiles y rutas salen de backend/config/models.json (MODELOS.md §6).
- Pruebas con un servidor simulado. Cumple el Harness de código (HARNESS.md).
- No toques el Harness de IA en esta tarea. No guardes secretos en código ni logs.
Al terminar: reindexa codebase-memory y marca los criterios de la spec 005 que cumpliste.
```

## 7. Notas
- Si `llama-server` pide un modelo y no hay VRAM, el proveedor debe reintentar con menos capas en GPU, no fallar de inmediato.
- Los puertos son aleatorios en producción; el `8080` de arriba es solo para la prueba manual.

