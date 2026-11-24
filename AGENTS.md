# AGENTS.md — Instrucciones para agentes de IA

Este archivo es el punto de entrada. Léelo completo antes de tocar código.

## 1. Contexto obligatorio
1. Usa el MCP **codebase-memory-mcp** para consultar el grafo del proyecto ANTES de abrir o buscar archivos a mano
   (ver `docs/mcp/CODEBASE-MEMORY.md`).
2. Lee `docs/sdd/METODOLOGIA-SDD.md`: **no se escribe código sin una spec aprobada** en `specs/`.
3. Lee `docs/harness/HARNESS.md`: son reglas innegociables de diseño y código.
4. Identifica tu rol y lee su archivo en `docs/roles/`.

## 2. Reglas duras (resumen del Harness)
- **Modular**: un archivo = una responsabilidad. Nada de archivos gigantes.
- **Reutilizar antes de crear**: busca primero en `frontend/src/components/` (o `backend/app/` según el caso).
  Si existe un componente parecido, se parametriza; no se duplica.
- **Tokens únicos**: colores, tipografías, espaciados y animaciones se definen UNA vez en
  `frontend/src/styles/tokens.css` y se referencian con `var(--...)`. Prohibido escribir hex o `font-family` sueltos.
- **Colores**: fondo `#191919`, texto `#EFEFEF`, botones/acentos *vivid purple*.
- **Tipografía**: Montserrat (identidad), Inter (UI), Lato (cuerpo). Ver Harness.
- **Iconos**: SVG del sprite del proyecto. **Prohibido usar emojis** como iconos.
- **Animaciones**: limpias, estilo macOS, usando tokens de curva y duración.
- **Conexiones externas**: solo dentro de `backend/app/connections/`. Ningún otro módulo llama a una API externa.
- **Secretos**: nunca en código, SQLite ni logs. Se guardan en el Administrador de credenciales de Windows (`keyring`).
- **Stack cerrado**: frontend JS vanilla, backend Python, SQLite. No agregues dependencias sin proponerlo en una spec.

## 3. Flujo de trabajo
`spec.md` → `plan.md` → `tasks.md` → implementación → verificación contra criterios de aceptación.
Cada tarea referencia el criterio de aceptación que cumple.

## 4. Definición de terminado (DoD)
- Cumple los criterios de aceptación de la spec.
- Respeta el Harness (sin hex sueltos, sin duplicados, sin emojis).
- Tiene pruebas (backend) o checklist visual (frontend).
- El grafo de codebase-memory fue reindexado.

