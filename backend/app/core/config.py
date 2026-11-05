"""
Application configuration using Pydantic Settings.
Environment variables are read from .env file or system environment.
"""

from pathlib import Path
from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    # CORS
    frontend_origin: str = "http://localhost:5173"

    # Application metadata
    app_title: str = "Intelligent Patient Stratification & Drug Candidate Recommendation System"
    app_version: str = "1.0.0"
    app_description: str = (
        "Research/educational decision-support prototype. "
        "Not a medical diagnostic or prescription system."
    )

    # Model directory
    model_dir: Path = (
        BACKEND_DIR
        / "models"
        / "patient_ai_models"
    )

    # LLM Configuration (Google Gemini for cloud deployment)
    llm_provider: str = "gemini"
    llm_model: str = "gemini-1.5-flash"
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"

    # OpenFDA API Configuration
    openfda_api_key: str = "AlqBpoXw03ITN1J2zteR2zg17gCnbQERlGQT3ema"

    # Embedding & RAG Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 5
    rag_score_threshold: float = 0.4

    # Conversational Flow Settings
    max_followup_questions: int = 5
    session_timeout_minutes: int = 60

    class Config:
        env_file = (str(ENV_FILE_PATH), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
