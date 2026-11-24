from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.migrator import run_migrations
from app.api import health, auth, settings as settings_api, conversations, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ejecutar migraciones automáticas al arrancar (CA-4 de Spec 002)
    print(f"[Backend] Iniciando {settings.app_name} v{settings.version}")
    applied = run_migrations()
    if applied:
        print(f"[Backend] Migraciones ejecutadas: {applied}")
    else:
        print("[Backend] Base de datos al día.")
    yield
    print("[Backend] Deteniendo servicio.")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url="/docs",
    lifespan=lifespan
)

# CORS: orígenes permitidos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers con prefijo api/v1
app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["health"])
app.include_router(auth.router, prefix=settings.api_v1_prefix, tags=["auth"])
app.include_router(settings_api.router, prefix=settings.api_v1_prefix, tags=["settings"])
app.include_router(conversations.router, prefix=settings.api_v1_prefix, tags=["conversations"])
app.include_router(chat.router, prefix=settings.api_v1_prefix, tags=["chat"])
