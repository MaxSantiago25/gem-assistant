/**
 * Custom Element: <ui-nav-item icon="..." label="..." target="..." active logout></ui-nav-item>
 */
export class UiNavItem extends HTMLElement {
  static get observedAttributes() {
    return ['icon', 'label', 'target', 'active', 'logout'];
  }

  connectedCallback() {
    this.render();
    this.addEventListener('click', this.handleClick.bind(this));
  }

  attributeChangedCallback() {
    if (this.isConnected) {
      this.render();
    }
  }

  handleClick(e) {
    const target = this.getAttribute('target');
    const isLogout = this.hasAttribute('logout');
    this.dispatchEvent(new CustomEvent('nav-select', {
      bubbles: true,
      composed: true,
      detail: { target, isLogout }
    }));
  }

  render() {
    const icon = this.getAttribute('icon');
    const label = this.getAttribute('label') || '';
    const isActive = this.hasAttribute('active');
    const isLogout = this.hasAttribute('logout');

    this.innerHTML = `
      <div
        class="ui-nav-item ${isActive ? 'ui-nav-item--active' : ''} ${isLogout ? 'ui-nav-item--logout' : ''}"
        role="button"
        tabindex="0"
        aria-selected="${isActive ? 'true' : 'false'}"
        aria-label="${label}"
      >
        ${icon ? `<ui-icon name="${icon}" size="md"></ui-icon>` : ''}
        <span>${label}</span>
      </div>
    `;

    // Accesibilidad teclado (Enter y Espacio)
    const item = this.querySelector('.ui-nav-item');
    item.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.handleClick(e);
      }
    });
  }
}

if (!customElements.get('ui-nav-item')) {
  customElements.define('ui-nav-item', UiNavItem);
}

