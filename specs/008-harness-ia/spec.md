# 008 — Harness de IA (acciones seguras sobre el PC)

## Problema
El agente debe organizar archivos y abrir aplicaciones por el usuario, pero una IA no debe poder borrar ni modificar nada ni ejecutar comandos, y el usuario debe saber siempre qué se movió y de dónde a dónde.

## Historias de usuario
- Como usuario, quiero que el agente mueva archivos y carpetas entre carpetas que yo permito.
- Como usuario, quiero que cree carpetas nuevas y renombre archivos.
- Como usuario, quiero que abra aplicaciones y archivos que yo autorice.
- Como usuario, quiero ver antes de ejecutar qué se va a mover y a dónde mediante una tarjeta de confirmación.
- Como usuario, quiero que siempre me diga la ruta de origen y la de destino de cada movimiento.
- Como usuario, quiero poder deshacer lo que el agente hizo.
- Como usuario, quiero tener la certeza de que el agente no puede borrar ni editar mis archivos.

## Criterios de aceptación
- [x] CA-1 El agente solo opera dentro de zonas permitidas (por defecto Descargas, Documentos y Escritorio) editables en Ajustes.
- [x] CA-2 Carpetas del sistema y de otras cuentas nunca son accesibles, aunque se añadan como zona.
- [x] CA-3 No existe ninguna acción de borrar, editar contenido ni ejecutar comandos.
- [x] CA-4 Mover o renombrar nunca sobrescribe un archivo existente.
- [x] CA-5 Mover entre discos se rechaza con un mensaje claro.
- [x] CA-6 Antes de ejecutar, el usuario ve una tarjeta de confirmación con origen → destino de cada acción y debe aprobarla explícitamente (aplica tanto a mover como a crear carpetas).
- [x] CA-7 Tras ejecutar, se muestra un reporte con ruta de origen y de destino exactas de cada elemento.
- [x] CA-8 El reporte lo produce el sistema, no el modelo.
- [x] CA-9 Si una acción del lote no es válida, no se ejecuta ninguna del lote.
- [x] CA-10 Cada acción queda en un historial consultable y se puede deshacer.
- [x] CA-11 Solo se pueden abrir aplicaciones de una lista que el usuario registró (únicamente Google Chrome).
- [x] CA-12 No se pueden abrir archivos ejecutables o de comandos.
- [x] CA-13 Un lote tiene un máximo de operaciones configurable (50 operaciones).
- [x] CA-14 Textos maliciosos en nombres de archivo o correos no cambian lo que el agente propone ejecutar sin aprobación.

## Fuera de alcance
Leer contenido de archivos, copiar, mover entre discos, acciones en red.

## Preguntas resueltas
- ¿Auto-aprobar la creación de carpetas? Resuelto: No, siempre debe mostrarse la tarjeta de confirmación en la interfaz antes de ejecutar `fs_mkdir`.
- ¿Cuánto tiempo se conserva el historial de acciones? Resuelto: 30 días o hasta limpieza manual del usuario.
- ¿Qué aplicaciones entran en la lista blanca inicial? Resuelto: Únicamente el navegador predeterminado: Google Chrome (`chrome`).
