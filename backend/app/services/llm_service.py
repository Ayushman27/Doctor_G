"""
Modular LLM Provider Interface.
Supports Local LLM / SLM, Ollama, OpenAI-compatible APIs, and local fallback provider.
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
    """Abstract base class for modular LLM providers."""

    @abc.abstractmethod
    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """Generate structured JSON output from LLM."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama API provider for local open-weights LLMs/SLMs."""

    def __init__(self, base_url: str = "", model_name: str = ""):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model_name = model_name or settings.llm_model or "llama3"

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": f"{system_instruction}\n\n{prompt}",
            "format": "json",
            "stream": False,
        }
        try:
            with httpx.Client(timeout=2.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                raw_response = data.get("response", "{}")
                return json.loads(raw_response)
        except Exception as exc:
            logger.warning("Ollama provider request failed (%s). Falling back to LocalMockProvider.", exc)
            return LocalMockProvider().generate_json(prompt, system_instruction)


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI / Gemini-compatible API provider."""

    def __init__(self, api_key: str = "", base_url: str = "", model_name: str = ""):
        self.api_key = api_key or settings.openai_api_key or settings.gemini_api_key
        self.base_url = (base_url or settings.openai_base_url).rstrip("/")
        self.model_name = model_name or settings.llm_model or "gpt-3.5-turbo"

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as exc:
            logger.warning("OpenAI-compatible request failed (%s). Falling back to LocalMockProvider.", exc)
            return LocalMockProvider().generate_json(prompt, system_instruction)


class LocalMockProvider(LLMProvider):
    """
    Deterministic rule-guided local mock provider.
    Ensures complete operational reliability when external API/Ollama server is unconfigured.
    """

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # Symptom extraction check
        if "canonical key names" in system_instruction.lower() or "allowed symptoms list" in prompt_lower:
            extracted = []
            # Extract common symptoms present in text
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
    if provider_name == "ollama":
        return OllamaProvider()
    elif provider_name in ["openai", "api", "gemini"]:
        return OpenAICompatibleProvider()
    else:
        return LocalMockProvider()
