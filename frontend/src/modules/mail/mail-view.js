import { createEmptyStateView } from '../common/empty-state.js';

export function renderMailView() {
  return createEmptyStateView({
    icon: 'mail',
    title: 'Bandeja de Correo',
    description: 'Resumen inteligente de correo, clasificación automática y redacción asistida de borradores mediante Gmail API.',
    phase: 'Fase 6 (Spec 007)'
  });
}

