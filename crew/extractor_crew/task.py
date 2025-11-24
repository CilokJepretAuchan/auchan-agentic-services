


from crewai import Task
from crew.extractor_crew.agent import context_agent,extractor_agent
from crew.extractor_crew.models import ExtractedDocumentOutput, ContextTaskModel

context_task = Task(
    description="""
        Analyze the structured JSON content_flow extracted by the preprocessing script.
        Determine the document type, its purpose, key themes, and important sections.
        always highlight transaction or financial reports

        extracted document : 
        {extracted_document}
    """,
    expected_output="""
        JSON:
        {
            "document_type": "...",
            "purpose": "...",
            "key_topics": ["...", "..."],
            "important_sections": ["...", "..."]
        }
    """,
    agent=context_agent,
    output_pydantic=ContextTaskModel
)

extraction_task = Task(
    description="""
Based on the structured JSON content_flow extracted by the preprocessing script,
extract financial transactions, evidence of payments, and total expenses from the document.
CRITICAL RULE: TABLE VALIDATION & FILTERING (READ THIS FIRST
You will encounter two types of tables. You must distinguish them:

1.  **TRANSACTION TABLES (Process these for 'Transaction List'):**
    * Usually contain headers like: "No", "Uraian" (Description), "Volume/Qty", "Harga Satuan" (Unit Price), "Jumlah".
    * Contains specific items (e.g., "Kerupuk", "Minyak Goreng", "Bensin", "Transport").
    * **ACTION:** Extract these rows into the transaction list.

2.  **SUMMARY/RECAP TABLES (IGNORE these for 'Transaction List'):**
    * Usually contain headers like: "Keterangan", "Jumlah" (Total only), without "Unit Price".
    * Contains aggregate descriptions like: "Total Penjualan", "Sisa Produk", "Total Pengeluaran", "Laba/Rugi".
    * **ACTION:** DO NOT add these rows to the transaction list. Only use them to find the 'Total Expense' value.

3. **ANOTHER TABLE THAT NOT HAVE RELATION ABOUT TRANSACTION**
   * Tables that do not have headers or content related to transactions or summaries.
    * **ACTION:** IGNORE these tables entirely.

FOR THE TRANSACTIONS LIST, EXTRACT THE FOLLOWING FIELDS:
1. **DESCRIPTIONS (Crucial):**
   - Combine [Section Context] - [Item Name] - [Type] - [Notes].
   - **NEGATIVE CONSTRAINT:** If the description contains words like "TOTAL PENJUALAN", "SISA PRODUK", "REKAPITULASI", or represents a summary of income/sales, **SKIP THIS ROW**.

2. **TYPE:**
   - Determine if 'INCOME' or 'EXPENSE'.

3. **CATEGORY:**
   - E.g., "food", "utilities", "raw materials".

4. **QTY (Quantities):**
   - Extract exactly as written (e.g., "4 KG", "1 Tabung").

5. **AMOUNT:**
   - The total price for that specific item row.

FOR EVIDENCE OF PAYMENTS:
- List detected images with titles indicating proof of payment/receipts.
- Format: "Filename [found in section: Context Section]".

FOR TOTAL EXPENSE:
- Look for the final sum of the costs.
- **TIP:** You usually find this value in the "SUMMARY/RECAP TABLES" that you ignored for the transaction list (e.g., look for row "Total Pengeluaran" or the largest sum at the bottom of the expense table).
- If multiple totals exist (e.g., Total Sales vs Total Expense), ensure you pick the EXPENSE total.

extracted document :
{extracted_document}
    """,
    expected_output="""
        JSON:
{
  "transactions": [
    {
      "amount": [total_amount_float],
      "type": [The transaction category, either 'INCOME' or 'EXPENSE', determined automatically based on the transaction name/description.]
      "category": [category_string],
      "description": [rich description string as per instructions],
      "qty": [quantity_int],
      },
    ...
    ],
        "evidence": [
            {
            "section": [section where the evidence image was found],
            "file_name": [image filename]
            },
            ...
        ],
        "totalExpense": [total_expense_float]
    }
    """,
    agent=extractor_agent,
    output_pydantic=ExtractedDocumentOutput,
)