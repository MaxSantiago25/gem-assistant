/**
 * Custom Element: <ui-badge tone="accent|neutral|muted">Texto</ui-badge>
 */
export class UiBadge extends HTMLElement {
  static get observedAttributes() {
    return ['tone'];
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
    const tone = this.getAttribute('tone') || 'neutral';
    const text = this.getAttribute('data-text') || this.textContent.trim();
    if (!this.hasAttribute('data-text') && text) {
      this.setAttribute('data-text', text);
    }

    this.innerHTML = `
      <span class="ui-badge ui-badge--${tone}">
        ${this.getAttribute('data-text') || ''}
      </span>
    `;
  }
}

if (!customElements.get('ui-badge')) {
  customElements.define('ui-badge', UiBadge);
}

