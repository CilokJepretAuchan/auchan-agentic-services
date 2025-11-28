from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class CategoryStat(BaseModel):
    name: str = Field(..., description="Category name, e.g., food, utilities")
    amount: float = Field(..., description="Total amount spent in this category")
    percentage: float = Field(..., description="Percentage of total spending")


class ProjectStat(BaseModel):
    id: UUID = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    budget: float = Field(..., description="Budget allocated to the project")
    spent_this_month: float = Field(..., description="Spending for the given month")
    status: str = Field(..., description="Status: Safe / Warning / Critical")


class MonthlyReport(BaseModel):
    org_name: str = Field(..., description="Organization or user name")
    period: str = Field(..., description="Month-year period, e.g., 11-2025")
    total_spent: float = Field(..., description="Total spending in the month")
    
    top_categories: List[CategoryStat] = Field(
        ..., description="List of spending categories with stats"
    )

    projects: List[ProjectStat] = Field(
        ..., description="List of projects and their financial status"
    )
    
    # Optional fields that you can generate automatically later
    summary_text: Optional[str] = Field(
        None, description="AI-generated summary for use in PDF"
    )
    optimization_suggestions: Optional[List[str]] = Field(
        None, description="AI-generated suggestions"
    )
    risk_flags: Optional[List[str]] = Field(
        None, description="Detected risks for projects or categories"
    )
