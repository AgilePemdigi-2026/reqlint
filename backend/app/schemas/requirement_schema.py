from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.core.config import settings


class AuditRequest(BaseModel):
    # P0/SEC-02 companion: bound legacy endpoint input to the same limit as the
    # main pipeline (MAX_TEXT_CHARS) so the CPU-heavy path cannot be fed
    # arbitrarily large payloads.
    requirement_text: str = Field(
        ...,
        max_length=settings.MAX_TEXT_CHARS,
        json_schema_extra={"example": "Sebagai pembeli, saya sebaiknya dapat membayar dengan cepat, sehingga transaksi segera selesai."}
    )
    override_language: Optional[str] = Field(
        None,
        description="Optional 'id' or 'en' language override",
        json_schema_extra={"example": "id"}
    )

class AuditResponse(BaseModel):
    requirement_text: str
    detected_language: str
    quality_score: float
    ambiguity_index: float
    completeness_score: float
    verifiability_score: float
    smells: List[Dict[str, Any]]
    revisions: List[Dict[str, Any]]

