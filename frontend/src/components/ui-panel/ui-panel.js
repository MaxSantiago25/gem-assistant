/**
 * Custom Element: <ui-panel padding="sm|md|lg|none">...</ui-panel>
 */
export class UiPanel extends HTMLElement {
  static get observedAttributes() {
    return ['padding'];
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
    const padding = this.getAttribute('padding') || 'md';
    if (!this.querySelector('.ui-panel')) {
      const content = this.innerHTML;
      this.innerHTML = `
        <div class="ui-panel ui-panel--padding-${padding}">
          ${content}
        </div>
      `;
    } else {
      const inner = this.querySelector('.ui-panel');
      inner.className = `ui-panel ui-panel--padding-${padding}`;
    }
  }
}

if (!customElements.get('ui-panel')) {
  customElements.define('ui-panel', UiPanel);
}

