from pydantic import BaseModel, Field
from typing import List, Optional, Literal

ToolName = Literal["fs_list", "fs_mkdir", "fs_move", "fs_rename", "os_open"]

class FsListParams(BaseModel):
    path: str = Field(..., description="Ruta absoluta de la carpeta a listar")

class FsMkdirParams(BaseModel):
    path: str = Field(..., description="Ruta absoluta de la nueva carpeta a crear")

class FsMoveParams(BaseModel):
    source: str = Field(..., description="Ruta absoluta del archivo o carpeta a mover")
    destination: str = Field(..., description="Ruta absoluta de destino (mismo volumen, no debe existir)")

class FsRenameParams(BaseModel):
    path: str = Field(..., description="Ruta absoluta del archivo a renombrar")
    new_name: str = Field(..., description="Nuevo nombre del archivo (mismo directorio, sin barras)")

class OsOpenParams(BaseModel):
    app_id: Optional[str] = Field(None, description="Identificador de la app registrada (ej. notepad, calc)")
    file_path: Optional[str] = Field(None, description="Ruta absoluta del archivo no ejecutable a abrir")

class ActionOperation(BaseModel):
    tool: ToolName
    params: dict
    source_path: Optional[str] = None
    dest_path: Optional[str] = None

class ActionBatch(BaseModel):
    batch_id: str
    operations: List[ActionOperation]
    model_profile: str = "herramientas"

