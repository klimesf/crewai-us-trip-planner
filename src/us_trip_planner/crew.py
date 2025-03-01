from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from us_trip_planner.tools.search_tool import SearchTool
from us_trip_planner.tools.calculator_tool import CalculatorTool
from us_trip_planner.tools.mapycz_tool import MapyCzTool
from us_trip_planner.tools.browser_tool import BrowserTool


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
            tools=[SearchTool(), BrowserTool()]
        )

    @agent
    def accommodation_scouting_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['accommodation_scouting_agent'],
            verbose=True,
            tools=[SearchTool(), BrowserTool()]
        )

    @agent
    def foodie_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['foodie_agent'],
            verbose=True,
            tools=[SearchTool(), BrowserTool(), CalculatorTool()]
        )

    @agent
    def rental_car_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['rental_car_agent'],
            verbose=True,
            tools=[SearchTool(), BrowserTool(), CalculatorTool()]
        )

    @agent
    def route_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['route_planner'],
            verbose=True,
            tools=[SearchTool(), MapyCzTool(), CalculatorTool(), BrowserTool()]
        )

    @task
    def identify_task(self) -> Task:
        return Task(
            description=self.tasks_config['identify_task']['description'],
            expected_output=self.tasks_config['identify_task']['expected_output'],
            agent=self.attraction_selection_agent(),
            output_file='attractions_report.md'
        )

    @task
    def accommodation_task(self) -> Task:
        return Task(
            description=self.tasks_config['accommodation_task']['description'],
            expected_output=self.tasks_config['accommodation_task']['expected_output'],
            agent=self.accommodation_scouting_agent(),
            output_file='accommodation_report.md'
        )

    @task
    def foodie_task(self) -> Task:
        return Task(
            description=self.tasks_config['foodie_task']['description'],
            expected_output=self.tasks_config['foodie_task']['expected_output'],
            agent=self.foodie_agent(),
            output_file='foodie_report.md'
        )

    @task
    def rental_car_task(self) -> Task:
        return Task(
            description=self.tasks_config['rental_car_task']['description'],
            expected_output=self.tasks_config['rental_car_task']['expected_output'],
            agent=self.rental_car_agent(),
            output_file='rental_car_report.md'
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
            tasks=[self.identify_task(), self.accommodation_task(),
                   self.foodie_task(), self.rental_car_task(), self.plan_route_task()],
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
