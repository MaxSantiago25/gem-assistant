# Guía para añadir una conexión externa

En Island Agent, **TODAS las conexiones externas** viven exclusivamente en `backend/app/connections/` (ADR-6 y HARNESS.md §8).

## Pasos para añadir un nuevo proveedor o servicio:
1. Crear un archivo en `backend/app/connections/llm/` (o la subcarpeta temática correspondiente).
2. Heredar de `LLMProvider` (o la interfaz base correspondiente definida en `base.py`).
3. Implementar todos los métodos abstractos: `list_models()`, `chat()`, `stream()`, `health()`.
4. Registrar la nueva instancia en `registry.py`.
5. Asegurarse de que las claves secretas se lean desde Windows Credential Manager (`keyring`) o variables de entorno, NUNCA escritas en código ni guardadas en SQLite.
6. Añadir pruebas con dobles simulados (mocks) en `backend/tests/`.

