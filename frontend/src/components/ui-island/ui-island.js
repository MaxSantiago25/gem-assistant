import { tauriBridge } from '../../core/tauri-bridge.js';
import { router } from '../../core/router.js';

/**
 * Custom Element: <ui-island state="collapsed|expanded"></ui-island>
 * Orquestador principal de la isla dinámica y el panel dividido.
 */
export class UiIsland extends HTMLElement {
  static get observedAttributes() {
    return ['state'];
  }

  constructor() {
    super();
    this._state = 'collapsed';
    this._activeModule = 'home';
    this._timeUpdateInterval = null;
    this._isTransitioning = false;
  }

  connectedCallback() {
    this._state = this.getAttribute('state') || 'collapsed';
    this.render();
    this.setupEventListeners();
    this.startTimeUpdater();
  }

  disconnectedCallback() {
    if (this._timeUpdateInterval) {
      clearInterval(this._timeUpdateInterval);
    }
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'state' && oldValue !== newValue && !this._isTransitioning) {
      if (newValue === 'expanded') {
        this.expand();
      } else {
        this.collapse();
      }
    }
  }

  startTimeUpdater() {
    this.updateClock();
    this._timeUpdateInterval = setInterval(() => this.updateClock(), 1000);
  }

  updateClock() {
    const timeEl = this.querySelector('.js-clock-display');
    if (timeEl) {
      const now = new Date();
      timeEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  }

  setupEventListeners() {
    // Escuchar selección de navegación de los items hijos
    this.addEventListener('nav-select', (e) => {
      const { target, isLogout } = e.detail;
      if (isLogout) {
        this.handleLogout();
      } else if (target) {
        this.navigateTo(target);
      }
    });

    // Atajo de teclado global interno: Esc contrae la isla (CA-8)
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this._state === 'expanded') {
        e.preventDefault();
        this.collapse();
      }
    });
  }

  async expand() {
    if (this._state === 'expanded' || this._isTransitioning) return;
    this._isTransitioning = true;

    // 1. Notificar a Tauri para ampliar la ventana transparente nativa antes de la animación (ADR-7)
    await tauriBridge.setWindowExpanded(true);

    this._state = 'expanded';
    this.setAttribute('state', 'expanded');
    this.render();

    // Permitir que la animación de 420 ms se complete
    setTimeout(() => {
      this._isTransitioning = false;
      router.renderCurrentModule();
    }, 420);
  }

  async collapse() {
    if (this._state === 'collapsed' || this._isTransitioning) return;
    this._isTransitioning = true;

    this._state = 'collapsed';
    this.setAttribute('state', 'collapsed');
    this.render();

    // 2. Esperar que termine la animación CSS (~420 ms) y luego reducir la ventana nativa (ADR-7)
    setTimeout(async () => {
      await tauriBridge.setWindowExpanded(false);
      this._isTransitioning = false;
    }, 420);
  }

  handleLogout() {
    // Definición de Salir (CA-6 y spec.md): cierra sesión bloqueando y contrayendo a la píldora
    this.collapse();
    const statusText = this.querySelector('.pill-status');
    if (statusText) {
      statusText.textContent = 'Sesión cerrada';
    }
    window.dispatchEvent(new CustomEvent('island-session-logout'));
  }

  navigateTo(moduleName) {
    if (this._activeModule === moduleName) return;
    this._activeModule = moduleName;
    router.navigate(moduleName);

    // Actualizar nav items
    this.querySelectorAll('ui-nav-item').forEach((item) => {
      const target = item.getAttribute('target');
      if (target === moduleName) {
        item.setAttribute('active', '');
      } else {
        item.removeAttribute('active');
      }
    });

    // Actualizar título en cabecera de módulo
    const titleEl = this.querySelector('.js-module-header-title');
    if (titleEl) {
      titleEl.textContent = router.getModuleTitle(moduleName);
    }
  }

  render() {
    if (this._state === 'collapsed') {
      this.renderCollapsed();
    } else {
      this.renderExpanded();
    }
  }

  renderCollapsed() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    this.innerHTML = `
      <div class="island-container island-container--collapsed" role="button" tabindex="0" aria-label="Abrir Gem">
        <div class="pill-left">
          <ui-leopard size="sm"></ui-leopard>
          <span class="pill-title">Gem</span>
          <span class="pill-status">Listo</span>
        </div>
        <div class="pill-right">
          <ui-icon name="clock" size="sm"></ui-icon>
          <span class="js-clock-display tabular-numbers">${timeStr}</span>
        </div>
      </div>
    `;

    const container = this.querySelector('.island-container');
    container.addEventListener('click', () => this.expand());
    container.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.expand();
      }
    });
  }

  renderExpanded() {
    this.innerHTML = `
      <!-- Backdrop transparente para clic fuera (CA-8) -->
      <div class="island-backdrop" aria-hidden="true"></div>

      <div class="island-container island-container--expanded" role="dialog" aria-modal="true" aria-label="Panel Gem">
        <!-- Columna Izquierda: Menú (~220 px) (CA-4) -->
        <aside class="island-sidebar">
          <div class="island-brand-header">
            <div class="island-brand-info">
              <ui-leopard size="md"></ui-leopard>
              <span class="island-brand-name">Gem</span>
            </div>
            <ui-button variant="icon" size="sm" icon="minimize" aria-label="Minimizar a píldora" class="js-btn-collapse"></ui-button>
          </div>

          <nav class="island-nav-list" role="navigation" aria-label="Navegación principal">
            <ui-nav-item icon="home" label="Inicio" target="home" ${this._activeModule === 'home' ? 'active' : ''}></ui-nav-item>
            <ui-nav-item icon="chat" label="Chat" target="chat" ${this._activeModule === 'chat' ? 'active' : ''}></ui-nav-item>
            <ui-nav-item icon="tasks" label="Tareas" target="tasks" ${this._activeModule === 'tasks' ? 'active' : ''}></ui-nav-item>
            <ui-nav-item icon="habits" label="Hábitos" target="habits" ${this._activeModule === 'habits' ? 'active' : ''}></ui-nav-item>
            <ui-nav-item icon="focus" label="Enfoque" target="focus" ${this._activeModule === 'focus' ? 'active' : ''}></ui-nav-item>
            <ui-nav-item icon="mail" label="Correo" target="mail" ${this._activeModule === 'mail' ? 'active' : ''}></ui-nav-item>
            <ui-nav-item icon="pc" label="MiPC" target="pc" ${this._activeModule === 'pc' ? 'active' : ''}></ui-nav-item>
            <ui-nav-item icon="settings" label="Ajustes" target="settings" ${this._activeModule === 'settings' ? 'active' : ''}></ui-nav-item>
          </nav>

          <!-- Salir al fondo: integrado al fondo, sin apariencia de botón (CA-6) -->
          <div class="island-sidebar-footer">
            <ui-nav-item icon="logout" label="Salir" logout></ui-nav-item>
          </div>
        </aside>

        <!-- Columna Derecha: Contenido del módulo activo -->
        <main class="island-main">
          <header class="island-main-header">
            <h2 class="island-module-title js-module-header-title">${router.getModuleTitle(this._activeModule)}</h2>
            <ui-badge tone="accent">Fase 1 · Shell</ui-badge>
          </header>

          <div class="island-main-content js-module-viewport" id="module-viewport">
            <!-- El módulo activo se renderiza dinámicamente aquí -->
          </div>
        </main>
      </div>
    `;

    // Botón de minimizar a píldora
    const collapseBtn = this.querySelector('.js-btn-collapse');
    if (collapseBtn) {
      collapseBtn.addEventListener('click', () => this.collapse());
    }

    // Clic en backdrop fuera del panel -> colapsa (CA-8)
    const backdrop = this.querySelector('.island-backdrop');
    if (backdrop) {
      backdrop.addEventListener('click', (e) => {
        e.stopPropagation();
        this.collapse();
      });
    }

    // Renderizar inmediatamente el módulo actual en el viewport
    router.mountViewport(this.querySelector('#module-viewport'));
  }
}

if (!customElements.get('ui-island')) {
  customElements.define('ui-island', UiIsland);
}

