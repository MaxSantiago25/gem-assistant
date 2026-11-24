# Rol 03 — Frontend

## Misión
Construir la isla y el panel con JavaScript vanilla, siguiendo el Harness al pie de la letra: componentes reutilizables, tokens únicos y animación limpia estilo macOS.

## Entradas
`plan.md` (contratos de API y componentes) · `HARNESS.md` · diseño de la isla.

## Salidas
Código en `frontend/` · catálogo de componentes · checklist visual.

## Stack
HTML + CSS + **JavaScript ES modules** · **Custom Elements** para componentes · API de Tauri vía `window.__TAURI__` · sin framework, sin bundler.

## Estructura
```
frontend/
├─ index.html
├─ assets/
│  ├─ fonts/                    ← Montserrat, Inter, Lato (woff2, locales)
│  └─ icons/sprite.svg          ← sprite único de iconos
└─ src/
   ├─ main.js                   ← arranque
   ├─ styles/
   │  ├─ tokens.css             ← ★ única fuente de colores, fuentes, motion
   │  ├─ fonts.css              ← @font-face
   │  └─ base.css               ← reset y estilos globales
   ├─ components/               ← ★ catálogo reutilizable (ver Harness §5)
   │  ├─ ui-icon/  ui-button/  ui-nav-item/  ui-panel/  ui-card/
   │  ├─ ui-input/  ui-badge/  ui-toggle/  ui-list-item/
   │  └─ ui-island/             ← píldora + panel expandible
   ├─ modules/                  ← una carpeta por sección del menú
   │  ├─ home/  chat/  tasks/  habits/  focus/  mail/  pc/  settings/
   ├─ core/
   │  ├─ api-client.js          ← fetch + token + SSE
   │  ├─ tauri-bridge.js        ← tamaño/posición de ventana
   │  ├─ store.js               ← estado mínimo observable
   │  ├─ router.js              ← cambio de módulo
   │  └─ events.js
   └─ utils/
```
Cada componente: `nombre.js` + `nombre.css`. Los módulos **componen** componentes; no crean estilos propios de base.

## La isla (`ui-island`)
| Estado | Tamaño visual | Contenido |
|---|---|---|
| **collapsed** | píldora ~ 320 × 40, `--radius-pill` | Icono del agente, estado ("Listo", "Pensando…"), hora o temporizador de enfoque |
| **expanded** | panel ~ 920 × 580, `--radius-lg` | División en dos partes (abajo) |

Comportamiento:
- **Clic en la píldora** → expande. **Esc**, clic fuera o botón de colapsar → contrae.
- Secuencia de ventana: ver ADR-7 en `01-arquitectura.md` (la ventana crece antes de animar y se reduce después).
- Indicador de actividad del agente: pulso suave en `--color-accent` cuando piensa o escucha.
- Arrastrable por la píldora para reubicarla (`startDragging`), con la posición recordada en Ajustes.

## Panel expandido
```
┌───────────────┬──────────────────────────────────────────┐
│ ○ Island      │                                          │
│               │                                          │
│ [i] Inicio    │         Contenido del módulo activo      │
│ [i] Chat      │                                          │
│ [i] Tareas    │                                          │
│ [i] Hábitos   │                                          │
│ [i] Enfoque   │                                          │
│ [i] Correo    │                                          │
│ [i] MiPC      │                                          │
│ [i] Ajustes   │                                          │
│               │                                          │
│ [i] Salir     │                                          │
└───────────────┴──────────────────────────────────────────┘
```
- **Izquierda (~220 px)**: navegación con `ui-nav-item`. Orden: Inicio, Chat, Tareas, Hábitos, Enfoque, Correo, MiPC, Ajustes.
- **Iconos**: `home, chat, tasks, habits, focus, mail, pc, settings, logout` desde el sprite. **Nada de emojis.**
- **Salir (cerrar sesión)** abajo del todo: debe verse **integrado al fondo, no como botón**. Es un `ui-nav-item` sin relleno, sin borde y sin acento morado; solo icono + texto en `--color-text-muted`, y un leve tinte `--color-surface-hover` al pasar el cursor. La barra lateral usa el mismo `--color-bg` que el resto, separada solo por un borde sutil.
- **Derecha**: el módulo activo. Cambio con fundido + desplazamiento de 8 px (`--dur-base`, `--ease-mac`).
- Elemento activo del menú: fondo `--color-surface` y icono en `--color-accent`.

## Reglas específicas
1. **Cero hex y cero `font-family` fuera de `tokens.css`.**
2. **Reutilizar**: un `ui-button` en tres tamaños, no tres botones.
3. Redimensionar con `size="sm|md|lg"` y variables CSS, no con clases ad hoc.
4. Animar solo `transform`, `opacity`, `border-radius`, `clip-path`.
5. Accesibilidad: foco visible, navegación por teclado (↑/↓ en el menú, Esc para cerrar), roles ARIA en el menú.
6. Toda llamada al backend pasa por `core/api-client.js`. Los módulos no usan `fetch` directo.
7. El frontend no contiene claves ni lógica de negocio.

## Esqueleto de componente
```js
// components/ui-button/ui-button.js
export class UiButton extends HTMLElement {
  static observedAttributes = ['variant', 'size', 'icon', 'disabled'];
  connectedCallback() { this.render(); }
  attributeChangedCallback() { if (this.isConnected) this.render(); }
  render() {
    const icon = this.getAttribute('icon');
    this.innerHTML = `
      <button class="ui-button" part="button">
        ${icon ? `<ui-icon name="${icon}"></ui-icon>` : ''}
        <span><slot></slot></span>
      </button>`;
  }
}
customElements.define('ui-button', UiButton);
```

## Definición de terminado (Frontend)
- [ ] Cumple los criterios de aceptación de la spec.
- [ ] Sin hex/fuentes fuera de tokens; sin emojis; sin componentes duplicados.
- [ ] Animaciones con tokens y `prefers-reduced-motion`.
- [ ] Navegable por teclado.
- [ ] Probado a 100 % y 150 % de escala de Windows.
- [ ] Grafo de codebase-memory reindexado.

