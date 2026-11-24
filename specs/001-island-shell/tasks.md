# Tareas — 001 Island Shell

| ID | Tarea | Rol | Criterio de Aceptación | Estado |
|---|---|---|---|---|
| T-1.1 | Crear estructura base del proyecto (`frontend/`, `src-tauri/`, `backend/`, `data/`) y organizar documentación en `docs/` y `specs/` | Arquitectura | CA-1, CA-4 | [x] Hecho |
| T-1.2 | Definir `tokens.css` estricto con los 3 colores base, derivadas con `color-mix()`, tipografías y curvas de movimiento macOS | Frontend | CA-9, CA-10, CA-11 | [x] Hecho |
| T-1.3 | Crear `@font-face` y configuración de fuentes locales (Montserrat, Inter, Lato) y `base.css` transparente | Frontend | CA-10 | [x] Hecho |
| T-1.4 | Crear `frontend/assets/icons/sprite.svg` con todos los iconos requeridos en formato SVG (Lucide: home, chat, tasks, habits, focus, mail, pc, settings, logout, chevron, close, status, check) | Frontend | CA-5 | [x] Hecho |
| T-1.5 | Implementar Custom Element `ui-icon` que consume el sprite SVG | Frontend | CA-5 | [x] Hecho |
| T-1.6 | Implementar Custom Element `ui-button` con variantes (primary, ghost, icon) y tamaños (sm, md, lg) | Frontend | CA-9 | [x] Hecho |
| T-1.7 | Implementar Custom Element `ui-badge` y `ui-card` para estados vacíos y tarjetas de resumen | Frontend | CA-12 | [x] Hecho |
| T-1.8 | Implementar Custom Element `ui-nav-item` con soporte para selección activa y variante especial "logout" discreta | Frontend | CA-4, CA-6 | [x] Hecho |
| T-1.9 | Implementar Custom Element `ui-panel` como contenedor base | Frontend | CA-4, CA-7 | [x] Hecho |
| T-1.10 | Implementar el orquestador `ui-island` con píldora colapsada (320x40/360x44), animación a panel (~420ms), backdrop de clic fuera y Esc | Frontend | CA-1, CA-3, CA-8, CA-11 | [x] Hecho |
| T-1.11 | Implementar la barra lateral izquierda con los 8 módulos en orden y "Salir" al fondo integrado al fondo sin apariencia de botón | Frontend | CA-4, CA-6 | [x] Hecho |
| T-1.12 | Implementar el enrutador (`router.js`) y módulos con transición suave de 8px + fundido y estados vacíos ("Próximamente") | Frontend | CA-7, CA-12 | [x] Hecho |
| T-1.13 | Implementar `tauri-bridge.js` para comunicación con Tauri 2 (redimensión de ventana, centrado, atajos, arrastre) y modo fallback para web | Frontend | CA-1, CA-2, CA-3, CA-8 | [x] Hecho |
| T-1.14 | Crear configuración de Tauri 2 (`tauri.conf.json`) y código en Rust (`src-tauri/`) para ventana sin bordes, transparente, always on top y skip taskbar | Backend/Tauri | CA-1, CA-2 | [x] Hecho |
| T-1.15 | Estructurar scaffold base de `backend/` para preparación de Fase 2 | Backend | ADR-2 | [x] Hecho |
| T-1.16 | Verificación integral contra todos los criterios de aceptación CA-1 a CA-12 y checklist de Harness | Todos | CA-1 a CA-12 | [x] Hecho |
| T-1.17 | Reindexar proyecto en `codebase-memory-mcp` | Todos | DoD | [x] Hecho |
