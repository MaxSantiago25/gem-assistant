-- Migración 0002: Tabla de auditoría y deshacer de acciones del agente (HARNESS-IA.md §7)

CREATE TABLE IF NOT EXISTS action_log (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id      TEXT NOT NULL,
  ts            TEXT NOT NULL,
  tool          TEXT NOT NULL,
  source_path   TEXT,
  dest_path     TEXT,
  status        TEXT NOT NULL CHECK (status IN
                ('proposed','rejected','approved','done','failed','undone')),
  error_code    TEXT,
  model_profile TEXT,
  undo_of       INTEGER REFERENCES action_log(id)
);

CREATE INDEX IF NOT EXISTS idx_action_log_batch ON action_log(batch_id);

