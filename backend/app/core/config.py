import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Island Agent Backend"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = int(os.environ.get("ISLAND_PORT", 8765))
    session_token: str = os.environ.get("ISLAND_TOKEN", "dev-island-token")
    database_path: str = os.environ.get("ISLAND_DB_PATH", "data/island.db")

settings = Settings()

