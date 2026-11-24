import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("ISLAND_PORT", 8765))
    host = "127.0.0.1"  # Estricto según arquitectura (solo loopback local)
    uvicorn.run("app.main:app", host=host, port=port, reload=False)

