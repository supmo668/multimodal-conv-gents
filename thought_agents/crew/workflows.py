from dotenv import load_dotenv
load_dotenv()

from functools import wraps

from .helper import agent, task, Agent, Task, WorkflowBase


@WorkflowBase
class LabProtocolScientist:
    """Laboratory Protocol Workflow Manager"""

    def __init__(self):
        pass

    @agent
    def protocol_reviewer(self) -> Agent:
        """Scientific protocol reviewer agent"""
        return Agent(
            name="protocol_reviewer",
            config=self.agents_config["scientific_protocol_reviewer"],
            tools=[
                ProtocolAnalysisTools.analyze_protocol,
                ProtocolAnalysisTools.validate_protocol,
                ProtocolAnalysisTools.identify_gaps
            ],
            verbose=True
        )

    @agent
    def protocol_executer(self) -> Agent:
        """Scientific protocol executer agent"""
        return Agent(
            name="protocol_executer",
            config=self.agents_config["scientific_protocol_executer"],
            tools=[
                ProtocolExecutionTools.create_action_steps,
                ProtocolExecutionTools.validate_execution,
                ProtocolExecutionTools.monitor_progress
            ],
            verbose=True
        )

    @agent
    def lab_supervisor(self) -> Agent:
        """Laboratory supervisor agent"""
        return Agent(
            name="lab_supervisor",
            config=self.agents_config["laboratory_supervisor"],
            tools=[
                ProtocolTools.safety_check,
                ProtocolTools.quality_control,
                ProtocolTools.resource_management
            ],
            verbose=True
        )

    @task
    def protocol_analysis(self) -> Task:
        """Protocol analysis task"""
        return Task(
            name="protocol_analysis",
            config=self.tasks_config["protocol_interpreter"],
            agent=self.protocol_reviewer(),
            output_file="protocol_analysis.json"
        )

    @task
    def protocol_execution(self) -> Task:
        """Protocol execution task"""
        return Task(
            name="protocol_execution",
            config=self.tasks_config["protocol_execution"],
            agent=self.protocol_executer(),
            output_file="protocol_execution.json"
        )

    @task
    def protocol_supervision(self) -> Task:
        """Protocol supervision task"""
        return Task(
            name="protocol_supervision",
            config=self.tasks_config["protocol_supervision"],
            agent=self.lab_supervisor(),
            output_file="protocol_supervision.json"
        )
        
# Example usage:
# workflow = LabProtocolScientist()
# result = workflow.run("protocol_analysis", inputs={"protocol": "Sample protocol steps..."})