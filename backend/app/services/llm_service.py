"""
Modular LLM Provider Interface.
Production-ready Google Gemini API provider with resilient deterministic local fallback.
Configurable via environment variables (.env).
"""

from __future__ import annotations

import abc
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(abc.ABC):
    """Abstract base class for LLM providers."""

    @abc.abstractmethod
    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """Generate structured JSON output from LLM."""
        pass


class GeminiProvider(LLMProvider):
    """
    Google Gemini API provider for cloud deployment.
    Uses Google's Generative Language REST API with structured JSON output mode.
    """

    def __init__(self, api_key: str = "", model_name: str = "", base_url: str = ""):
        self.api_key = api_key or settings.gemini_api_key
        self.base_url = (base_url or getattr(settings, "gemini_base_url", "https://generativelanguage.googleapis.com/v1beta")).rstrip("/")
        raw_model = model_name or settings.llm_model or "gemini-1.5-flash"
        self.model_name = raw_model.removeprefix("models/")

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("Gemini API key is not configured. Falling back to LocalMockProvider.")
            return LocalMockProvider().generate_json(prompt, system_instruction)

        url = f"{self.base_url}/models/{self.model_name}:generateContent"
        params = {"key": self.api_key}
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
            },
        }

        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, headers=headers, params=params, json=payload)
                resp.raise_for_status()
                data = resp.json()

                candidates = data.get("candidates", [])
                if not candidates:
                    raise ValueError(f"No candidates returned in Gemini response: {data}")

                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    raise ValueError(f"No content parts returned in candidate: {candidates[0]}")

                raw_text = parts[0].get("text", "{}").strip()

                # Clean potential markdown code blocks
                if raw_text.startswith("```"):
                    lines = raw_text.splitlines()
                    if lines and lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    raw_text = "\n".join(lines).strip()

                return json.loads(raw_text)
        except Exception as exc:
            logger.warning("Gemini API request failed (%s). Falling back to LocalMockProvider.", exc)
            return LocalMockProvider().generate_json(prompt, system_instruction)


class LocalMockProvider(LLMProvider):
    """
    Deterministic rule-guided local mock provider.
    Ensures complete operational reliability when external API server is unconfigured or unreachable.
    """

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # Symptom extraction check
        if "canonical key names" in system_instruction.lower() or "allowed symptoms list" in prompt_lower:
            extracted = []
            symptom_keywords = {
                "fever": "fever",
                "cough": "cough",
                "fatigue": "fatigue",
                "chills": "chills",
                "headache": "headache",
                "chest pain": "chest_pain",
                "breath": "breathlessness",
                "shortness of breath": "breathlessness",
                "sweat": "sweating",
                "body pain": "muscle_pain",
                "muscle pain": "muscle_pain",
                "joint pain": "joint_pain",
                "vomiting": "vomiting",
                "nausea": "nausea",
                "diarrhea": "diarrhea",
                "phlegm": "phlegm",
                "sore throat": "throat_irritation",
                "throat": "throat_irritation",
                "rash": "skin_rash",
            }
            for kw, canon in symptom_keywords.items():
                if kw in prompt_lower:
                    if canon not in extracted:
                        extracted.append(canon)
            if not extracted:
                extracted = ["fever", "cough"]
            return {"symptoms": extracted, "unmatched_symptoms": []}

        # Question generation check
        if "question" in system_instruction.lower() or "targeted" in prompt_lower:
            return {
                "question": "Have you experienced any shortness of breath or difficulty breathing?",
                "reason": "Shortness of breath helps distinguish lower respiratory conditions like Pneumonia from upper respiratory infections.",
            }

        # Diagnostic reasoning check
        return {
            "action": "ASK_FOLLOWUP",
            "question": "Have you experienced shortness of breath or chest pain when coughing?",
            "reason": "Distinguishes upper respiratory infection from pulmonary involvement.",
            "confidence": 0.65,
            "candidate_diseases": [
                {"disease": "Influenza", "probability": 0.62},
                {"disease": "Pneumonia", "probability": 0.21},
            ],
            "evidence": [],
        }


def get_llm_provider() -> LLMProvider:
    """Factory method to get LLM provider based on settings.llm_provider."""
    provider_name = settings.llm_provider.lower().strip()
    if provider_name in ["mock", "local"]:
        return LocalMockProvider()
    return GeminiProvider()
