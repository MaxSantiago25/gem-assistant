import { createEmptyStateView } from '../common/empty-state.js';

export function renderFocusView() {
  return createEmptyStateView({
    icon: 'focus',
    title: 'Modo Enfoque',
    description: 'Temporizador Pomodoro con registro de sesiones productivas y vinculación opcional a tareas activas.',
    phase: 'Fase 3 (Spec 004)'
  });
}

