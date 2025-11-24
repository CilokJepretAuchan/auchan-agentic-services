#TASK

from openai import BaseModel


class DocumentAnalysisOutputModel (BaseModel):
    document_purpose: str
    main_topics: list[str]
    short_summary: str


class SectionClassificationOutputModel (BaseModel):
    sections: list[dict[str, str | int]]

class EvidenceDetectionOutputModel (BaseModel):
    has_evidence: bool
    evidence_type: str

class AnalyzerCrewModels:
    DocumentAnalysisOutputModel = DocumentAnalysisOutputModel
    SectionClassificationOutputModel = SectionClassificationOutputModel
    EvidenceDetectionOutputModel = EvidenceDetectionOutputModel