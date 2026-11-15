from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CreateAuditRequest(BaseModel):
    konten: str = Field(..., description="Draf kebutuhan teks pengguna")
    judul_klausul: Optional[str] = None
    tipe_masukan: str = Field(default="manual", description="manual atau pdf")
    id_dokumen: Optional[int] = None
    evaluator: str = Field(
        default="rule_based",
        description="rule_based | traditional_ml | llm (Task 06 evaluator selection)"
    )

class ApplyAuditRequest(BaseModel):
    terapkan: List[str] = Field(..., description="['rewrite', 'acceptance_criteria']")

class RevisionAuditRequest(BaseModel):
    konten_revisi: str = Field(..., description="Konten revisi manual")

class LintRequest(BaseModel):
    konten: str = Field(default="", description="Konten untuk inline linting")

class LintFinding(BaseModel):
    kategori_cacat: str
    severity: str
    potongan_teks_asli: str
    highlight_start: int
    highlight_end: int
    saran_perbaikan: str

class AcceptanceCriteriaItem(BaseModel):
    given: str
    when: str
    then: str

class AIRecommendation(BaseModel):
    ai_rewrite: str
    acceptance_criteria: List[AcceptanceCriteriaItem]
