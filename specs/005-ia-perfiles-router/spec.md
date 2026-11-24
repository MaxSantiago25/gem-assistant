# 005 — IA: perfiles, router y proveedores

## Problema
El usuario quiere un agente que responda bien en español, rápido y sin depender de internet, pero que pueda apoyarse en un modelo en la nube cuando la tarea lo requiera, sin sacrificar su privacidad.

## Historias de usuario
- Como usuario, quiero que el agente responda en español con buena calidad aunque no tenga internet.
- Como usuario, quiero que las acciones en mi PC las ejecute un modelo fiable con herramientas (Qwen 3.5 9B), y la redacción un modelo más ágil (Gemma 4 E4B QAT).
- Como usuario, quiero saber qué modelo respondió cada mensaje.
- Como usuario, quiero decidir en cada ocasión individual si una consulta puede usar la nube.
- Como usuario, quiero que mis correos y datos del PC nunca salgan a la nube.
- Como usuario, quiero que la app arranque y detenga el motor de IA sola, sin abrir otros programas.

## Criterios de aceptación
- [x] CA-1 Con el motor local activo, el chat responde en español con streaming visible.
- [x] CA-2 Existen tres perfiles: `rapido`, `herramientas` y `nube`, configurables en Ajustes.
- [x] CA-3 Cada respuesta muestra una insignia con el perfil/modelo usado.
- [x] CA-4 Las peticiones de acciones sobre el PC usan el perfil `herramientas`; chat y redacción usan `rapido`.
- [x] CA-5 Solo hay un modelo local cargado a la vez; cambiar de perfil no bloquea la interfaz.
- [x] CA-6 Si el modelo cargado puede resolver la tarea, no se cambia de modelo.
- [x] CA-7 Ante un fallo de formato o herramienta, se reintenta una vez y luego se escala; si la privacidad lo prohíbe, se avisa al usuario.
- [x] CA-8 Correo y MiPC son "solo local" por defecto; la nube nunca recibe rutas ni listados de archivos.
- [x] CA-9 Para usar la nube en el Chat se pide permiso al usuario en cada ocasión individual (no se recuerda permanentemente).
- [x] CA-10 Sin clave de Gemini, el sistema funciona en modo local y pide la clave solo al intentar escalar.
- [x] CA-11 Cerrar la app libera la memoria de la GPU (no quedan procesos del motor).
- [x] CA-12 Si el motor local no responde, el usuario ve un mensaje claro y la app intenta recuperarse.
- [x] CA-13 El diagnóstico muestra por petición: perfil, tokens/segundo y tiempo al primer token.

## Fuera de alcance
Descarga automática de modelos, voz, visión, ajuste fino de modelos.

## Preguntas resueltas
- Modelo de Gemini por defecto: `gemini-2.5-flash`.
- ¿El permiso de nube se recuerda por conversación o por sesión? Resuelto: Se solicita en cada ocasión individualmente para máxima privacidad.
