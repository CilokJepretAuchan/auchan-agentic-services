


from crewai import Task
from crew.analyzer_crew.agent import (
    document_analysis_agent,
    section_classifier_agent,
    evidence_detector_agent,
)
from crew.analyzer_crew.models import DocumentAnalysisOutputModel,SectionClassificationOutputModel,EvidenceDetectionOutputModel

analyze_document_task = Task(
    description="""
        Perform a quick high-level analysis of the document to understand its purpose,
        topic, and main content. Identify the key themes without going into deep detail.
        path docx : {path}
    """,
    expected_output="""
        JSON:
        {
            "document_purpose": "...",
            "main_topics": ["...", "..."],
            "short_summary": "2–3 sentence summary"
        }
    """,
    agent=document_analysis_agent,
    output_pydantic=DocumentAnalysisOutputModel
)

classify_sections_task = Task(
    description="""
        Identify and label the main sections of the document (e.g., header, body,
        tables, appendix). Keep it simple and only detect major segments.
    """,
    expected_output="""
        JSON:
        {
            "sections": [
                { "id": 1, "label": "header" },
                { "id": 2, "label": "content" },
                { "id": 3, "label": "table" }
            ]
        }
    """,
    agent=section_classifier_agent,
    output_pydantic=SectionClassificationOutputModel
)

detect_evidence_task = Task(
    description="""
        Quickly detect whether the document contains any financial or transactional
        evidence such as receipts or invoices.
    """,
    expected_output="""
        JSON:
        {
            "has_evidence": true/false,
            "evidence_type": "receipt | invoice | none"
        }
    """,
    agent=evidence_detector_agent,
    output_pydantic=EvidenceDetectionOutputModel
)
