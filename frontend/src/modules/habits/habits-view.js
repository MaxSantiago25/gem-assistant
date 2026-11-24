import { createEmptyStateView } from '../common/empty-state.js';

export function renderHabitsView() {
  return createEmptyStateView({
    icon: 'habits',
    title: 'Registro de Hábitos',
    description: 'Seguimiento de rachas y hábitos diarios para mantener constancia en tus rutinas personales y profesionales.',
    phase: 'Fase 3 (Spec 004)'
  });
}

