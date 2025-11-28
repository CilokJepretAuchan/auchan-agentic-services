# crew/extractor_crew/runner.py

from crew.report_builder_crew.report_builder_crew import ReportBuilderCrewFactory
from crew.report_builder_crew.models import MonthlyReport

class BuildReportCrewRunner:
    @staticmethod
    def run_extraction(aggregated_data: dict) -> MonthlyReport:
        """
        Run the Report Builder Crew with the given parsed document.

        Parameters
        ----------
        parsed_document : dict
            The Aggregated data from database.

        """

        # Load Crew
        crew = ReportBuilderCrewFactory.create()

        # Run Crew
        results = crew.kickoff(
            inputs={"aggregated_data": aggregated_data}
        )

        return results.pydantic
