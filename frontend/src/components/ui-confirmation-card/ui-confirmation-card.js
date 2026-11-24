import { apiClient } from '../../core/api-client.js';

/**
 * Custom Element: <ui-confirmation-card action="..." source="..." destination="..." batch-id="..."></ui-confirmation-card>
 * Widget de confirmación previa a la ejecución de acciones en PC o escalado a la nube.
 */
export class UiConfirmationCard extends HTMLElement {
  static get observedAttributes() {
    return ['action', 'source', 'destination', 'batch-id', 'operations'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    if (this.isConnected) {
      this.render();
    }
  }

  _escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  _getOperationsList() {
    const opsAttr = this.getAttribute('operations');
    if (opsAttr) {
      try {
        const parsed = JSON.parse(opsAttr);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      } catch (_) {}
    }

    const action = this.getAttribute('action') || 'fs_move';
    const source = this.getAttribute('source') || '';
    const destination = this.getAttribute('destination') || '';
    return [
      {
        tool: action,
        source_path: source,
        dest_path: destination,
        params: { path: destination || source, source, destination }
      }
    ];
  }

  async handleApprove() {
    const batchId = this.getAttribute('batch-id') || '';
    const action = this.getAttribute('action') || '';
    const isRealBatch = batchId && !batchId.startsWith('demo-');

    let reportText = '';
    if (isRealBatch) {
      try {
        const res = await apiClient.post(`/actions/${batchId}/confirm`, {});
        reportText = res.report || '';
        this.dispatchEvent(new CustomEvent('action-approve', {
          bubbles: true,
          composed: true,
          detail: { batchId, action, response: res }
        }));
      } catch (err) {
        this.renderError(err.message || 'Error al ejecutar la acción');
        return;
      }
    } else {
      this.dispatchEvent(new CustomEvent('action-approve', {
        bubbles: true,
        composed: true,
        detail: { batchId, action }
      }));
    }

    const canUndo = isRealBatch && action !== 'cloud_escalation' && action !== 'os_open';

    this.innerHTML = `
      <div class="confirmation-card confirmation-card--done">
        <div class="confirmation-header">
          <div class="confirmation-title-area">
            <ui-icon name="check" size="md" class="confirmation-icon"></ui-icon>
            <span class="confirmation-title">Comando Permitido y Ejecutado</span>
          </div>
          <ui-badge tone="accent">Completado</ui-badge>
        </div>
        ${reportText ? `
        <div class="confirmation-body">
          <pre class="confirmation-report">${this._escapeHtml(reportText)}</pre>
        </div>` : ''}
        ${canUndo ? `
        <div class="confirmation-footer">
          <ui-button variant="ghost" size="sm" icon="chevron-left" class="js-btn-undo">Deshacer acción</ui-button>
        </div>` : ''}
      </div>
    `;

    this.querySelector('.js-btn-undo')?.addEventListener('click', () => this.handleUndo(batchId));
  }

  async handleReject() {
    const batchId = this.getAttribute('batch-id') || '';
    const action = this.getAttribute('action') || '';
    const isRealBatch = batchId && !batchId.startsWith('demo-');

    if (isRealBatch) {
      try {
        const res = await apiClient.post(`/actions/${batchId}/reject`, {});
        this.dispatchEvent(new CustomEvent('action-reject', {
          bubbles: true,
          composed: true,
          detail: { batchId, action, response: res }
        }));
      } catch (_) {}
    } else {
      this.dispatchEvent(new CustomEvent('action-reject', {
        bubbles: true,
        composed: true,
        detail: { batchId, action }
      }));
    }

    this.innerHTML = `
      <div class="confirmation-card confirmation-card--rejected">
        <div class="confirmation-header">
          <div class="confirmation-title-area">
            <ui-icon name="close" size="md"></ui-icon>
            <span class="confirmation-title">Comando Cancelado</span>
          </div>
          <ui-badge tone="muted">Cancelado</ui-badge>
        </div>
      </div>
    `;
  }

  async handleUndo(batchId) {
    try {
      const res = await apiClient.post(`/actions/${batchId}/undo`, {});
      this.innerHTML = `
        <div class="confirmation-card confirmation-card--rejected">
          <div class="confirmation-header">
            <div class="confirmation-title-area">
              <ui-icon name="check" size="md"></ui-icon>
              <span class="confirmation-title">Acción Revertida (${res.undone_count || 1} op.)</span>
            </div>
            <ui-badge tone="neutral">Deshecho</ui-badge>
          </div>
        </div>
      `;
    } catch (err) {
      this.renderError(err.message || 'No se pudo deshacer la acción');
    }
  }

  renderError(msg) {
    this.innerHTML = `
      <div class="confirmation-card confirmation-card--rejected">
        <div class="confirmation-header">
          <div class="confirmation-title-area">
            <ui-icon name="close" size="md"></ui-icon>
            <span class="confirmation-title">Acción Bloqueada por Harness</span>
          </div>
          <ui-badge tone="muted">Error</ui-badge>
        </div>
        <div class="confirmation-body">
          <span class="confirmation-path">${this._escapeHtml(msg)}</span>
        </div>
      </div>
    `;
  }

  _renderOperationItem(op) {
    const tool = op.tool || 'fs_move';
    const source = this._escapeHtml(op.source_path || op.params?.source || op.params?.path || '');
    const destination = this._escapeHtml(op.dest_path || op.params?.destination || op.params?.path || '');

    if (tool === 'fs_move') {
      return `
        <div class="confirmation-op-item">
          <div class="confirmation-row">
            <span class="confirmation-label">Mover archivo — Origen</span>
            <span class="confirmation-path">${source}</span>
          </div>
          <div class="confirmation-arrow">Hacia destino</div>
          <div class="confirmation-row">
            <span class="confirmation-label">Destino</span>
            <span class="confirmation-path">${destination}</span>
          </div>
        </div>
      `;
    }

    if (tool === 'fs_mkdir') {
      return `
        <div class="confirmation-op-item">
          <div class="confirmation-row">
            <span class="confirmation-label">Crear nueva carpeta</span>
            <span class="confirmation-path">${destination || source}</span>
          </div>
        </div>
      `;
    }

    if (tool === 'fs_rename') {
      return `
        <div class="confirmation-op-item">
          <div class="confirmation-row">
            <span class="confirmation-label">Renombrar — Archivo actual</span>
            <span class="confirmation-path">${source}</span>
          </div>
          <div class="confirmation-arrow">Nuevo nombre</div>
          <div class="confirmation-row">
            <span class="confirmation-label">Ruta final</span>
            <span class="confirmation-path">${destination}</span>
          </div>
        </div>
      `;
    }

    if (tool === 'os_open') {
      return `
        <div class="confirmation-op-item">
          <div class="confirmation-row">
            <span class="confirmation-label">Aplicación autorizada</span>
            <span class="confirmation-path">Google Chrome (chrome)</span>
          </div>
          ${source ? `
          <div class="confirmation-row">
            <span class="confirmation-label">Objetivo</span>
            <span class="confirmation-path">${source}</span>
          </div>` : ''}
        </div>
      `;
    }

    if (tool === 'cloud_escalation') {
      return `
        <div class="confirmation-op-item">
          <span class="confirmation-path">
            Esta consulta solicita escalar al modelo en la nube (Google Gemini) para esta ocasión. Tus archivos y rutas locales nunca son enviados.
          </span>
        </div>
      `;
    }

    return `
      <div class="confirmation-op-item">
        <div class="confirmation-row">
          <span class="confirmation-label">${this._escapeHtml(tool)}</span>
          <span class="confirmation-path">${destination || source}</span>
        </div>
      </div>
    `;
  }

  render() {
    const ops = this._getOperationsList();
    const firstTool = ops[0]?.tool || this.getAttribute('action') || 'fs_move';

    let title = 'Validación de Comando Requerida';
    let icon = 'tasks';

    if (ops.length > 1) {
      title = `Validar lote (${ops.length} operaciones)`;
      icon = 'tasks';
    } else if (firstTool === 'fs_move') {
      title = 'Permiso para mover archivo';
      icon = 'tasks';
    } else if (firstTool === 'fs_mkdir') {
      title = 'Permiso para crear carpeta';
      icon = 'tasks';
    } else if (firstTool === 'fs_rename') {
      title = 'Permiso para renombrar archivo';
      icon = 'tasks';
    } else if (firstTool === 'os_open') {
      title = 'Permiso para abrir Google Chrome';
      icon = 'pc';
    } else if (firstTool === 'cloud_escalation') {
      title = 'Autorizar consulta en la Nube (esta ocasión)';
      icon = 'sparkles';
    }

    const bodyContent = ops.map((op) => this._renderOperationItem(op)).join('');

    this.innerHTML = `
      <div class="confirmation-card">
        <div class="confirmation-header">
          <div class="confirmation-title-area">
            <ui-icon name="${icon}" size="md" class="confirmation-icon"></ui-icon>
            <h4 class="confirmation-title">${title}</h4>
          </div>
          <ui-badge tone="accent">Confirmación Requerida</ui-badge>
        </div>

        <div class="confirmation-body">
          ${bodyContent}
        </div>

        <div class="confirmation-footer">
          <ui-button variant="ghost" size="sm" icon="close" class="js-btn-reject">Cancelar</ui-button>
          <ui-button variant="primary" size="sm" icon="check" class="js-btn-approve">Permitir y Ejecutar</ui-button>
        </div>
      </div>
    `;

    this.querySelector('.js-btn-approve')?.addEventListener('click', () => this.handleApprove());
    this.querySelector('.js-btn-reject')?.addEventListener('click', () => this.handleReject());
  }
}

if (!customElements.get('ui-confirmation-card')) {
  customElements.define('ui-confirmation-card', UiConfirmationCard);
}
