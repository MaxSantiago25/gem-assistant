import { renderHomeView } from '../modules/home/home-view.js';
import { renderChatView } from '../modules/chat/chat-view.js';
import { renderTasksView } from '../modules/tasks/tasks-view.js';
import { renderHabitsView } from '../modules/habits/habits-view.js';
import { renderFocusView } from '../modules/focus/focus-view.js';
import { renderMailView } from '../modules/mail/mail-view.js';
import { renderPcView } from '../modules/pc/pc-view.js';
import { renderSettingsView } from '../modules/settings/settings-view.js';

class Router {
  constructor() {
    this._currentModule = 'home';
    this._viewport = null;

    this._modules = {
      home: { title: 'Inicio', render: renderHomeView },
      chat: { title: 'Chat', render: renderChatView },
      tasks: { title: 'Tareas', render: renderTasksView },
      habits: { title: 'Hábitos', render: renderHabitsView },
      focus: { title: 'Enfoque', render: renderFocusView },
      mail: { title: 'Correo', render: renderMailView },
      pc: { title: 'MiPC', render: renderPcView },
      settings: { title: 'Ajustes', render: renderSettingsView },
    };
  }

  mountViewport(element) {
    this._viewport = element;
    this.renderCurrentModule();
  }

  getModuleTitle(moduleId) {
    return this._modules[moduleId]?.title || 'Gem';
  }

  getCurrentModule() {
    return this._currentModule;
  }

  navigate(moduleId) {
    if (!this._modules[moduleId]) return;
    this._currentModule = moduleId;
    this.renderCurrentModule();
  }

  renderCurrentModule() {
    if (!this._viewport) return;
    const module = this._modules[this._currentModule];
    if (!module) return;

    this._viewport.innerHTML = '';
    const view = module.render();
    this._viewport.appendChild(view);
  }
}

export const router = new Router();

