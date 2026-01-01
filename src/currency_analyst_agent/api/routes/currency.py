# src/currency_analyst/api/routes/currency.py

from fastapi import APIRouter, HTTPException
from src.currency_analyst.api.schemas.currency_schema import (
    CurrencyAnalysisRequest,
    CurrencyAnalysisResponse,
)
from src.currency_analyst.api.services.agent_service import analyze_currency_service

from src.currency_analyst_crew.main import run


# define the router.
router = APIRouter(prefix="/currency", tags=["Currency Analysis"])

# define the analyze endpoint.
@router.post("/analyze", response_model=CurrencyAnalysisResponse)
async def analyze_currency(request: CurrencyAnalysisRequest):
    """
    Endpoint for analyzing and Providing accurate and insightful information 
    about current exchange rates and relationships between currencies in real 
    time using CrewAI logic.

    Accepts JSON input and returns an AI-generated insight.
    """


    try:
        result = await run(request)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
