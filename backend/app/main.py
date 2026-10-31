"""
Intelligent Patient Stratification & Drug Candidate Recommendation System
FastAPI Application Entry Point

Architecture:
  React Frontend → FastAPI → Preprocessor → XGBoost → Risk Stratification
                                          → Drug Candidate Ranking

Future endpoints reserved:
  /api/slm/explain  — SLM natural language explanation
  /api/rag/search   — RAG clinical context retrieval
  /api/feedback     — User feedback collection
  /api/rl/update    — RL policy update

DISCLAIMER: Research/educational decision-support prototype only.
Not a medical diagnostic or prescription system.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.model_loader import registry
from app.api import health, patient, drugs, models, disease, chat
from rag.retriever import retriever

# ------------------------------------------------------------------ #
#  Logging                                                             #
# ------------------------------------------------------------------ #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
#  Lifespan — model loading at startup                                 #
# ------------------------------------------------------------------ #

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models and RAG vectorstore once when the application starts."""
    logger.info("=== Patient AI System starting up ===")
    try:
        registry.initialize()
        logger.info("=== All ML models loaded successfully ===")
    except RuntimeError as exc:
        logger.critical("CRITICAL: Model loading failed — %s", exc)

    try:
        retriever.load_vectorstore()
        logger.info("=== RAG Medical Vectorstore loaded successfully ===")
    except Exception as exc:
        logger.warning("RAG Vectorstore initialization warning: %s", exc)

    yield  # Application is running

    logger.info("=== Patient AI System shutting down ===")


# ------------------------------------------------------------------ #
#  Application                                                         #
# ------------------------------------------------------------------ #

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ------------------------------------------------------------------ #
#  CORS — configurable via FRONTEND_ORIGIN environment variable        #
# ------------------------------------------------------------------ #

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------ #
#  Global exception handler — never expose stack traces               #
# ------------------------------------------------------------------ #

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s: %s", request.url, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please contact the system administrator."},
    )


# ------------------------------------------------------------------ #
#  API Routers                                                         #
# ------------------------------------------------------------------ #

app.include_router(health.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(drugs.router, prefix="/api")
app.include_router(patient.router, prefix="/api")
app.include_router(disease.router, prefix="/api")
app.include_router(chat.router, prefix="/api")



# ------------------------------------------------------------------ #
#  Root redirect to docs                                               #
# ------------------------------------------------------------------ #

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Intelligent Patient Stratification & Drug Candidate Recommendation System",
        "docs": "/docs",
        "health": "/api/health",
        "disclaimer": "Research/educational prototype only. Not a clinical diagnostic tool.",
    }
