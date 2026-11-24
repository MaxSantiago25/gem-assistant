/**
 * Helper para estados vacíos estándar (CA-12: "Próximamente")
 * Sin emojis, tipografía conforme al Harness y tokens estrictos.
 */
export function createEmptyStateView({ icon, title, description, phase, badgeText = 'Próximamente' }) {
  const container = document.createElement('div');
  container.className = 'module-transition-enter';
  container.style.cssText = 'height: 100%; display: flex; align-items: center; justify-content: center; padding: var(--space-6);';

  container.innerHTML = `
    <div style="max-width: 420px; width: 100%; text-align: center; display: flex; flex-direction: column; align-items: center; gap: var(--space-4);">
      <div style="
        width: 64px;
        height: 64px;
        border-radius: var(--radius-lg);
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--color-accent);
      ">
        <ui-icon name="${icon}" size="xl"></ui-icon>
      </div>

      <div style="display: flex; flex-direction: column; gap: var(--space-2); align-items: center;">
        <div style="display: flex; align-items: center; gap: var(--space-2);">
          <h3 style="font-size: 18px; margin: 0;">${title}</h3>
          <ui-badge tone="accent">${badgeText}</ui-badge>
        </div>
        <p style="color: var(--color-text-muted); font-size: 13px; line-height: 1.5; margin: 0;">
          ${description}
        </p>
      </div>

      <ui-card size="sm" style="width: 100%; text-align: left;">
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
          <span style="color: var(--color-text-muted);">Hoja de ruta SDD:</span>
          <span style="font-weight: 600; color: var(--color-text);">${phase}</span>
        </div>
      </ui-card>
    </div>
  `;

  return container;
}

