/**
 * Punto de entrada principal del Frontend (ES Modules)
 */

// Registrar Custom Elements del catálogo
import './components/ui-icon/ui-icon.js';
import './components/ui-leopard/ui-leopard.js';
import './components/ui-thinking-orb/ui-thinking-orb.js';
import './components/ui-button/ui-button.js';
import './components/ui-badge/ui-badge.js';
import './components/ui-card/ui-card.js';
import './components/ui-confirmation-card/ui-confirmation-card.js';
import './components/ui-nav-item/ui-nav-item.js';
import './components/ui-panel/ui-panel.js';
import './components/ui-island/ui-island.js';

import { tauriBridge } from './core/tauri-bridge.js';

document.addEventListener('DOMContentLoaded', () => {
  console.log('[Island] Interfaz inicializada. Entorno Tauri:', tauriBridge.isTauri);

  // Escuchar evento de logout
  window.addEventListener('island-session-logout', () => {
    console.log('[Island] Sesión cerrada. Estado seguro colapsado.');
  });
});
