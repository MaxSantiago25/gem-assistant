/**
 * Módulo: Inicio (Home)
 * Resumen del día: estado del agente, tareas rápidas, hábitos del día y enfoque.
 */
export function renderHomeView() {
  const container = document.createElement('div');
  container.className = 'module-transition-enter';
  container.style.cssText = 'display: flex; flex-direction: column; gap: var(--space-4); padding: var(--space-5);';

  container.innerHTML = `
    <!-- Tarjeta de bienvenida y estado del agente -->
    <ui-card size="md">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
        <div style="display: flex; align-items: center; gap: var(--space-2);">
          <ui-icon name="sparkles" size="lg" style="color: var(--color-accent);"></ui-icon>
          <h3 style="font-size: 16px; margin: 0;">Agente Activo</h3>
        </div>
        <ui-badge tone="accent">Conectado</ui-badge>
      </div>
      <p style="color: var(--color-text-muted); font-size: 13px; margin: 0; line-height: 1.4;">
        Tu asistente está listo en segundo plano. Monitoreando tareas, sesiones de enfoque y solicitudes del sistema.
      </p>
    </ui-card>

    <!-- Grid de métricas y resumen rápido -->
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3);">
      <!-- Tarjeta Tareas -->
      <ui-card size="sm" interactive>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
          <div style="display: flex; align-items: center; gap: var(--space-2);">
            <ui-icon name="tasks" size="md" style="color: var(--color-accent);"></ui-icon>
            <span style="font-family: var(--font-brand); font-weight: 700; font-size: 13px;">Tareas de hoy</span>
          </div>
          <span class="tabular-numbers" style="font-weight: 700; font-size: 16px; color: var(--color-text);">0/3</span>
        </div>
        <p style="color: var(--color-text-muted); font-size: 12px; margin: 0;">3 pendientes para completar</p>
      </ui-card>

      <!-- Tarjeta Hábitos -->
      <ui-card size="sm" interactive>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
          <div style="display: flex; align-items: center; gap: var(--space-2);">
            <ui-icon name="habits" size="md" style="color: var(--color-accent);"></ui-icon>
            <span style="font-family: var(--font-brand); font-weight: 700; font-size: 13px;">Racha actual</span>
          </div>
          <span class="tabular-numbers" style="font-weight: 700; font-size: 16px; color: var(--color-text);">5 días</span>
        </div>
        <p style="color: var(--color-text-muted); font-size: 12px; margin: 0;">2 hábitos registrados hoy</p>
      </ui-card>

      <!-- Tarjeta Enfoque -->
      <ui-card size="sm" interactive>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
          <div style="display: flex; align-items: center; gap: var(--space-2);">
            <ui-icon name="focus" size="md" style="color: var(--color-accent);"></ui-icon>
            <span style="font-family: var(--font-brand); font-weight: 700; font-size: 13px;">Sesión Enfoque</span>
          </div>
          <span class="tabular-numbers" style="font-weight: 700; font-size: 16px; color: var(--color-text);">25 min</span>
        </div>
        <p style="color: var(--color-text-muted); font-size: 12px; margin: 0;">Listo para iniciar</p>
      </ui-card>

      <!-- Tarjeta MiPC -->
      <ui-card size="sm" interactive>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2);">
          <div style="display: flex; align-items: center; gap: var(--space-2);">
            <ui-icon name="cpu" size="md" style="color: var(--color-accent);"></ui-icon>
            <span style="font-family: var(--font-brand); font-weight: 700; font-size: 13px;">Rendimiento</span>
          </div>
          <span class="tabular-numbers" style="font-weight: 700; font-size: 16px; color: var(--color-text);">Normal</span>
        </div>
        <p style="color: var(--color-text-muted); font-size: 12px; margin: 0;">Memoria y CPU estables</p>
      </ui-card>
    </div>

    <!-- Actividad Reciente -->
    <ui-card size="md">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-3);">
        <h4 style="font-size: 13px; font-family: var(--font-brand); margin: 0;">Atajos rápidos</h4>
        <ui-badge tone="neutral">Gem v1.0</ui-badge>
      </div>
      <div style="display: flex; flex-direction: column; gap: var(--space-2); font-size: 12px; color: var(--color-text-muted);">
        <div style="display: flex; justify-content: space-between; padding: var(--space-1) 0; border-bottom: 1px solid var(--color-border-subtle);">
          <span>Atajo global de teclado</span>
          <span class="tabular-numbers" style="color: var(--color-text); font-weight: 600;">Ctrl + Alt + Espacio</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: var(--space-1) 0;">
          <span>Contraer panel</span>
          <span class="tabular-numbers" style="color: var(--color-text); font-weight: 600;">Escape</span>
        </div>
      </div>
    </ui-card>
  `;

  return container;
}

