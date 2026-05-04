import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_happy_path_auto_approve():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "envelope_id": "env_1",
            "schema_version": "v1",
            "extraction": {
                "shipment_id": {"value": "SHP-001", "confidence": 0.95},
                "recipient_name": {"value": "ABC Corp", "confidence": 0.92},
                "commodity_code": {"value": "8471.30.0100", "confidence": 0.90}
            },
            "processing_instructions": {
                "workflow": "manifest-v1",
                "confidence_threshold": 0.80,
                "hitl_on_failure": True
            },
            "audit": []
        }

        response = await ac.post("/process", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data["decision"]["route"] == "auto_approve"


@pytest.mark.asyncio
async def test_low_confidence_recipient_hitl():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "envelope_id": "env_2",
            "schema_version": "v1",
            "extraction": {
                "shipment_id": {"value": "SHP-002", "confidence": 0.95},
                "recipient_name": {"value": "XYZ Corp", "confidence": 0.60},
                "commodity_code": {"value": "8471.30.0100", "confidence": 0.90}
            },
            "processing_instructions": {
                "workflow": "manifest-v1",
                "confidence_threshold": 0.80,
                "hitl_on_failure": True
            },
            "audit": []
        }

        response = await ac.post("/process", json=payload)
        data = response.json()

        assert data["decision"]["route"] == "hitl_review"


@pytest.mark.asyncio
async def test_low_confidence_code_triggers_llm():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "envelope_id": "env_3",
            "schema_version": "v1",
            "extraction": {
                "shipment_id": {"value": "SHP-003", "confidence": 0.95},
                "recipient_name": {"value": "XYZ Logistics", "confidence": 0.90},
                "commodity_code": {"value": "8471.30.0100", "confidence": 0.50},
                "commodity_desc": {"value": "portable data processing machine", "confidence": 0.95}
            },
            "processing_instructions": {
                "workflow": "manifest-v1",
                "confidence_threshold": 0.80,
                "hitl_on_failure": True
            },
            "audit": []
        }

        response = await ac.post("/process", json=payload)
        data = response.json()

        assert "matching_results" in data
        assert data["matching_results"]["source"] in ["llm_match", "catalog_exact"]


@pytest.mark.asyncio
async def test_invalid_envelope():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "envelope_id": "env_invalid",
            "schema_version": "v1",
            "extraction": {},
            "processing_instructions": {
                "workflow": "manifest-v1",
                "confidence_threshold": 0.80,
                "hitl_on_failure": True
            },
            "audit": []
        }

        response = await ac.post("/process", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert "validation_results" in data
        assert data["decision"]["route"] == "hitl_review"


@pytest.mark.asyncio
async def test_llm_failure_graceful(monkeypatch):
    async def mock_llm_fail(desc):
        raise Exception("LLM timeout")

    from app.services import matching_service
    monkeypatch.setattr(matching_service, "call_llm", mock_llm_fail)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "envelope_id": "env_5",
            "schema_version": "v1",
            "extraction": {
                "shipment_id": {"value": "SHP-005", "confidence": 0.95},
                "recipient_name": {"value": "ABC", "confidence": 0.90},
                "commodity_code": {"value": "8471.30.0100", "confidence": 0.50},
                "commodity_desc": {"value": "portable machine", "confidence": 0.95}
            },
            "processing_instructions": {
                "workflow": "manifest-v1",
                "confidence_threshold": 0.80,
                "hitl_on_failure": True
            },
            "audit": []
        }

        response = await ac.post("/process", json=payload)
        data = response.json()

        assert data["matching_results"]["source"] == "no_match"
        assert data["decision"]["route"] == "hitl_review"