

from pydantic import BaseModel
from typing import Optional,List
from enum import Enum

class ContextTaskModel(BaseModel):
    document_type: str
    purpose: str
    key_topics: list[str]
    important_sections: list[str]


class EvidencePayment(BaseModel):
    section: Optional[str] = None
    file_name: Optional[str] = None

class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class ExtractedTransaction(BaseModel):
    amount: float = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    description: Optional[str] = None
    qty: Optional[int] = None


class ExtractedDocumentOutput(BaseModel):
    transactions: List[ExtractedTransaction]
    evidence: Optional[list[EvidencePayment]] = None
    totalExpense: Optional[float] = None