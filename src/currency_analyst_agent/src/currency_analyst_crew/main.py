# src/currency_analyst_crew/main.py

import os
from currency_analyst_crew.crew import CurrencyAnalystCrew


# create output directory if it doesn't exist.
os.makedirs('output', exist_ok=True)


# define the run function to kickoff the crew.
def run(inputs: dict):
    """
    Run the currency analyst crew.
    """

    # create and run the crew.
    result = CurrencyAnalystCrew().crew().kickoff(inputs=inputs)

    # print the result.
    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("\n\nReport has been saved to output/report.md")

    return result.raw

if __name__ == "__main__":

    inputs = {
        "user_query": "what is the current exchange rate between USA currency and Germany currency? Also, provide insights on factors that might have influenced this rate recently."
        }
    
    
    run(inputs)