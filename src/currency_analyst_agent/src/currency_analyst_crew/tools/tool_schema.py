from pydantic import BaseModel, Field

class SupportedCurrenciesInput(BaseModel):
    """Input schema for SupportedCurrenciesTool. No inputs required."""
    pass  # no user input needed for this tool.


class CurrencyConverterInput(BaseModel):
    """"Input schema for CurrencyConverterTool."""
    from_currency: str = Field(..., description="The base or source currency code (e.g., USD, NGN) to convert from.")
    to_currency: str = Field(..., description="The target currency code (e.g., EUR) to convert to.")