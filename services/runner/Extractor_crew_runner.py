# crew/extractor_crew/runner.py

from crew.extractor_crew.extractor_crew_factory import ExtractorCrewFactory
from crew.extractor_crew.models import ExtractedDocumentOutput

class ExtractorCrewRunner:
    @staticmethod
    def run_extraction(parsed_document: dict) -> ExtractedDocumentOutput:
        """
        Run the Extractor Crew with the given parsed document.

        Parameters
        ----------
        parsed_document : dict
            The JSON result from your DOCX parsing script.

        Returns
        -------
        dict :
            {
                "context_result": ...,
                "extraction_result": ...
            }
        """

        # Load Crew
        crew = ExtractorCrewFactory.create()

        # Run Crew
        results = crew.kickoff(
            inputs={"extracted_document": parsed_document}
        )

        return results.pydantic
