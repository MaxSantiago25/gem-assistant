# Spec 004 — Identidad "Gem", Leopardo Oficial y Esfera Animada de Pensamiento (`<ui-thinking-orb>`)

- **Estado**: APROBADA
- **Fecha**: 2026-11-07
- **Autor**: Agente (SDD)

## 1. Objetivo y Contexto
1. Mantener el nombre e identidad **"Gem"** con el leopardo oficial al costado izquierdo del nombre dentro de la isla, **sin seguimiento ocular por vista** (usando el arte original limpio en tono bronce-ámbar sobre fondo transparente).
2. Incorporar la **esfera animada de pensamiento (`<ui-thinking-orb>`)** basada en la esfera de rosetas/manchas de leopardo proporcionada por el usuario, donde cada roseta/mancha **se aleja y se acerca radialmente** en un ciclo continuo mientras se espera la respuesta del modelo de IA.

## 2. Alcance
### Incluye
- Simplificación de `<ui-leopard>` (`frontend/src/components/ui-leopard/ui-leopard.js` y `ui-leopard.css`): elimina el seguimiento por vista y muestra el leopardo oficial (`assets/images/gem-leopard.png`) con fondo transparente.
- Creación del componente `<ui-thinking-orb size="sm|md|lg">` (`frontend/src/components/ui-thinking-orb/ui-thinking-orb.js` y `ui-thinking-orb.css`):
  - Extrae cada mancha/roseta individual de `assets/images/gem-thinking-orb.png` mediante componentes conexos en un canvas offscreen.
  - Anima en tiempo real (`requestAnimationFrame`) cada mancha alejándose hacia afuera y acercándose hacia el centro de la esfera de forma fluida hasta que llega la respuesta del modelo.
- Integración de `<ui-thinking-orb>` en `frontend/src/modules/chat/chat-view.js` durante el estado de espera de respuesta del modelo.

## 3. Criterios de Aceptación
- **CA-1 (Identidad "Gem" y leopardo sin seguimiento por vista)**: `<ui-leopard>` muestra el leopardo oficial al costado izquierdo de **"Gem"** sin seguimiento ocular al cursor.
- **CA-2 (Esfera de pensamiento animada)**: Al enviar un mensaje al modelo en el Chat, se muestra `<ui-thinking-orb>` con las manchas de leopardo alejándose y acercándose continuamente hasta recibir la respuesta del modelo.
- **CA-3 (Cumplimiento del Harness)**: Componentes modulares, sin colores hex sueltos en CSS/JS y limpieza automática de `requestAnimationFrame` al desmontar.
