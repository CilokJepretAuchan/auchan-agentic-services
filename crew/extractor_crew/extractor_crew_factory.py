# crew/analyzer_crew/factory.py

from crewai import Crew
from crew.extractor_crew.agent import (
    context_agent,
    extractor_agent,
)
from crew.extractor_crew.task import (
    context_task,
    extraction_task,
)

class ExtractorCrewFactory:
    @staticmethod
    def create():
        """
        Create and return a Crew instance for document extractor.
        """

        crew = Crew(
            agents=[
                context_agent,
                extractor_agent,
            ],
            tasks=[
                context_task,
                extraction_task,
            ],
            verbose=True  # set False for production
        )

        return crew
