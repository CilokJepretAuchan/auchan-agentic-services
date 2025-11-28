# crew/analyzer_crew/factory.py

from crewai import Crew
from crew.report_builder_crew.agent import (
    financial_analysis
)
from crew.report_builder_crew.task import (
    report_build_task
)

class ReportBuilderCrewFactory:
    @staticmethod
    def create():
        """
        Create and return a Crew instance for document analysis.
        This crew runs 3 lightweight tasks: analysis -> section classification -> evidence detection.
        """

        crew = Crew(
            agents=[
                financial_analysis
            ],
            tasks=[
                report_build_task
            ],
            verbose=True  # set False for production
        )

        return crew
