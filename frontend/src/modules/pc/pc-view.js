import { createEmptyStateView } from '../common/empty-state.js';

export function renderPcView() {
  return createEmptyStateView({
    icon: 'pc',
    title: 'Mi PC',
    description: 'Monitoreo de CPU, memoria RAM, almacenamiento y batería con herramientas seguras del sistema sujetas a confirmación explícita.',
    phase: 'Fase 5 (Spec 006)'
  });
}

