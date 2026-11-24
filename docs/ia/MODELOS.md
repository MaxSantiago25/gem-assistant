# MODELOS — Stack de IA definitivo y criterios de elección

## 1. Criterios (en orden de prioridad)
1. **Español sólido** (redacción y comprensión). Si un modelo no lo garantiza, se omite.
2. **Calidad por peso**: la mejor respuesta posible dentro de la memoria disponible.
3. **Cabe en el equipo**: RTX 3050 (6 GB de VRAM) + 16 GB de RAM + i5-13420H.
4. **Llamadas a herramientas fiables** (para la capa de acciones).
5. **Licencia permisiva** (por si la app se reparte).

## 2. Stack final

| Perfil | Modelo | Para qué | Dónde corre |
|---|---|---|---|
| `rapido` | **Gemma 4 E4B QAT** (GGUF) | Chat, redacción, resúmenes cortos, clasificación | Local, completo en GPU |
| `herramientas` | **Qwen 3.5 9B** (GGUF) | Acciones: archivos, tareas, MiPC, correo (llamadas a herramientas) | Local, parte en GPU y parte en RAM |
| `nube` | **Gemini** (modelo definido en Ajustes) | Tareas largas o complejas, solo con permiso | Nube |

### Por qué estos
- **Gemma 4 E4B QAT**: la versión QAT conserva calidad con mucha menos memoria; pesa unos 5–6 GB y cabe en la VRAM con contexto corto. Gemma 4 declara soporte para más de 140 idiomas, incluido el español.
- **Qwen 3.5 9B**: soporta 201 idiomas y dialectos, licencia Apache 2.0, ventana de contexto grande y llamadas a herramientas estructuradas. Ya está descargado.
- **Gemini**: respaldo de máxima calidad; nunca recibe rutas ni listados de archivos.

## 3. Modelos descartados (y por qué)

| Modelo | Decisión | Motivo |
|---|---|---|
| Nemotron 3 Nano 4B | **Omitido** | Muy bueno en herramientas y ligero, pero **la ficha oficial de NVIDIA no confirma español**. Si NVIDIA lo documenta, se reevalúa como capa de acciones. Nota: un directorio externo lo listaba con 4K de contexto, dato que contradice el blog oficial (entrenado hasta 49K); no fiarse de directorios de terceros. |
| Gemma 4 12B / 12B QAT | Descartado | ~7 GB: no cabe en 6 GB de VRAM, es más lento y se solapa con Qwen 9B. |
| Gemma 4 E2B | Solo reserva | Más ligero; usar únicamente si el E4B resulta lento. |
| Qwen 3.5 4B | **Plan B de `herramientas`** | Cabe completo en la GPU. Si el 9B resulta demasiado lento, es el reemplazo. |

## 4. Descarga
| Modelo | Fuente |
|---|---|
| Gemma 4 E4B QAT | Repositorio GGUF `gemma-4-E4B-it-qat-GGUF` (por ejemplo, el de Unsloth en Hugging Face) |
| Qwen 3.5 9B | El GGUF que ya tienes (cuantización Q4_K_M recomendada) |

Carpeta de modelos (desarrollo): `%APPDATA%\IslandAgent\models\`. Si Hugging Face pide aceptar términos de un modelo, hace falta una cuenta gratuita; ninguna cuenta ni clave es necesaria para *ejecutar* los modelos.

## 5. Parámetros recomendados
| Parámetro | Valor | Nota |
|---|---|---|
| Contexto (`-c`) | 8192 (hasta 16384) | Más contexto consume VRAM y empuja a RAM |
| Capas en GPU (`-ngl`) | Gemma E4B: todas · Qwen 9B: las que quepan | Si falla por VRAM, bajar `-ngl` en pasos |
| Gemma 4 muestreo | `temperature 1.0`, `top_p 0.95`, `top_k 64` | Recomendado por Google |
| Qwen 3.5 muestreo | Usar el de su ficha oficial | Para herramientas, temperatura baja |
| Modo razonamiento | **Apagado** por defecto | Encender solo para tareas complejas; verificar el parámetro exacto en la versión de `llama-server` usada |
| Modelos cargados a la vez | 1 (`--models-max 1`) | Límite de 6 GB de VRAM |

## 6. Configuración de perfiles (`backend/config/models.json`)
```json
{
  "profiles": {
    "rapido":       { "provider": "llamacpp", "model": "gemma-4-E4B-it-qat", "ctx": 8192, "thinking": false },
    "herramientas": { "provider": "llamacpp", "model": "qwen3.5-9b",         "ctx": 8192, "thinking": false },
    "nube":         { "provider": "gemini",   "model": "DEFINIR_EN_AJUSTES" }
  },
  "routing": {
    "chat": "rapido",
    "redaccion": "rapido",
    "acciones_pc": "herramientas",
    "tareas": "herramientas",
    "correo_resumen": "rapido"
  },
  "privacy": {
    "correo": "solo_local",
    "mipc": "solo_local",
    "chat": "nube_con_permiso"
  },
  "escalation": { "max_retries_same_model": 1, "escalate_to": ["nube"] }
}
```
Los nombres de modelo deben coincidir con los archivos `.gguf` de la carpeta de modelos.

## 7. Protocolo de prueba (20 minutos, en español)
Probar `Gemma E4B`, `Qwen 9B` y, si hace falta, `Qwen 4B` con las mismas 5 tareas:
1. "Crea una tarea para mañana a las 5 pm: llamar al dentista" → JSON correcto.
2. Resumir un correo de 300 palabras.
3. Pregunta de seguimiento que dependa del mensaje anterior.
4. Elegir entre dos herramientas según la petición.
5. "Responde solo con JSON" con formato estricto.

Registrar por modelo: tokens/segundo, tiempo al primer token, aciertos (0–5) y calidad de español (1–5). Se elige el stack con esos datos.

