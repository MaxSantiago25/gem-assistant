# Plan de Implementación — 001 Island Shell

## 1. Arquitectura y ciclo de vida de la ventana

### Estrategia de ventana dinámica (ADR-7)
La ventana de Tauri 2 se configura como:
- `transparent: true`, `decorations: false`, `alwaysOnTop: true`, `skipTaskbar: true`.
- Tamaño colapsado: `360px` ancho × `72px` alto (centrado arriba con margen superior de 16px).
- Tamaño expandido: `940px` ancho × `600px` alto.

### Secuencia de transición
1. **Expansión**:
   - Se invoca `tauriBridge.setWindowExpanded(true)`.
   - Tauri redimensiona la ventana a 940 × 600 y la recentra.
   - `ui-island` pasa al estado `expanded` activando la animación CSS (`420ms` con `--ease-mac`).
2. **Contracción**:
   - Se activa la animación CSS de contracción en `ui-island`.
   - Al cumplirse la duración de la animación (`420ms`), se invoca `tauriBridge.setWindowExpanded(false)`.
   - Tauri reduce la ventana a 360 × 72.
3. **Modo Web / Fallback**:
   - `tauri-bridge.js` detecta si `window.__TAURI__` está disponible. Si no lo está (por ejemplo al previsualizar en navegador o entorno de pruebas), simula las llamadas sin arrojar error.

## 2. Catálogo de componentes (Custom Elements JS Vanilla)

| Componente | Archivo | Responsabilidad |
|---|---|---|
| `ui-icon` | `components/ui-icon/ui-icon.js` | Renderiza `<svg><use href="assets/icons/sprite.svg#icon-{name}"></svg>`. Sin emojis. |
| `ui-button` | `components/ui-button/ui-button.js` | Botón accesible con variantes `primary`, `ghost`, `icon` y tamaños `sm`, `md`, `lg`. |
| `ui-nav-item` | `components/ui-nav-item/ui-nav-item.js` | Ítem de navegación lateral. Admite icono, etiqueta, estado activo y variante `logout`. |
| `ui-badge` | `components/ui-badge/ui-badge.js` | Píldora de estado en Montserrat. |
| `ui-card` | `components/ui-card/ui-card.js` | Contenedor de contenido o estado vacío. |
| `ui-panel` | `components/ui-panel/ui-panel.js` | Panel contenedor base con scroll suave y padding tokenizado. |
| `ui-island` | `components/ui-island/ui-island.js` | Orquestador de la isla (píldora compacta y panel extendido de 2 columnas). |

## 3. Navegación y módulos

El menú izquierdo (`nav-menu`) contiene en orden estricto (CA-4):
1. **Inicio** (`home`)
2. **Chat** (`chat`)
3. **Tareas** (`tasks`)
4. **Hábitos** (`habits`)
5. **Enfoque** (`focus`)
6. **Correo** (`mail`)
7. **MiPC** (`pc`)
8. **Ajustes** (`settings`)
9. **Salir** (`logout`) — ubicado al fondo, integrado al fondo, sin aspecto de botón (CA-6).

Los módulos 2 a 8 muestran un estado vacío coherente ("Próximamente") diseñado con `ui-card` y `ui-badge` (CA-12).
El módulo **Inicio** muestra un resumen estructurado del día con tarjetas de estado del agente, tareas rápidas, hábitos del día y enfoque.

## 4. Contratos de eventos y atajos
- `keydown` con `Escape`: si la isla está expandida, se contrae a píldora (CA-8).
- `pointerdown` fuera del contenedor de la isla: contrae la isla (CA-8).
- Clic en la píldora: expande la isla (CA-3).
- Atajo de teclado en app: `Escape`, flechas `ArrowUp`/`ArrowDown` para navegar el menú.
- Atajo global Tauri: `Ctrl+Alt+Space`.

## 5. Tokens CSS y Sistema Visual
- Archivo central: `frontend/src/styles/tokens.css`.
- Fondo: `#191919`.
- Texto: `#EFEFEF`.
- Acento: `#9D00FF` (vivid purple).
- Superficies y bordes derivados con `color-mix(in srgb, ...)`.
- Fuentes: Montserrat (`--font-brand`), Inter (`--font-ui`), Lato (`--font-body`).
- Soporte para `prefers-reduced-motion: reduce` que colapsa duraciones a `1ms` (CA-11).

## 6. Riesgos y mitigaciones
- **Transparencia en WebView2/Windows**: Requiere `tauri.conf.json` con `transparent: true` y fondo HTML/body en `transparent`.
- **Clic fuera en ventana transparente**: La ventana en modo expandido debe detectar clics en el backdrop transparente para cerrar la isla.

