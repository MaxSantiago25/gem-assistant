/**
 * Custom Element: <ui-button variant="primary|ghost|icon|surface" size="sm|md|lg" icon="..." disabled>Texto</ui-button>
 */
export class UiButton extends HTMLElement {
  static get observedAttributes() {
    return ['variant', 'size', 'icon', 'disabled', 'aria-label'];
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
    const variant = this.getAttribute('variant') || 'surface';
    const size = this.getAttribute('size') || 'md';
    const icon = this.getAttribute('icon');
    const disabled = this.hasAttribute('disabled');
    const ariaLabel = this.getAttribute('aria-label') || '';
    const originalContent = this.getAttribute('data-text') || this.textContent.trim();

    // Guardar texto original para evitar perderlo en re-renders
    if (!this.hasAttribute('data-text') && originalContent) {
      this.setAttribute('data-text', originalContent);
    }

    const text = this.getAttribute('data-text') || '';

    this.innerHTML = `
      <button
        class="ui-btn ui-btn--${variant} ui-btn--${size}"
        ${disabled ? 'disabled' : ''}
        ${ariaLabel ? `aria-label="${ariaLabel}"` : ''}
        type="button"
      >
        ${icon ? `<ui-icon name="${icon}" size="${size === 'sm' ? 'sm' : 'md'}"></ui-icon>` : ''}
        ${text ? `<span>${text}</span>` : ''}
      </button>
    `;

    // Re-dispatch click events from inner button to host element
    const btn = this.querySelector('button');
    btn.addEventListener('click', (e) => {
      if (disabled) {
        e.stopPropagation();
        e.preventDefault();
      }
    });
  }
}

if (!customElements.get('ui-button')) {
  customElements.define('ui-button', UiButton);
}

