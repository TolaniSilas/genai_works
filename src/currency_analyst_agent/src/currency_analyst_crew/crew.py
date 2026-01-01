# src/currency_analyst_crew/crew.py

from typing import List
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from currency_analyst_crew.tools.custom_tool import SupportedCurrenciesTool, CurrencyConverterTool


supported_currencies_tool = SupportedCurrenciesTool()

currency_converter_tool = CurrencyConverterTool()


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
            memory=True,
            tools=[
                supported_currencies_tool, 
                currency_converter_tool
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
            # markdown=True,
            # output_file='output/supported_currencies.md'
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

