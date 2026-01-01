# src/currency_analyst/api/schemas/currency_schema.py

from pydantic import BaseModel, Field

class CurrencyAnalysisRequest(BaseModel):
    """Schema for user request to analyze currencies."""

    query: str = Field(
        ...,
        example=["what is the current exchange rate between USA currency and Germany currency?", "what's the current exchange rate between USA currency and Mexico currency?"],
        description="User's natural language query or question."
    )


class CurrencyAnalysisResponse(BaseModel):
    """Schema for the AI analysis response."""

    response: str
