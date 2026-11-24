/**
 * Custom Element: <ui-card size="sm|md|lg" interactive>...</ui-card>
 */
export class UiCard extends HTMLElement {
  static get observedAttributes() {
    return ['size', 'interactive'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    if (this.isConnected) {
      this.render();
    }
  }

  render() {
    const size = this.getAttribute('size') || 'md';
    const interactive = this.hasAttribute('interactive');

    // Extraer o preservar contenido original
    if (!this.querySelector('.ui-card')) {
      const content = this.innerHTML;
      this.innerHTML = `
        <div class="ui-card ui-card--${size} ${interactive ? 'ui-card--interactive' : ''}">
          ${content}
        </div>
      `;
    } else {
      const inner = this.querySelector('.ui-card');
      inner.className = `ui-card ui-card--${size} ${interactive ? 'ui-card--interactive' : ''}`;
    }
  }
}

if (!customElements.get('ui-card')) {
  customElements.define('ui-card', UiCard);
}

