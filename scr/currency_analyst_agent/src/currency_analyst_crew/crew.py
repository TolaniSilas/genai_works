# src/currency_analyst_crew/crew.py

from typing import List
from crewai import BaseAgent, Agent, Task, Crew, Process, agent, task, crew
from crewai.tools.serper import SerperDevTool  # optional web search tool

@CrewBase
class CurrencyAnalystCrew():
    """Currency Analyst Crew for real-time exchange rate analysis and insights"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def currency_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['currency_analyst'],  # type: ignore[index]
            verbose=True,
            tools=[
                # Core conversion tool; you would wrap your API call here
                # e.g., PairConversionTool(),
                
                # Optional: real-time context for insights
                SerperDevTool()  
            ]
        )

    @task
    def real_time_currency_task(self) -> Task:
        return Task(
            config=self.tasks_config['real_time_currency_task'],  # type: ignore[index]
            markdown=True,
            output_file='output/report.md'
        )

    @task
    def supported_currencies_task(self) -> Task:
        return Task(
            config=self.tasks_config['supported_currencies_task'],  # type: ignore[index]
            markdown=True,
            output_file='output/supported_currencies.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Currency Analyst crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
