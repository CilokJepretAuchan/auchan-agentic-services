# crew/analyzer_crew/runner.py

from crew.analyzer_crew.analyzer_crew_factory import AnalyzerCrewFactory
from typing import Dict, Any

class AnalyzerRunner:
    def __init__(self):
        self.crew = AnalyzerCrewFactory.create()

    def run(self, document_path: str) -> Dict[str, Any]:
        """
        Run the analyzer crew and merge all task outputs (Pydantic parsed outputs).
        """

        # Run crew
        result = self.crew.run({"document": document_path})

        # Collect outputs (in task order)
        merged_output = {
            "analysis": None,
            "sections": None,
            "evidence": None
        }

        for task_result in result.tasks_output:
            task_name = task_result.get("task_name")
            pydantic_model = task_result.get("pydantic")

            if not pydantic_model:
                continue

            # Map based on task_name
            if "analyze_document" in task_name:
                merged_output["analysis"] = pydantic_model

            elif "classify_sections" in task_name:
                merged_output["sections"] = pydantic_model

            elif "detect_evidence" in task_name:
                merged_output["evidence"] = pydantic_model

        return merged_output
