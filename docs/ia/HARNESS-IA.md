# HARNESS DE IA — Guardia de acciones del agente

> No confundir con `HARNESS.md` (reglas de diseño y código). Este documento define **qué puede hacer la IA en el PC** y cómo se garantiza.

## 1. Principio
**El modelo nunca ejecuta nada. Solo propone acciones estructuradas; el harness las valida, las muestra al usuario y las ejecuta.** El harness funciona igual sin importar qué modelo esté detrás.

## 2. Capacidades

| Herramienta | Estado | Qué hace | Reglas clave |
|---|---|---|---|
| `fs_list` | Permitida | Lista nombres, tamaño y fecha | Solo dentro de zonas permitidas; sin leer contenido |
| `fs_mkdir` | Permitida | Crea una carpeta | Solo en zonas; falla si ya existe |
| `fs_move` | Permitida | Mueve archivo o carpeta | Origen y destino en zonas; **nunca sobrescribe**; solo mismo volumen |
| `fs_rename` | Permitida | Cambia el nombre | Mismo directorio; **nunca sobrescribe** |
| `os_open` | Permitida con límites | Abre una app o archivo | Apps de lista blanca; archivos no ejecutables de zonas |
| Borrar | **No existe** | — | No se implementa ni se expone |
| Editar contenido | **No existe** | — | No se implementa ni se expone |
| Shell / comandos | **No existe** | — | No se implementa ni se expone |

## 3. Zonas permitidas (por defecto)
- `Descargas`, `Documentos`, `Escritorio` del usuario.
- El usuario puede añadir o quitar zonas en Ajustes. Las zonas se guardan en `backend/config/harness_policy.json`.

**Siempre prohibido** (aunque el usuario lo intente añadir): `C:\Windows`, `C:\Program Files*`, `C:\ProgramData`, la raíz de cualquier disco, `.ssh`, la carpeta de datos de la propia app y cualquier carpeta de otro usuario.

## 4. Mecanismos

1. **Rutas blindadas.** Se resuelve la ruta real antes de decidir. Se rechazan: rutas relativas, `..`, rutas UNC (`\\servidor\...`), flujos alternos (`archivo.txt:stream`), nombres reservados de Windows (`CON`, `NUL`, `COM1`…), y enlaces simbólicos o *junctions* que salgan de la zona.
2. **Sin sobrescritura.** Se usa `os.rename`, que falla si el destino existe. Prohibido `os.replace` y `shutil.move` en este paquete (sobrescriben o hacen copiar+borrar).
3. **Solo mismo volumen.** `os.rename` falla entre discos: es el comportamiento deseado. No hay "plan B" de copiar y borrar.
4. **Plan → validación → vista previa → aprobación → ejecución.** El usuario ve cada movimiento (origen → destino) antes de que ocurra. Defensa contra instrucciones ocultas en nombres de archivo o correos.
5. **Reporte generado por el harness.** El texto con origen y destino sale del registro, no del modelo. El modelo no puede omitirlo ni inventarlo.
6. **Registro y deshacer.** Cada acción queda en `action_log`. Como todo son movimientos, todo es reversible con "Deshacer" (si el origen original sigue libre).
7. **`os_open` sin shell.** Las apps se abren por identificador de una lista blanca (`apps.json`) con ruta absoluta; se lanzan con lista de argumentos, nunca con una cadena armada por el modelo. Archivos: se abren con la app asociada; se bloquean `.exe .bat .cmd .ps1 .msi .vbs .scr .js .lnk .com .dll`.
8. **Límites.** Máximo 50 operaciones por lote y 100 por hora (configurable).
9. **Lotes atómicos en intención.** Si una operación del lote es rechazada en validación, **ningún** movimiento del lote se ejecuta.
10. **Confirmación por defecto.** Modo "preguntar siempre". Opcional por el usuario: auto-aprobar `fs_mkdir`. Mover y renombrar siempre se aprueba.

## 5. Flujo
```
Modelo ──(tool_call JSON)──► Validador de esquema (Pydantic)
                                    │
                             Guardia de rutas + políticas
                                    │ rechazo → ACCION_RECHAZADA (el modelo recibe el código)
                                    ▼
                          Vista previa en la isla (origen → destino)
                                    │ usuario aprueba
                                    ▼
                            Ejecutor (os.rename / mkdir)
                                    │
                               action_log (SQLite)
                                    │
                    Reporte generado por el harness
```

## 6. Reporte al usuario (formato fijo)
```
Movido:  C:\Users\...\Descargas\factura.pdf
      →  C:\Users\...\Documentos\Facturas\factura.pdf
```
Renombrado y carpeta creada usan el mismo formato (`Renombrado:`, `Carpeta creada:`).

## 7. Registro (`action_log`) — migración `0002_action_log.sql`
```sql
CREATE TABLE action_log (
  id            INTEGER PRIMARY KEY,
  batch_id      TEXT NOT NULL,
  ts            TEXT NOT NULL,
  tool          TEXT NOT NULL,              -- fs_move, fs_rename, fs_mkdir, os_open
  source_path   TEXT,
  dest_path     TEXT,
  status        TEXT NOT NULL CHECK (status IN
                ('proposed','rejected','approved','done','failed','undone')),
  error_code    TEXT,
  model_profile TEXT,                       -- rapido / herramientas / nube
  undo_of       INTEGER REFERENCES action_log(id)
);
CREATE INDEX idx_action_log_batch ON action_log(batch_id);
```

## 8. Códigos de error (se devuelven al modelo y al usuario)
`RUTA_NO_ABSOLUTA` · `FUERA_DE_ZONA` · `ZONA_PROHIBIDA` · `UNC_NO_PERMITIDO` · `ADS_NO_PERMITIDO` · `NOMBRE_RESERVADO` · `DESTINO_EXISTE` · `ORIGEN_NO_EXISTE` · `OTRO_VOLUMEN` · `LIMITE_EXCEDIDO` · `EXTENSION_BLOQUEADA` · `APP_NO_AUTORIZADA` · `HERRAMIENTA_NO_PERMITIDA`

## 9. Estructura de código
```
backend/app/harness_ia/
├─ policy.py        ← carga harness_policy.json (zonas, límites, extensiones)
├─ path_guard.py    ← resolve_in_zone(), reglas de rutas
├─ schemas.py       ← esquemas Pydantic de cada herramienta
├─ tools/           ← fs_list.py, fs_mkdir.py, fs_move.py, fs_rename.py, os_open.py
├─ executor.py      ← valida → registra → ejecuta
├─ audit.py         ← action_log
├─ undo.py          ← deshacer por batch_id
└─ report.py        ← texto de reporte
```

## 10. Pruebas obligatorias (`backend/tests/harness_ia/`)
- Rutas con `..`, UNC, ADS, nombres reservados, mayúsculas/minúsculas mezcladas, barras mixtas.
- *Junction* y enlace simbólico que apuntan fuera de la zona.
- Mover sobre un destino existente → debe fallar sin cambios.
- Mover entre discos → `OTRO_VOLUMEN`.
- Lote con una acción inválida → no se ejecuta ninguna.
- Deshacer restaura el estado original; deshacer con origen ocupado falla limpio.
- `os_open` con `.exe`, `.bat`, `.ps1` → bloqueado. App fuera de lista → bloqueada.
- Cadenas de inyección en nombres de archivo no alteran el plan.
- **Prueba estática:** falla el CI si en `harness_ia/` aparece `os.remove`, `os.unlink`, `os.rmdir`, `shutil.rmtree`, `shutil.move`, `os.replace`, `subprocess` con `shell=True` o `open(..., "w"/"a"/"r+")`.

## 11. Fuera de alcance (v1)
Leer el contenido de archivos, copiar archivos, mover entre discos, acciones en red, lanzar comandos arbitrarios.

## 12. Definición de terminado
- [ ] Todas las pruebas de la sección 10 pasan.
- [ ] No existe ninguna ruta de código para borrar, editar o ejecutar comandos.
- [ ] El reporte siempre lo genera el harness.
- [ ] Cada acción queda en `action_log` y se puede deshacer.

