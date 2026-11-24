# HARNESS — Reglas de diseño y código

Estas reglas aplican a todo el proyecto y a todo agente (humano o IA). Se crean **una vez** y se **llaman** después.

## 1. Principios
1. **Diseño modular**: un archivo, una responsabilidad.
2. **Reutilizar**: se crea un componente general y se reutiliza redimensionándolo (variantes y tamaños), nunca copiándolo.
3. **Definir una vez**: colores, tipografías, espaciados, radios y animaciones viven en `tokens.css`.
4. **Animaciones limpias, estilo macOS**: suaves, cortas, sin rebotes exagerados.
5. **Sin emojis** como iconografía: solo iconos SVG.

## 2. Colores (únicos tres base)
| Token | Valor | Uso |
|---|---|---|
| `--color-bg` | `#191919` | Fondo |
| `--color-text` | `#EFEFEF` | Texto |
| `--color-accent` | *vivid purple* → `#9D00FF` (propuesto, se cambia solo aquí) | Botones y acentos |

Los tonos derivados (superficies, bordes, hover) se calculan con `color-mix()` a partir de estos tres. No se agregan hex nuevos.

## 3. Tipografía
| Familia | Uso | Pesos | CSS |
|---|---|---|---|
| **Montserrat** | Titulares, branding, badges, identidad | 700, 800 | `'Montserrat', sans-serif` |
| **Inter** | Componentes UI, tablas, botones, números tabulares, nombres | 500, 600, 700 | `'Inter', system-ui, sans-serif` |
| **Lato** | Cuerpo, metadatos, párrafos, ayudas, subtítulos | 400, 700 | `'Lato', sans-serif` |

Las fuentes se incluyen **locales** (`frontend/assets/fonts/*.woff2`) para funcionar sin internet.
Para números en tablas y contadores: `font-variant-numeric: tabular-nums` con Inter.

## 4. `tokens.css` (fuente única)
```css
:root {
  /* Color */
  --color-bg: #191919;
  --color-text: #EFEFEF;
  --color-accent: #9D00FF;
  --color-surface: color-mix(in srgb, var(--color-bg), var(--color-text) 6%);
  --color-surface-hover: color-mix(in srgb, var(--color-bg), var(--color-text) 10%);
  --color-border: color-mix(in srgb, var(--color-bg), var(--color-text) 14%);
  --color-text-muted: color-mix(in srgb, var(--color-text), var(--color-bg) 40%);
  --color-accent-hover: color-mix(in srgb, var(--color-accent), var(--color-text) 15%);

  /* Tipografía */
  --font-brand: 'Montserrat', sans-serif;
  --font-ui: 'Inter', system-ui, sans-serif;
  --font-body: 'Lato', sans-serif;

  /* Espaciado (escala de 4) */
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 24px; --space-6: 32px;

  /* Radios */
  --radius-sm: 10px; --radius-md: 16px; --radius-lg: 28px; --radius-pill: 999px;

  /* Movimiento (estilo macOS) */
  --ease-mac: cubic-bezier(0.32, 0.72, 0, 1);
  --ease-soft: cubic-bezier(0.25, 0.1, 0.25, 1);
  --dur-fast: 160ms; --dur-base: 280ms; --dur-slow: 420ms;
}
@media (prefers-reduced-motion: reduce) {
  :root { --dur-fast: 1ms; --dur-base: 1ms; --dur-slow: 1ms; }
}
```

## 5. Componentes reutilizables (catálogo)
Se implementan como **Custom Elements** de JS vanilla. Se redimensionan con el atributo `size` (`sm | md | lg`), nunca con CSS nuevo por pantalla.

| Componente | Variantes / tamaños | Notas |
|---|---|---|
| `ui-icon` | `name`, `size` | Lee del sprite SVG único |
| `ui-button` | `variant`: primary · ghost · icon — `size`: sm/md/lg | Primary usa `--color-accent` |
| `ui-nav-item` | `active`, `icon`, `label` | Barra lateral |
| `ui-panel` | `padding` | Contenedor base de contenido |
| `ui-card` | `size` | Tarjetas de tareas, hábitos, correos |
| `ui-input` / `ui-textarea` | `size` | Chat, formularios |
| `ui-badge` | `tone` | Montserrat |
| `ui-toggle` | — | Ajustes |
| `ui-list-item` | `size` | Listas de tareas, correos, archivos |
| `ui-island` | `state`: collapsed · expanded | La píldora |

**Regla de oro:** antes de crear un componente, buscar en `frontend/src/components/`. Si hay uno parecido, se extiende con una variante.

## 6. Iconografía
- Sprite SVG único: `frontend/assets/icons/sprite.svg`, usado con `<ui-icon name="...">`.
- Set recomendado: **Lucide** (licencia ISC), trazo uniforme de 1.75–2 px, `stroke="currentColor"` para heredar color.
- Nombres semánticos del proyecto: `home, chat, tasks, habits, focus, mail, pc, settings, logout`.
- Prohibido emoji o caracteres Unicode como icono.

## 7. Animación
- Expandir/contraer la isla: `--dur-slow` con `--ease-mac`.
- Hover y foco: `--dur-fast`.
- Cambio de módulo: fundido + desplazamiento de 8 px, `--dur-base`.
- Animar solo `transform`, `opacity` y `clip-path`/`border-radius`; evitar `width/height` salvo la isla.
- Respetar `prefers-reduced-motion`.

## 8. Código
- **Frontend**: ES modules, sin globales, sin librerías de UI. Un archivo por componente (`ui-button.js` + `ui-button.css`).
- **Backend**: capas `api → services → repositories`, tipado con Pydantic, nada de lógica en los routers.
- **Nombres**: archivos en `kebab-case` (frontend) y `snake_case` (Python).
- **Conexiones externas** solo en `backend/app/connections/`.
- **Idioma**: interfaz en español; código y comentarios técnicos en español o inglés, pero consistente.

## 9. Checklist de revisión
- [ ] ¿Algún hex o `font-family` fuera de `tokens.css`?
- [ ] ¿Se duplicó un componente existente?
- [ ] ¿Hay emojis usados como icono?
- [ ] ¿Las animaciones usan los tokens y respetan `prefers-reduced-motion`?
- [ ] ¿Alguna llamada externa fuera de `connections/`?
- [ ] ¿Algún secreto en código, SQLite o logs?

