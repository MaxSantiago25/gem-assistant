/**
 * Custom Element: <ui-icon name="..." size="sm|md|lg"></ui-icon>
 * Lee del sprite SVG único (assets/icons/sprite.svg)
 */
export class UiIcon extends HTMLElement {
  static get observedAttributes() {
    return ['name', 'size'];
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
    const name = this.getAttribute('name');
    if (!name) {
      this.innerHTML = '';
      return;
    }

    const spritePath = 'assets/icons/sprite.svg';
    this.innerHTML = `
      <svg aria-hidden="true" focusable="false">
        <use href="${spritePath}#icon-${name}"></use>
      </svg>
    `;
  }
}

if (!customElements.get('ui-icon')) {
  customElements.define('ui-icon', UiIcon);
}

