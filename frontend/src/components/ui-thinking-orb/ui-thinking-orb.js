let cachedSpotsPromise = null;

function loadAndExtractSpots() {
  if (cachedSpotsPromise) {
    return cachedSpotsPromise;
  }

  cachedSpotsPromise = new Promise((resolve) => {
    const img = new Image();
    img.src = 'assets/images/gem-thinking-orb.png';
    img.onload = () => {
      const W = 256;
      const H = 256;
      const offscreen = document.createElement('canvas');
      offscreen.width = W;
      offscreen.height = H;
      const ctx = offscreen.getContext('2d');
      ctx.drawImage(img, 0, 0, W, H);

      const imgData = ctx.getImageData(0, 0, W, H);
      const data = imgData.data;
      const visited = new Uint8Array(W * H);
      const spots = [];

      const centerX = W / 2;
      const centerY = H / 2;

      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const idx = y * W + x;
          if (visited[idx]) continue;
          const alpha = data[idx * 4 + 3];
          if (alpha <= 20) {
            visited[idx] = 1;
            continue;
          }

          // BFS para extraer todos los píxeles de esta mancha/roseta individual
          const queue = [idx];
          visited[idx] = 1;
          const pixels = [];
          let minX = x;
          let maxX = x;
          let minY = y;
          let maxY = y;
          let sumX = 0;
          let sumY = 0;

          let head = 0;
          while (head < queue.length) {
            const curr = queue[head++];
            const cx = curr % W;
            const cy = (curr - cx) / W;
            pixels.push(curr);
            sumX += cx;
            sumY += cy;

            if (cx < minX) minX = cx;
            if (cx > maxX) maxX = cx;
            if (cy < minY) minY = cy;
            if (cy > maxY) maxY = cy;

            for (let dy = -1; dy <= 1; dy++) {
              const ny = cy + dy;
              if (ny < 0 || ny >= H) continue;
              for (let dx = -1; dx <= 1; dx++) {
                const nx = cx + dx;
                if (nx < 0 || nx >= W) continue;
                const nIdx = ny * W + nx;
                if (!visited[nIdx] && data[nIdx * 4 + 3] > 20) {
                  visited[nIdx] = 1;
                  queue.push(nIdx);
                }
              }
            }
          }

          if (pixels.length < 4) continue;

          const sw = maxX - minX + 1;
          const sh = maxY - minY + 1;
          const spotCanvas = document.createElement('canvas');
          spotCanvas.width = sw;
          spotCanvas.height = sh;
          const sCtx = spotCanvas.getContext('2d');
          const sData = sCtx.createImageData(sw, sh);

          for (let i = 0; i < pixels.length; i++) {
            const pIdx = pixels[i];
            const px = pIdx % W;
            const py = (pIdx - px) / W;
            const localIdx = ((py - minY) * sw + (px - minX)) * 4;
            const srcIdx = pIdx * 4;
            sData.data[localIdx] = data[srcIdx];
            sData.data[localIdx + 1] = data[srcIdx + 1];
            sData.data[localIdx + 2] = data[srcIdx + 2];
            sData.data[localIdx + 3] = data[srcIdx + 3];
          }
          sCtx.putImageData(sData, 0, 0);

          const meanX = sumX / pixels.length;
          const meanY = sumY / pixels.length;
          const rx = meanX - centerX;
          const ry = meanY - centerY;
          const dist = Math.hypot(rx, ry);
          const ux = dist > 0.5 ? rx / dist : 0;
          const uy = dist > 0.5 ? ry / dist : 0;
          const distNorm = Math.min(1, dist / 118);

          spots.push({
            sprite: spotCanvas,
            sw,
            sh,
            baseX: minX + sw / 2 - centerX,
            baseY: minY + sh / 2 - centerY,
            ux,
            uy,
            distNorm
          });
        }
      }

      resolve(spots);
    };
    img.onerror = () => resolve([]);
  });

  return cachedSpotsPromise;
}

/**
 * Custom Element: <ui-thinking-orb size="sm|md|lg"></ui-thinking-orb>
 * Esfera de pensamiento animada donde las rosetas de leopardo se alejan y se acercan continuamente.
 */
export class UiThinkingOrb extends HTMLElement {
  static get observedAttributes() {
    return ['size'];
  }

  constructor() {
    super();
    this._rafId = null;
    this._spots = null;
    this._startTime = performance.now();
  }

  connectedCallback() {
    this.render();
    this._initAnimation();
  }

  disconnectedCallback() {
    this._stopAnimation();
  }

  attributeChangedCallback() {
    if (this.isConnected) {
      this.render();
      this._initAnimation();
    }
  }

  _stopAnimation() {
    if (this._rafId) {
      cancelAnimationFrame(this._rafId);
      this._rafId = null;
    }
  }

  async _initAnimation() {
    this._stopAnimation();
    const spots = await loadAndExtractSpots();
    if (!this.isConnected || !spots.length) return;
    this._spots = spots;
    this._startTime = performance.now();

    const canvas = this.querySelector('.thinking-orb-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const CW = canvas.width;
    const CH = canvas.height;
    const halfW = CW / 2;
    const halfH = CH / 2;

    const tick = (now) => {
      if (!this.isConnected) return;
      const t = (now - this._startTime) / 1000;

      ctx.clearRect(0, 0, CW, CH);

      for (let i = 0; i < spots.length; i++) {
        const s = spots[i];
        // Onda radial continua: las manchas se alejan hacia afuera y se acercan hacia el centro
        const wave = Math.sin(t * 3.2 - s.distNorm * 1.1);
        const radialOffset =
          wave >= 0
            ? wave * 28 * (0.22 + 0.78 * s.distNorm)
            : wave * 20 * (0.18 + 0.82 * s.distNorm);

        const scale = 1 + 0.1 * wave;
        const drawW = s.sw * scale;
        const drawH = s.sh * scale;

        const x = halfW + s.baseX + s.ux * radialOffset - drawW / 2;
        const y = halfH + s.baseY + s.uy * radialOffset - drawH / 2;

        ctx.drawImage(s.sprite, x, y, drawW, drawH);
      }

      this._rafId = requestAnimationFrame(tick);
    };

    this._rafId = requestAnimationFrame(tick);
  }

  render() {
    const size = this.getAttribute('size') || 'md';
    this.innerHTML = `
      <div class="thinking-orb thinking-orb--${size}" role="status" aria-label="Gem está pensando">
        <canvas class="thinking-orb-canvas" width="320" height="320"></canvas>
      </div>
    `;
  }
}

if (!customElements.get('ui-thinking-orb')) {
  customElements.define('ui-thinking-orb', UiThinkingOrb);
}

