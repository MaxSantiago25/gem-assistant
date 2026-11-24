/**
 * Cliente API centralizado (01-arquitectura.md §6 y 03-frontend.md §8)
 * Todas las llamadas al backend pasan por aquí.
 */
class ApiClient {
  constructor() {
    this.baseUrl = 'http://127.0.0.1:8765/api/v1';
    this.token = 'dev-island-token';
  }

  setSession(port, token) {
    if (port) this.baseUrl = `http://127.0.0.1:${port}/api/v1`;
    if (token) this.token = token;
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    if (this.token) {
      headers['X-Island-Token'] = this.token;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers
      }
    };

    const response = await fetch(url, config);
    if (!response.ok) {
      let errData = {};
      try {
        errData = await response.json();
      } catch (_) {}
      throw new Error(errData.error?.message || `Error HTTP ${response.status}`);
    }

    return response.json();
  }

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();

