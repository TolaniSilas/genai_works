# src/currency_analyst_crew/tools/custom_tool.py

import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Type
from crewai.tools import BaseTool
from .tool_schema import CurrencyConverterInput
from .tool_schema import SupportedCurrenciesInput


load_dotenv()


# access the exchange rate api key using os.getenv()
exchange_rate_api_key = os.getenv("EXCHANGE_RATE_API_KEY")


class SupportedCurrenciesTool(BaseTool):
    """
    Tool for retrieving all supported currency codes and their corresponding
    countries from the Exchange Rate API. Exchange Rate API supports 166 currency codes. 

    This tool fetches the complete list of currency codes and corresponding currency name
    that the API can handle for real-time conversion. It is designed to provide
    reference context for the LLM, ensuring it only works with valid currencies
    when performing conversions or comparisons. This tool does not provide
    exchange rates or historical data.
    """
    name: str = "Supported Currencies Tool"
    description: str = (
        "Fetches all currency codes and their corresponding currency name supported "
        "by the Exchange Rate API. Useful for providing the LLM with valid currency "
        "context. Does not require any input and does not return exchange rates."
    )
    args_schema: Type[BaseModel] = SupportedCurrenciesInput
    api_key: str = exchange_rate_api_key


    def _run(self) -> str:

        # endpoint for retrieving all supported currency codes.
        url = f'https://v6.exchangerate-api.com/v6/{self.api_key}/codes'

        # send a get request to fetch the list of all supported currencies.
        response = requests.get(url)

        # check if the request was successful; return error message if not successful.
        if response.status_code != 200:
            return "Failed to fetch supported currency codes."

        # parse the json response from the api.
        data = response.json()
        
        # if the key "supported_codes" is missing, default to an empty list to avoid errors.
        supported_codes = data.get("supported_codes", [])

        # format each supported currency code and its corresponding currency name.    
        output_lines = [f"{code} - {country}" for code, country in supported_codes]

        # return a structured, human-readable summary.
        return "\n".join(output_lines)


class CurrencyConverterTool(BaseTool):
    """
    Tool for retrieving the real-time exchange rate between two supported
    currencies.

    This tool fetches the latest available exchange rate for a specified
    currency pair and returns the current rate. It is designed strictly
    for real-time currency rate lookup and does not support amount-based
    conversions, historical data, trend analysis, or future predictions.
    """
    name: str = "Currency Converter Tool"
    description: str = (
        "Retrieves the current real-time exchange rate between a specified "
        "base or source currency and a target currency. The tool returns only the "
        "latest exchange rate for the currency pair and does not perform "
        "amount-based conversions or provide historical or predictive data."
    )
    args_schema: Type[BaseModel] = CurrencyConverterInput
    api_key: str = exchange_rate_api_key


    def _run(self, from_currency: str, to_currency: str) -> str:

        # construct the api url for fetching the real-time exchange rate.
        url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/pair/{from_currency}/{to_currency}"

        # send a get request to the exchange rate api.
        response = requests.get(url)

        # check if the request was successful; return error message if not successful.
        if response.status_code != 200:
            return "Failed to fetch current exchange rates."

        # parse the json response from the api.
        data = response.json()

        # extract the conversion rate and the target currency code from the response.
        conversion_rate = data.get("conversion_rate")
        target_code = data.get("target_code")

        # validate that the response contains the expected data and matches the requested target currency.
        if conversion_rate is None or target_code != to_currency:
            return "Invalid currency code."

        # return a clear, user-friendly message showing the current exchange rate.
        return f"Current exchange rate: 1 {from_currency} = {conversion_rate} {to_currency}"
