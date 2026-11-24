# Metodología SDD (Spec-Driven Development)

La **especificación es la fuente de verdad**; el código es su consecuencia. Si algo cambia, primero cambia la spec.

## Ciclo

| Fase | Archivo | Responsable | Contenido |
|---|---|---|---|
| 1. Especificar | `specs/NNN-nombre/spec.md` | Arquitectura (con quien pide la función) | Qué y por qué. Historias de usuario, criterios de aceptación. **Sin tecnología.** |
| 2. Planificar | `specs/NNN-nombre/plan.md` | Arquitectura + Backend + Frontend | Cómo: contratos de API, tablas, componentes, riesgos. |
| 3. Tareas | `specs/NNN-nombre/tasks.md` | Cada rol | Lista atómica, ordenada, con dueño y criterio de aceptación enlazado. |
| 4. Implementar | código | Backend / Frontend | Una tarea a la vez. |
| 5. Verificar | checklist en `tasks.md` | Quien implementa + Arquitectura | Se contrasta contra la spec. |

## Un archivo por rol
Cada rol tiene su `.md` en `docs/roles/` con: misión, entradas, salidas, reglas y definición de terminado.
Un rol **no** modifica entregables de otro; abre una petición de cambio en la spec.

## Reglas
1. Sin spec aprobada no hay código.
2. Una spec = una capacidad entregable (ej. "isla y panel", "chat con LM Studio").
3. Los criterios de aceptación son verificables (cumplido / no cumplido).
4. Los contratos entre frontend y backend viven en `plan.md` y se acuerdan antes de implementar.
5. Las dudas se marcan como `[NECESITA ACLARACIÓN]` en lugar de adivinar.

## Plantilla de spec
```md
# NNN — Nombre
## Problema
## Historias de usuario
- Como <quién>, quiero <qué>, para <por qué>.
## Criterios de aceptación
- [ ] CA-1 ...
## Fuera de alcance
## Preguntas abiertas
```

## Hoja de ruta (specs previstas)
| # | Spec | Contenido |
|---|---|---|
| 001 | island-shell | Isla, expansión, panel dividido, navegación, salir |
| 002 | backend-core | FastAPI, SQLite, migraciones, token de sesión |
| 003 | chat-lmstudio | Chat con streaming contra LM Studio |
| 004 | tareas-habitos-enfoque | CRUD y lógica de los tres módulos |
| 005 | gemini-provider | Segundo proveedor y selector en Ajustes |
| 006 | mipc | Información del sistema y acciones con confirmación |
| 007 | correo | Conexión de correo (Gmail) |

