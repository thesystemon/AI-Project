from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Any, Dict

class ScanRequest(BaseModel):
    target: HttpUrl
    run_zap: bool = False
    nuclei_args: List[str] = Field(default_factory=list)

class Finding(BaseModel):
    source: str
    severity: str
    name: str
    description: Optional[str] = None
    matched_at: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    references: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class RawScanResult(BaseModel):
    target: str
    nuclei: List[Dict[str, Any]] = Field(default_factory=list)
    zap: Dict[str, Any] = Field(default_factory=dict)

class TriageResult(BaseModel):
    findings: List[Finding]
    summary_md: str

class ScanResponse(BaseModel):
    scan_id: str
    raw: RawScanResult
    triage: TriageResult

class ReportRequest(BaseModel):
    scan_id: str
