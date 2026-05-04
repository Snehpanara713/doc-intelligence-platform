from datetime import datetime, timedelta
from app.models.envelope import Envelope, AuditEntry, Decision

# async def validate_envelope(envelope: Envelope) -> Envelope:
#     threshold = envelope.processing_instructions.confidence_threshold
#     hitl = envelope.processing_instructions.hitl_on_failure

#     errors = []
#     low_conf = []

#     extraction = envelope.extraction

#     required_fields = ["shipment_id", "recipient_name"]

#     for field in required_fields:
#         if field not in extraction or not extraction[field].value:
#             errors.append(field)

#     if not (
#         extraction.get("commodity_code") or extraction.get("commodity_desc")
#     ):
#         errors.append("commodity_code/commodity_desc")

#     # confidence check
#     for key, val in extraction.items():
#         if val.confidence is not None and val.confidence < threshold:
#             low_conf.append(key)

#     # date validation
#     if "ship_date" in extraction:
#         try:
#             date = datetime.fromisoformat(extraction["ship_date"].value)
#             if date > datetime.now() or date < datetime.now() - timedelta(days=365):
#                 errors.append("ship_date_invalid")
#         except:
#             errors.append("ship_date_format")

#     if errors:
#         route = "hitl_review" if hitl else "rejected"
#     elif low_conf:
#         route = "hitl_review" if hitl else "rejected"
#     else:
#         route = "auto_approve"

#     envelope.validation_results = {
#         "errors": errors,
#         "low_confidence": low_conf,
#     }

#     envelope.decision = Decision(route=route)

#     envelope.audit.append(
#         AuditEntry(
#             timestamp=str(datetime.utcnow()),
#             service="validation_service",
#             action="validate",
#             envelope_id=envelope.envelope_id,
#             result=route,
#             details={"errors": errors, "low_conf": low_conf},
#         )
#     )

#     if errors:
#         raise ValueError(errors)

#     return envelope

async def validate_envelope(envelope: Envelope) -> Envelope:
    threshold = envelope.processing_instructions.confidence_threshold
    hitl = envelope.processing_instructions.hitl_on_failure

    errors = []
    low_conf = []

    extraction = envelope.extraction

    # ✅ required fields
    for field in ["shipment_id", "recipient_name"]:
        val = extraction.get(field)
        if not val or not val.value:
            errors.append(field)

    # ✅ commodity check (FIXED)
    code = extraction.get("commodity_code")
    desc = extraction.get("commodity_desc")

    if (not code or not code.value) and (not desc or not desc.value):
        errors.append("commodity_code/commodity_desc")

    # ✅ confidence check
    for key, val in extraction.items():
        if val and val.confidence is not None and val.confidence < threshold:
            low_conf.append(key)

    # ✅ date validation
    if "ship_date" in extraction:
        try:
            date_val = extraction["ship_date"]
            if date_val and date_val.value:
                date = datetime.fromisoformat(date_val.value)
                if date > datetime.now() or date < datetime.now() - timedelta(days=365):
                    errors.append("ship_date_invalid")
        except:
            errors.append("ship_date_format")

    # ✅ decision
    if errors:
        route = "hitl_review" if hitl else "rejected"
    elif low_conf:
        route = "hitl_review" if hitl else "rejected"
    else:
        route = "auto_approve"

    envelope.validation_results = {
        "errors": errors,
        "low_confidence": low_conf,
    }

    envelope.decision = Decision(route=route)

    # ✅ audit
    envelope.audit.append(
        AuditEntry(
            timestamp=str(datetime.utcnow()),
            service="validation_service",
            action="validate",
            envelope_id=envelope.envelope_id,
            result=route,
            details={"errors": errors, "low_conf": low_conf},
        )
    )

    # ❗ raise error only for missing required fields
    if errors:
        raise ValueError(errors)

    return envelope