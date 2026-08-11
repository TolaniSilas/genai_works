from pydantic import BaseModel, Field, field_validator

class CurrencyAnalysisRequest(BaseModel):
    """Schema for user request to analyze currencies."""

    query: str = Field(
        ...,
        examples=[
            "what is the current exchange rate between USA currency and Germany currency?",
            "what's the current exchange rate between USD and MXN?"
            ],
        description="User's natural language query or question.",
        min_length=1
    )

    @field_validator('query')
    @classmethod
    def validate_query(cls, v:str) -> str:
        cleaned_query = v.strip()

        if not cleaned_query:
            raise ValueError("Query must not be empty or whitespace only.")

        return cleaned_query



class CurrencyAnalysisResponse(BaseModel):
    """Schema for the AI analysis response."""

    response: str