import { createEmptyStateView } from '../common/empty-state.js';

export function renderSettingsView() {
  return createEmptyStateView({
    icon: 'settings',
    title: 'Ajustes del Sistema',
    description: 'Configuración del proveedor LLM activo (LM Studio / Gemini), almacenamiento de claves de API en Windows Credential Manager y preferencias de la interfaz.',
    phase: 'Fase 2+ (Spec 002 y 005)'
  });
}

