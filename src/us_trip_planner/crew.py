from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from us_trip_planner.tools.search_tool import SearchTool
from us_trip_planner.tools.calculator_tool import CalculatorTool
from us_trip_planner.tools.mapycz_tool import MapyCzTool
from tenacity import retry, stop_after_attempt, wait_exponential


@CrewBase
class UsTripPlanner():
    """UsTripPlanner crew for planning US West Coast trips"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def attraction_selection_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['attraction_selection_agent'],
            verbose=True,
            tools=[SearchTool()]
        )

    @agent
    def route_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['route_planner'],
            verbose=True,
            tools=[SearchTool(), MapyCzTool(), CalculatorTool()]
        )

    @task
    def identify_task(self) -> Task:
        return Task(
            description=self.tasks_config['identify_task']['description'],
            expected_output=self.tasks_config['identify_task']['expected_output'],
            agent=self.attraction_selection_agent(),
            output_file='attractions_report.md'
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    @task
    def plan_route_task(self) -> Task:
        return Task(
            description=self.tasks_config['plan_route_task']['description'],
            expected_output=self.tasks_config['plan_route_task']['expected_output'],
            agent=self.route_planner(),
            output_file='route_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the UsTripPlanner crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=[self.identify_task(), self.plan_route_task()],
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
