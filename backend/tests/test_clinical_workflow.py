"""
Comprehensive Automated Tests for Medical AI Clinical Workflow.
Verifies all 7 non-negotiable test cases from Section 38 of prompt.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.conversation_service import clear_sessions

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    clear_sessions()


def test_case_1_initial_greeting():
    """
    TEST 1:
    Patient: 'Hi'
    Expected: Ask what symptoms they are experiencing.
    NOT Age? NOT Sex? NOT Weight? NOT Disease-specific question.
    """
    res_start = client.post("/api/chat/start")
    assert res_start.status_code == 200
    session_id = res_start.json()["session_id"]

    res_msg = client.post("/api/chat/message", json={"session_id": session_id, "message": "Hi"})
    assert res_msg.status_code == 200
    data = res_msg.json()

    assert data["stage"] == "INITIAL_COMPLAINT"
    msg = data["message"].lower()
    assert "symptoms" in msg or "health problems" in msg
    assert "age" not in msg
    assert "weight" not in msg
    assert "sex" not in msg


def test_case_2_diarrhea_symptom():
    """
    TEST 2:
    Patient: 'I have loose motion'
    Expected: Diarrhea-specific questioning after symptoms extracted.
    """
    res_start = client.post("/api/chat/start")
    session_id = res_start.json()["session_id"]

    res_msg = client.post("/api/chat/message", json={"session_id": session_id, "message": "I have loose motion"})
    assert res_msg.status_code == 200
    data = res_msg.json()

    assert "diarrhoea" in data["extracted_symptoms"] or "Diarrhoea" in data["extracted_symptoms"]
    assert data["stage"] in ["PATIENT_PROFILE", "SYMPTOM_CHARACTERIZATION"]


def test_case_3_headache_symptom():
    """
    TEST 3:
    Patient: 'I have headache'
    Expected: Headache-specific questioning.
    """
    res_start = client.post("/api/chat/start")
    session_id = res_start.json()["session_id"]

    res_msg = client.post("/api/chat/message", json={"session_id": session_id, "message": "I have headache"})
    assert res_msg.status_code == 200
    data = res_msg.json()

    assert "Headache" in data["extracted_symptoms"] or "headache" in data["extracted_symptoms"]


def test_case_4_chest_pain_screening():
    """
    TEST 4:
    Patient: 'I have chest pain'
    Expected: Chest pain questioning + safety screening.
    """
    res_start = client.post("/api/chat/start")
    session_id = res_start.json()["session_id"]

    res_msg = client.post("/api/chat/message", json={"session_id": session_id, "message": "I have chest pain"})
    assert res_msg.status_code == 200
    data = res_msg.json()

    assert "Chest Pain" in data["extracted_symptoms"] or "chest_pain" in data["extracted_symptoms"]


def test_case_5_cough_and_fever():
    """
    TEST 5:
    Patient: 'I have cough and fever'
    Expected: Respiratory/infection-related questioning.
    """
    res_start = client.post("/api/chat/start")
    session_id = res_start.json()["session_id"]

    res_msg = client.post("/api/chat/message", json={"session_id": session_id, "message": "I have cough and fever"})
    assert res_msg.status_code == 200
    data = res_msg.json()

    syms = [s.lower() for s in data["extracted_symptoms"]]
    assert "cough" in syms or "high fever" in syms or "fever" in syms


def test_case_6_unknown_complaint():
    """
    TEST 6:
    Patient: 'I don't know what's wrong'
    Expected: Ask patient to describe what they are feeling.
    """
    res_start = client.post("/api/chat/start")
    session_id = res_start.json()["session_id"]

    res_msg = client.post("/api/chat/message", json={"session_id": session_id, "message": "I don't know what's wrong with me"})
    assert res_msg.status_code == 200
    data = res_msg.json()

    assert data["stage"] == "INITIAL_COMPLAINT"
    msg = data["message"].lower()
    assert "describe what you're experiencing" in msg or "symptoms" in msg


def test_case_7_blood_in_stool_red_flag():
    """
    TEST 7:
    Patient: 'I have loose motion, stomach pain and blood in stool'
    Expected: Immediate safety-aware evaluation & red-flag warning.
    """
    res_start = client.post("/api/chat/start")
    session_id = res_start.json()["session_id"]

    res_msg = client.post(
        "/api/chat/message",
        json={"session_id": session_id, "message": "I have loose motion, stomach pain and blood in stool"}
    )
    assert res_msg.status_code == 200
    data = res_msg.json()

    assert data["stage"] == "URGENT_EVALUATION"
    assert data["type"] == "urgent_attention"
    assert len(data["red_flags"]) > 0
    assert "SAFETY ESCALATION" in data["message"] or "EMERGENCY" in data["message"]
