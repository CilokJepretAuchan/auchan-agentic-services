# crew/analyzer_crew/factory.py

from crewai import Crew
from crew.analyzer_crew.agent import (
    document_analysis_agent,
    section_classifier_agent,
    evidence_detector_agent,
)
from crew.analyzer_crew.task import (
    analyze_document_task,
    classify_sections_task,
    detect_evidence_task,
)

class AnalyzerCrewFactory:
    @staticmethod
    def create():
        """
        Create and return a Crew instance for document analysis.
        This crew runs 3 lightweight tasks: analysis -> section classification -> evidence detection.
        """

        crew = Crew(
            agents=[
                document_analysis_agent,
                section_classifier_agent,
                evidence_detector_agent,
            ],
            tasks=[
                analyze_document_task,
                classify_sections_task,
                detect_evidence_task,
            ],
            verbose=True  # set False for production
        )

        return crew
