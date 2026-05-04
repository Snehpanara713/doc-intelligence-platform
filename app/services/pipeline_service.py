from app.services.validation_service import validate_envelope
from app.services.matching_service import match_commodity

async def process_pipeline(envelope):
    envelope = await validate_envelope(envelope)

    code = envelope.extraction.get("commodity_code")
    threshold = envelope.processing_instructions.confidence_threshold

    if code and code.confidence < threshold:
        envelope = await match_commodity(envelope)

    return envelope