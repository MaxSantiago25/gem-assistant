/**
 * Puente de comunicación con Tauri 2 (Desktop Shell)
 * Con soporte de modo fallback automático si se ejecuta en navegador web estándar.
 */

class TauriBridge {
  get isTauri() {
    return typeof window !== 'undefined' && Boolean(window.__TAURI__ || window.__TAURI_INTERNALS__);
  }

  get windowApi() {
    if (!this.isTauri) return null;
    try {
      return window.__TAURI__?.window?.getCurrentWindow?.() || null;
    } catch (_) {
      return null;
    }
  }

  /**
   * Cambia el tamaño de la ventana nativa manteniendo anclaje superior central
   * @param {boolean} expanded
   */
  async setWindowExpanded(expanded) {
    if (!this.isTauri) {
      return;
    }

    try {
      const invokeFn = window.__TAURI__?.core?.invoke || window.__TAURI_INTERNALS__?.invoke;
      if (invokeFn) {
        await invokeFn('set_island_expanded', { expanded: Boolean(expanded) });
        return;
      }

      const win = this.windowApi;
      if (win && window.__TAURI__?.dpi?.LogicalSize) {
        const { LogicalSize } = window.__TAURI__.dpi;
        if (expanded) {
          await win.setSize(new LogicalSize(960, 620));
        } else {
          await win.setSize(new LogicalSize(360, 80));
        }
      }
    } catch (err) {
      console.warn('[TauriBridge] Error ajustando tamaño de ventana:', err);
    }
  }

  /**
   * Inicia el arrastre de ventana nativo
   */
  async startDragging() {
    const win = this.windowApi;
    if (!win) return;
    try {
      await win.startDragging();
    } catch (err) {
      console.warn('[TauriBridge] Error al iniciar arrastre:', err);
    }
  }

  /**
   * Cierra o minimiza la app
   */
  async close() {
    const win = this.windowApi;
    if (!win) return;
    try {
      await win.close();
    } catch (err) {
      console.warn('[TauriBridge] Error al cerrar ventana:', err);
    }
  }
}

export const tauriBridge = new TauriBridge();
