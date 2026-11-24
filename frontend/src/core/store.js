/**
 * Estado mínimo observable para la aplicación
 */
class Store {
  constructor() {
    this._state = {
      islandState: 'collapsed',
      activeModule: 'home',
      sessionActive: true,
      agentStatus: 'ready' // 'ready' | 'thinking' | 'idle'
    };
    this._listeners = new Set();
  }

  getState() {
    return { ...this._state };
  }

  setState(partial) {
    this._state = { ...this._state, ...partial };
    this._notify();
  }

  subscribe(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  _notify() {
    for (const listener of this._listeners) {
      try {
        listener(this._state);
      } catch (err) {
        console.error('[Store] Error en listener:', err);
      }
    }
  }
}

export const store = new Store();

