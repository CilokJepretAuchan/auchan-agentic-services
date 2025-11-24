

from core.config import llm
from crewai import Agent


context_agent = Agent(
    role="Document Context Interpreter",
    goal=(
        "Understand the overall purpose, theme, and structure of the document based on "
        "the already extracted content_flow JSON. Provide high-level context that helps "
        "provide relevant context, especially regarding report information or financial transaction history."
        "downstream extraction."

    ),
    backstory=(
        "You are an expert in interpreting structured document extraction data. "
        "You understand reports, invoices, logs, letters, and administrative documents. "
        "You can infer document purpose and detect important sections without raw OCR."
    ),
    llm=llm,
    max_rpm=10
)


extractor_agent = Agent(
    role="Structured Document Data Extractor",
    goal=(
        "Extract meaningful values from the structured content_flow JSON, including "
        "tables, headings, lists, images, and intro text. Identify numbers, totals, "
        "transaction data, names, and relationships."
        "The extracted data must be real, not fictitious, and can be analyzed further for the purposes of detecting errors and anomalies such as excessive transactions, inappropriate nominal amounts, and other fraud in financial reports."
    ),
    backstory=(
        "You specialize in structured content analysis. Unlike OCR or full parsing, "
        "you focus on extracting key data fields such as totals, participant names, "
        "financial summaries, and contextual values from cleaned JSON structures."
    ),
    llm=llm,
    max_rpm=10
)
