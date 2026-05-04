from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class FieldValue(BaseModel):
    value: Optional[str]
    confidence: Optional[float]

class ProcessingInstructions(BaseModel):
    workflow: str
    confidence_threshold: float
    hitl_on_failure: bool

class Decision(BaseModel):
    route: Optional[str] = None

class AuditEntry(BaseModel):
    timestamp: str
    service: str
    action: str
    envelope_id: str
    result: str
    details: Dict[str, Any]

class Envelope(BaseModel):
    envelope_id: str
    schema_version: str
    extraction: Dict[str, FieldValue]
    processing_instructions: ProcessingInstructions

    validation_results: Optional[Dict] = None
    matching_results: Optional[Dict] = None
    decision: Optional[Decision] = None
    audit: List[AuditEntry] = Field(default_factory=list)