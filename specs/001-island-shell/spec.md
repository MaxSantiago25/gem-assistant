# 001 — Island Shell (isla y panel)

## Problema
El usuario necesita un acceso rápido y discreto a su agente desde cualquier momento del trabajo en la PC, sin abrir una ventana tradicional.

## Historias de usuario
- Como usuario, quiero ver una píldora flotante siempre visible para saber que mi agente está listo.
- Como usuario, quiero presionar la píldora y que se expanda en un panel para acceder a todas las funciones.
- Como usuario, quiero un menú lateral con Inicio, Chat, Tareas, Hábitos, Enfoque, Correo, MiPC y Ajustes para elegir en qué trabaja mi agente.
- Como usuario, quiero un botón de salir (cerrar sesión) discreto al final del menú.
- Como usuario, quiero volver a la píldora con Esc o haciendo clic fuera del panel.

## Criterios de aceptación
- [x] CA-1 La píldora aparece centrada arriba en el monitor principal, sin bordes y sobre las demás ventanas.
- [x] CA-2 La píldora no aparece en la barra de tareas.
- [x] CA-3 Al hacer clic se expande con animación fluida (~420 ms) a un panel dividido en dos partes.
- [x] CA-4 El menú izquierdo muestra, en orden: Inicio, Chat, Tareas, Hábitos, Enfoque, Correo, MiPC, Ajustes.
- [x] CA-5 Todos los iconos son SVG; no hay emojis en ninguna parte de la interfaz.
- [x] CA-6 "Salir" está al fondo del menú, sin apariencia de botón (sin relleno ni borde), integrado al fondo.
- [x] CA-7 Al seleccionar un elemento del menú, el contenido derecho cambia con una transición suave.
- [x] CA-8 Esc o clic fuera contraen el panel a la píldora.
- [x] CA-9 Colores: fondo `#191919`, texto `#EFEFEF`, acentos y botones en *vivid purple* (`#9D00FF`).
- [x] CA-10 Tipografías: Montserrat en titulares, Inter en UI, Lato en cuerpo.
- [x] CA-11 Con "reducir movimiento" activado en Windows, las animaciones se minimizan.
- [x] CA-12 Los módulos aún sin funcionalidad muestran un estado vacío coherente ("Próximamente").

## Fuera de alcance
Lógica real de chat, tareas, hábitos, correo, MiPC; conexión a LLMs; pantalla de inicio de sesión completa.

## Preguntas aclaradas
- ¿"Salir" cierra sesión (bloquea) o cierra la app? Resuelto: Cierra sesión, invalida el estado activo y regresa la píldora a estado bloqueado/discreto sin cerrar la aplicación de fondo.
- ¿Atajo global de teclado para abrir/cerrar la isla? Resuelto: `Ctrl+Alt+Espacio` (registrado en Tauri).
- ¿Tono exacto de *vivid purple*? Resuelto: `#9D00FF` definido como `--color-accent` en `tokens.css`.
- ¿Soporte de varios monitores desde la fase 1? Resuelto: Monitor principal centrado arriba en Fase 1.

