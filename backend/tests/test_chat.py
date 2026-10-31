"""
Unit tests for Conversational Medical Chat Endpoints, Profile Collection,
Symptom-specific questioning, and clinical test cases.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.model_loader import registry

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    registry.initialize()


def test_start_chat():
    response = client.post("/api/chat/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "symptoms" in data["message"].lower() or "health problems" in data["message"].lower()
    assert data["stage"] == "INITIAL_COMPLAINT"


def test_case_1_pediatric_gastroenteritis():
    """CASE 1: Age 10, diarrhea + mild abdominal pain -> pediatric GI considered, no adult CV diseases."""
    start_res = client.post("/api/chat/start").json()
    sid = start_res["session_id"]

    # 1. Initial symptoms
    r1 = client.post("/api/chat/message", json={"session_id": sid, "message": "I have loose motion and stomach pain."}).json()
    assert r1["type"] == "profile_collection"
    assert "old are you" in r1["message"].lower() or "age" in r1["message"].lower()

    # 2. Provide age 10
    r2 = client.post("/api/chat/message", json={"session_id": sid, "message": "10 years old"}).json()
    assert r2["type"] == "profile_collection"

    # 3. Provide sex
    r3 = client.post("/api/chat/message", json={"session_id": sid, "message": "Male"}).json()
    assert r3["type"] == "profile_collection"

    # 4. Provide weight
    r4 = client.post("/api/chat/message", json={"session_id": sid, "message": "32 kg"}).json()
    assert r4["type"] in ["followup_question", "final_assessment"]

    # Fast forward through questions to final assessment
    res = r4
    for ans in ["Since yesterday", "3 times", "No blood", "Keeping fluids down fine", "Home food"]:
        if res["type"] == "final_assessment":
            break
        res = client.post("/api/chat/message", json={"session_id": sid, "message": ans}).json()

    assert res["type"] == "final_assessment"
    assert res["assessment"] is not None
    top_cond = res["assessment"]["likely_conditions"][0]["condition"]
    assert "Pediatric" in top_cond or "Gastroenteritis" in top_cond
    assert not any("Heart Attack" in c["condition"] for c in res["assessment"]["likely_conditions"])


def test_case_2_young_adult_postprandial_chest_discomfort():
    """CASE 2: Age 22, diarrhea + mild chest discomfort after eating -> questions asked, no raw 16% heart attack."""
    start_res = client.post("/api/chat/start").json()
    sid = start_res["session_id"]

    # 1. Initial symptoms
    r1 = client.post("/api/chat/message", json={"session_id": sid, "message": "I have loose motion and chest discomfort."}).json()
    assert r1["type"] == "profile_collection"

    # Age 22
    r2 = client.post("/api/chat/message", json={"session_id": sid, "message": "22"}).json()
    assert r2["type"] == "profile_collection"

    # Male
    r3 = client.post("/api/chat/message", json={"session_id": sid, "message": "Male"}).json()

    # 65 kg
    r4 = client.post("/api/chat/message", json={"session_id": sid, "message": "65 kg"}).json()
    assert r4["type"] in ["followup_question", "final_assessment"]

    # Complete follow-up questions detailing post-prandial symptoms
    res = r4
    answers = [
        "Since yesterday",
        "Started after eating dinner",
        "Worse when lying down",
        "No, none of these warning signs",
        "Burning sensation / heartburn"
    ]
    for a in answers:
        if res["type"] == "final_assessment":
            break
        res = client.post("/api/chat/message", json={"session_id": sid, "message": a}).json()

    assert res["type"] == "final_assessment"
    likely_names = [c["condition"] for c in res["assessment"]["likely_conditions"]]
    assert any("Gastroenteritis" in name or "GERD" in name for name in likely_names)
    assert res["assessment"]["safety_screening"]["screened"] is True


def test_case_3_age_55_severe_chest_pressure_emergency():
    """CASE 3: Age 55, severe chest pressure + sweating + shortness of breath -> URGENT ATTENTION."""
    start_res = client.post("/api/chat/start").json()
    sid = start_res["session_id"]

    # Immediate red flag in message
    msg = "I am having severe crushing chest pressure and sweating and cannot breathe!"
    r = client.post("/api/chat/message", json={"session_id": sid, "message": msg}).json()
    assert r["type"] == "urgent_attention"
    assert "EMERGENCY" in r["message"] or "SAFETY ESCALATION" in r["message"]
    assert len(r["red_flags"]) > 0


def test_case_4_age_30_diarrhea_vomiting_fever():
    """CASE 4: Age 30, diarrhea + vomiting + fever -> asks duration, dehydration, assesses GI causes."""
    start_res = client.post("/api/chat/start").json()
    sid = start_res["session_id"]

    # Initial symptoms with profile in text
    r1 = client.post("/api/chat/message", json={"session_id": sid, "message": "I am 30 years old female 60kg with diarrhea, vomiting, and fever."}).json()
    assert r1["type"] in ["followup_question", "final_assessment"]

    res = r1
    for ans in ["2 days", "5 times", "No blood", "Keeping fluids down fine", "Home food"]:
        if res["type"] == "final_assessment":
            break
        res = client.post("/api/chat/message", json={"session_id": sid, "message": ans}).json()

    assert res["type"] == "final_assessment"
    likely_names = [c["condition"] for c in res["assessment"]["likely_conditions"]]
    assert any("Gastroenteritis" in name or "Enteritis" in name for name in likely_names)


def test_case_5_age_70_chest_pressure_shortness_of_breath_sweating():
    """CASE 5: Age 70, chest pressure + shortness of breath + sweating -> strong safety escalation."""
    start_res = client.post("/api/chat/start").json()
    sid = start_res["session_id"]

    msg = "I am 70 years old with chest pressure, shortness of breath, and cold sweats."
    r = client.post("/api/chat/message", json={"session_id": sid, "message": msg}).json()
    assert r["type"] == "urgent_attention"
    assert len(r["red_flags"]) > 0
