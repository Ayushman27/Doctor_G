"""Unit tests for Clinical Safety and Red-Flag Emergency Detection."""

from app.services.safety_service import check_emergency_symptoms


def test_safety_normal_message():
    res = check_emergency_symptoms("I have a low fever and slight cough for 2 days.")
    assert res["is_emergency"] is False
    assert res["continue_chat"] is True
    assert len(res["red_flags"]) == 0


def test_safety_chest_pain_emergency():
    res = check_emergency_symptoms("I am experiencing severe chest pain radiating to my left arm.")
    assert res["is_emergency"] is True
    assert res["continue_chat"] is True
    assert len(res["red_flags"]) > 0


def test_safety_respiratory_distress_emergency():
    res = check_emergency_symptoms("I am gasping for air and turning blue.")
    assert res["is_emergency"] is True
    assert res["continue_chat"] is True
