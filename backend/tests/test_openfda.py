"""
Unit test for OpenFDA service integration.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.services.openfda_service import fetch_openfda_drug_info

client = TestClient(app)


def test_openfda_service_fetch():
    info = fetch_openfda_drug_info("loperamide")
    assert info is not None
    assert info["fda_verified"] is True
    assert "loperamide" in info["generic_name"].lower() or "loperamide" in info["brand_name"].lower()


def test_openfda_api_endpoint():
    resp = client.get("/api/drugs/openfda/info", params={"drug_name": "loperamide"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["fda_verified"] is True
