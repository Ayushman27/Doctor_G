"""Unit tests for Disease Prediction ML Model."""

import pytest
from app.core.model_loader import registry
from app.services.disease_service import predict_disease_from_symptoms


@pytest.fixture(scope="module", autouse=True)
def init_registry():
    """Ensure ML registry is loaded before tests."""
    registry.initialize()


def test_predict_disease_valid_symptoms():
    symptoms = ["high_fever", "cough", "fatigue"]
    result = predict_disease_from_symptoms(symptoms, top_k=5)

    assert result.top_prediction is not None
    assert len(result.predictions) == 5
    assert len(result.matched_symptoms) > 0
    assert result.predictions[0].probability >= result.predictions[1].probability


def test_predict_disease_unknown_symptoms():
    symptoms = ["high_fever", "unknown_alien_symptom_xyz"]
    result = predict_disease_from_symptoms(symptoms, top_k=3)


    assert len(result.predictions) == 3
    assert "unknown_alien_symptom_xyz" in result.unmatched_symptoms


def test_predict_disease_no_valid_symptoms():
    symptoms = ["completely_fake_symptom_123"]
    with pytest.raises(ValueError, match="None of the provided symptoms were recognized"):
        predict_disease_from_symptoms(symptoms)
