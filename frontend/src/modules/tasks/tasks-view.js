import { createEmptyStateView } from '../common/empty-state.js';

export function renderTasksView() {
  return createEmptyStateView({
    icon: 'tasks',
    title: 'Gestor de Tareas',
    description: 'Control de tareas y pendientes organizados por prioridad y fechas de vencimiento, integrados directamente con las acciones del agente.',
    phase: 'Fase 3 (Spec 004)'
  });
}

