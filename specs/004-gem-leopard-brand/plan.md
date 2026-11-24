# Plan Técnico — Spec 004: Identidad "Gem", Leopardo Oficial y Esfera de Pensamiento (`<ui-thinking-orb>`)

## 1. Componente `<ui-leopard>` (Sin seguimiento por vista)
- Renderiza `assets/images/gem-leopard.png` (fondo transparente, tonos bronce-ámbar optimizados para `#191919`) sin listeners de `pointermove`/`pointerdown` ni pupilas SVG superpuestas.

## 2. Componente `<ui-thinking-orb>` (`frontend/src/components/ui-thinking-orb/`)
- Carga `assets/images/gem-thinking-orb.png` (`256×256` RGBA) una sola vez en memoria.
- Identifica cada mancha/roseta individual por componentes conexos (`alpha > 20`), calculando su centroide `(cx, cy)`, su vector radial unitario `(ux, uy)` respecto al centro de la esfera `(128, 128)` y su distancia normalizada `distNorm`.
- En el bucle `requestAnimationFrame`:
  - Calcula una onda radial continua `wave = Math.sin(t * 3.0 - spot.distNorm * 1.1)` que hace que todas las rosetas **se alejen entre sí hacia afuera** y luego **se acerquen de vuelta hacia el centro**, acompañado de un escalado suave de cada roseta.
- Al recibir la respuesta del modelo en `chat-view.js`, el elemento `<ui-thinking-orb>` se elimina del DOM y `disconnectedCallback()` detiene el bucle de animación.
