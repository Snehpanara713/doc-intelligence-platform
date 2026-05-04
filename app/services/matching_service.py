import httpx
from datetime import datetime
from app.models.envelope import Envelope, AuditEntry, Decision

CATALOG = [
    {"hs_code": "8471.30.0100", "description": "laptop", "category": "electronics", "restricted": False, "weight": 2},
    {"hs_code": "1006.30", "description": "rice", "category": "food", "restricted": False, "weight": 50},
]


async def call_llm(desc: str):
    # MOCK (replace with OpenAI if key exists)
    if desc and "machine" in desc.lower():
        return {
            "matched_code": "8471.30.0100",
            "confidence": 0.85,
            "reason": "matches computing device"
        }
    return None


async def match_commodity(envelope: Envelope) -> Envelope:

    # ✅ Ensure decision exists (CRITICAL FIX)
    if envelope.decision is None:
        envelope.decision = Decision(route="hitl_review")

    threshold = envelope.processing_instructions.confidence_threshold

    code = envelope.extraction.get("commodity_code")
    desc = envelope.extraction.get("commodity_desc")

    # ✅ If code already good → skip matching
    if code and code.confidence >= threshold:
        return envelope

    try:
        result = await call_llm(desc.value if desc else "")

        if result:
            match_conf = result["confidence"]

            envelope.matching_results = {
                "matched_code": result["matched_code"],
                "match_confidence": match_conf,
                "rationale": result["reason"],
                "fallback_used": True,
                "source": "llm_match"
            }

            # ✅ enforce HITL if low confidence
            if match_conf < 0.7:
                envelope.decision.route = "hitl_review"

        else:
            raise Exception("No match")

    except Exception as e:
        envelope.matching_results = {
            "matched_code": None,
            "match_confidence": 0,
            "rationale": str(e),
            "fallback_used": False,
            "source": "no_match"
        }

        envelope.decision.route = "hitl_review"

    # ✅ Safe audit logging
    envelope.audit.append(
        AuditEntry(
            timestamp=str(datetime.utcnow()),
            service="matching_service",
            action="match",
            envelope_id=envelope.envelope_id,
            result=envelope.decision.route,
            details=envelope.matching_results,
        )
    )

    return envelope