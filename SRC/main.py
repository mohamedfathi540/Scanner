import logging
import os
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from Routes import Base
from Routes import Production
from Helpers.Config import get_settings
from Stores.LLM.LLMProviderFactory import LLMProviderFactory
from Stores.OCR.OCRProviderFactory import OCRProviderFactory
from Stores.LLM.Templates.template_parser import template_parser as TemplateParser
from Utils.metrics import setup_metrics
from Controllers.SecurityController import SecurityController, limiter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("uvicorn.error")

# ── Create FastAPI instance ─────────────────────────────────────────
app = FastAPI()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/api/v1/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Rate-limit middleware & error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5877", "http://localhost:3000", "http://localhost:8101", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
setup_metrics(app)





# ── Startup event ───────────────────────────────────────────────────
@app.on_event("startup")
async def startup_span():
    settings = get_settings()

    # LLM Provider Factory
    llm_provider_factory = LLMProviderFactory(settings)

    # Generation Client
    app.genration_client = llm_provider_factory.create(provider=settings.GENRATION_BACKEND)
    app.genration_client.set_genration_model(model_id=settings.GENRATION_MODEL_ID)

    # Embedding Client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_SIZE,
    )

    # OCR Client
    ocr_provider_factory = OCRProviderFactory(settings)
    ocr_backend = getattr(settings, "OCR_BACKEND", "LLAMAPARSE").upper()
    app.ocr_client = ocr_provider_factory.create(provider=ocr_backend)

    # Template Parser
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE,
        default_language=settings.DEFUALT_LANGUAGE,
    )

    db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DB}"
    engine = create_async_engine(db_url, echo=False)
    
    # Automatically create any missing tables in the database (bypassing Alembic)
    from Models.DB_Schemes.minirag.Schemes import SQLAlchemyBase
    async with engine.begin() as conn:
        await conn.run_sync(SQLAlchemyBase.metadata.create_all)
        
    app.db_client = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    logger.info("[Startup] Application database initialized and schema verified")


# ── Shutdown event ──────────────────────────────────────────────────
@app.on_event("shutdown")
async def shutdown_span():
    logger.info("[Shutdown] Application shutting down")


# ── Include Routers ─────────────────────────────────────────────────

# Public routes (no auth required)
app.include_router(Base.base_router)

# Production route
app.include_router(Production.production_router)


from fastapi.responses import RedirectResponse

# ── Root endpoint redirect ──────────────────────────────────────────
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# ── Rate-limited health endpoint ────────────────────────────────────
@app.get("/api/health")
@limiter.limit("5/minute")
async def health_check(request: Request):
    return {"status": "ok"}