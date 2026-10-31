"""
Application configuration using Pydantic Settings.
Environment variables are read from .env file or system environment.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


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
        Path(__file__).resolve().parent.parent.parent
        / "models"
        / "patient_ai_models"
    )

    # LLM Configuration
    llm_provider: str = "ollama"
    llm_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    gemini_api_key: str = ""

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
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
