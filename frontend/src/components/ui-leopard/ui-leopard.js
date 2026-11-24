/**
 * Custom Element: <ui-leopard size="sm|md|lg"></ui-leopard>
 * Emblema oficial de Gem (sin seguimiento por vista).
 */
export class UiLeopard extends HTMLElement {
  static get observedAttributes() {
    return ['size'];
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
    const size = this.getAttribute('size') || 'sm';
    this.innerHTML = `
      <div class="leopard-avatar leopard-avatar--${size}" aria-hidden="true">
        <img
          src="assets/images/gem-leopard.png"
          alt="Gem"
          class="leopard-img"
          draggable="false"
        />
      </div>
    `;
  }
}

if (!customElements.get('ui-leopard')) {
  customElements.define('ui-leopard', UiLeopard);
}
