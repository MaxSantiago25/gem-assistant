import { apiClient } from '../../core/api-client.js';

let activeConversationId = null;
let selectedMode = 'auto';

function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function renderChatView() {
  const container = document.createElement('div');
  container.className = 'chat-view';

  container.innerHTML = `
    <div class="chat-toolbar">
      <div class="chat-toolbar-left">
        <select class="chat-select js-conv-select" aria-label="Seleccionar conversación">
          <option value="">Nueva conversación</option>
        </select>
        <ui-button variant="ghost" size="sm" icon="plus" class="js-btn-new-conv">Nueva</ui-button>
      </div>
      <div class="chat-toolbar-right">
        <select class="chat-select js-mode-select" aria-label="Seleccionar perfil de IA">
          <option value="auto" ${selectedMode === 'auto' ? 'selected' : ''}>Router Automático</option>
          <option value="rapido" ${selectedMode === 'rapido' ? 'selected' : ''}>Rápido · Gemma 4 E4B</option>
          <option value="herramientas" ${selectedMode === 'herramientas' ? 'selected' : ''}>Herramientas · Qwen 3.5 9B</option>
          <option value="nube" ${selectedMode === 'nube' ? 'selected' : ''}>Nube · Gemini (Con permiso)</option>
        </select>
      </div>
    </div>

    <div class="chat-messages js-chat-messages" role="log" aria-live="polite"></div>

    <form class="chat-Composer js-chat-form">
      <input
        type="text"
        class="chat-input js-chat-input"
        placeholder="Escribe un mensaje o pide una acción en tu PC (ej. Crea una carpeta en Escritorio)..."
        autocomplete="off"
      />
      <ui-button variant="primary" size="md" icon="send" class="js-btn-send">Enviar</ui-button>
    </form>
  `;

  const convSelect = container.querySelector('.js-conv-select');
  const modeSelect = container.querySelector('.js-mode-select');
  const newConvBtn = container.querySelector('.js-btn-new-conv');
  const messagesEl = container.querySelector('.js-chat-messages');
  const formEl = container.querySelector('.js-chat-form');
  const inputEl = container.querySelector('.js-chat-input');
  const sendBtn = container.querySelector('.js-btn-send');

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function renderEmptyConversation() {
    messagesEl.innerHTML = `
      <div class="chat-empty">
        <ui-leopard size="lg"></ui-leopard>
        <h3 class="chat-empty-title">Gem · Agente IA Local y Guardia de Comandos</h3>
        <p class="chat-empty-desc">
          Conversa con <strong>Gemma 4 E4B QAT</strong> (chat y redacción) o pide acciones en tu PC con
          <strong>Qwen 3.5 9B</strong>. Cualquier comando que modifique carpetas o abra aplicaciones lanzará un widget de confirmación para permitirlo o cancelarlo.
        </p>
        <div class="chat-suggestions">
          <button type="button" class="chat-chip js-chip" data-prompt="Crea una carpeta llamada PruebaIsland en Escritorio">
            <ui-icon name="tasks" size="sm"></ui-icon>
            Crear carpeta en Escritorio (Widget)
          </button>
          <button type="button" class="chat-chip js-chip" data-prompt="Abre Google Chrome">
            <ui-icon name="pc" size="sm"></ui-icon>
            Abrir Google Chrome (Widget)
          </button>
          <button type="button" class="chat-chip js-chip" data-prompt="Lista mis archivos de Descargas">
            <ui-icon name="tasks" size="sm"></ui-icon>
            Listar archivos de Descargas
          </button>
          <button type="button" class="chat-chip js-chip" data-prompt="Redacta un correo breve y formal para solicitar una prórroga de entrega">
            <ui-icon name="chat" size="sm"></ui-icon>
            Redactar correo con Gemma 4
          </button>
        </div>
      </div>
    `;

    messagesEl.querySelectorAll('.js-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        const promptText = chip.getAttribute('data-prompt') || '';
        inputEl.value = promptText;
        handleSendMessage(promptText);
      });
    });
  }

  function appendMessageBubble({ role, content, modelUsed, profileUsed, pendingBatch }) {
    const emptyEl = messagesEl.querySelector('.chat-empty');
    if (emptyEl) {
      emptyEl.remove();
    }

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role === 'user' ? 'chat-bubble--user' : 'chat-bubble--assistant'}`;

    const authorLabel = role === 'user' ? 'Tú' : 'Gem';
    const authorIcon = role === 'user' ? 'user' : 'sparkles';
    const badgeHtml =
      role === 'assistant' && modelUsed
        ? `<ui-badge tone="accent">${escapeHtml(modelUsed)} · ${escapeHtml(profileUsed || 'local')}</ui-badge>`
        : '';

    bubble.innerHTML = `
      <div class="chat-bubble-meta">
        <span class="chat-bubble-author">
          <ui-icon name="${authorIcon}" size="sm"></ui-icon>
          ${authorLabel}
        </span>
        ${badgeHtml}
      </div>
      <div class="chat-bubble-content">${escapeHtml(content)}</div>
    `;

    if (pendingBatch && pendingBatch.batch_id) {
      const widgetWrapper = document.createElement('div');
      widgetWrapper.className = 'chat-bubble-widget';

      const card = document.createElement('ui-confirmation-card');
      const firstOp = pendingBatch.operations?.[0] || {};
      card.setAttribute('batch-id', pendingBatch.batch_id);
      card.setAttribute('action', firstOp.tool || 'fs_mkdir');
      if (firstOp.source_path) card.setAttribute('source', firstOp.source_path);
      if (firstOp.dest_path) card.setAttribute('destination', firstOp.dest_path);
      if (pendingBatch.operations) {
        card.setAttribute('operations', JSON.stringify(pendingBatch.operations));
      }

      card.addEventListener('action-approve', () => {
        scrollToBottom();
      });
      card.addEventListener('action-reject', () => {
        scrollToBottom();
      });

      widgetWrapper.appendChild(card);
      bubble.appendChild(widgetWrapper);
    }

    messagesEl.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  async function loadConversationList() {
    try {
      const list = await apiClient.get('/conversations');
      convSelect.innerHTML = `<option value="">+ Nueva conversación</option>`;
      for (const c of list) {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.title || 'Conversación';
        if (c.id === activeConversationId) {
          opt.selected = true;
        }
        convSelect.appendChild(opt);
      }
    } catch (err) {
      console.warn('[ChatView] No se pudo cargar lista de conversaciones:', err);
    }
  }

  async function loadConversationMessages(convId) {
    if (!convId) {
      activeConversationId = null;
      renderEmptyConversation();
      return;
    }

    try {
      const detail = await apiClient.get(`/conversations/${convId}`);
      activeConversationId = detail.id;
      messagesEl.innerHTML = '';
      if (!detail.messages || detail.messages.length === 0) {
        renderEmptyConversation();
        return;
      }
      for (const m of detail.messages) {
        appendMessageBubble({
          role: m.role,
          content: m.content,
          modelUsed: m.role === 'assistant' ? detail.provider : null,
          profileUsed: m.role === 'assistant' ? 'historial' : null
        });
      }
    } catch (err) {
      console.warn('[ChatView] Error cargando conversación:', err);
      renderEmptyConversation();
    }
  }

  async function handleSendMessage(rawText) {
    const text = (rawText !== undefined ? rawText : inputEl.value).trim();
    if (!text) return;

    inputEl.value = '';
    inputEl.disabled = true;

    appendMessageBubble({ role: 'user', content: text });

    const loadingEl = document.createElement('div');
    loadingEl.className = 'chat-status-indicator';
    loadingEl.innerHTML = `
      <ui-thinking-orb size="md"></ui-thinking-orb>
      <span>Gem está pensando...</span>
    `;
    messagesEl.appendChild(loadingEl);
    scrollToBottom();

    try {
      const res = await apiClient.post('/chat', {
        conversation_id: activeConversationId,
        message: text,
        mode: selectedMode,
        allow_cloud: false
      });

      loadingEl.remove();

      if (res.conversation_id && res.conversation_id !== activeConversationId) {
        activeConversationId = res.conversation_id;
        await loadConversationList();
      }

      appendMessageBubble({
        role: 'assistant',
        content: res.assistant_message?.content || '',
        modelUsed: res.model_used,
        profileUsed: res.profile_used,
        pendingBatch: res.pending_batch
      });
    } catch (err) {
      loadingEl.remove();
      appendMessageBubble({
        role: 'assistant',
        content: `Error al comunicar con el backend: ${err.message}`,
        modelUsed: 'sistema',
        profileUsed: 'error'
      });
    } finally {
      inputEl.disabled = false;
      inputEl.focus();
    }
  }

  formEl.addEventListener('submit', (e) => {
    e.preventDefault();
    handleSendMessage();
  });

  sendBtn.addEventListener('click', () => {
    handleSendMessage();
  });

  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  convSelect.addEventListener('change', () => {
    const val = convSelect.value || null;
    loadConversationMessages(val);
  });

  newConvBtn.addEventListener('click', () => {
    activeConversationId = null;
    convSelect.value = '';
    renderEmptyConversation();
    inputEl.focus();
  });

  modeSelect.addEventListener('change', () => {
    selectedMode = modeSelect.value || 'auto';
  });

  // Inicializar vista
  loadConversationList().then(() => {
    if (activeConversationId) {
      loadConversationMessages(activeConversationId);
    } else {
      renderEmptyConversation();
    }
  });

  return container;
}
