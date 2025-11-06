from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import chat, dashboard, health

# Función simple para parsear CORS_ORIGINS
def parse_cors_origins(cors_str: str) -> list[str]:
    """Convierte string de CORS a lista"""
    if not cors_str or cors_str.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in cors_str.split(",") if origin.strip()]

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend RAG para análisis gerencial de Calzando a México",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# Root endpoint
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciado")
    print(f"📝 Documentación: http://localhost:8000/docs")
    print(f"🌍 Entorno: {settings.APP_ENV}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al cerrar la aplicación"""
    print("👋 Aplicación cerrada")