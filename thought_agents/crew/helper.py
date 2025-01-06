from dotenv import load_dotenv
load_dotenv()

from typing import Any, List, Callable, Dict, Optional
from functools import wraps
import autogen  # Assuming autogen is available
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import yaml
from pathlib import Path

# Example tools
class SerperDevTool:
    pass

class VisionTool:
    pass

########################################
# Agent and Task Classes
########################################
        
class Agent:
    """Base class for workflow agents"""
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        tools: Optional[List[Callable]] = None,
        verbose: bool = True,
        **kwargs
    ):
        self.name = name
        self.config = config
        self.tools = tools or []
        self.verbose = verbose
        self.kwargs = kwargs
        self._instance = None

    def __call__(self) -> AssistantAgent:
        """Create and return an AssistantAgent instance"""
        if self._instance is None:
            self._instance = AssistantAgent(
                name=self.name,
                system_message=self._create_system_message(),
                tools=self.tools,
                verbose=self.verbose,
                **self.kwargs
            )
        return self._instance

    @property
    def agent(self) -> AssistantAgent:
        return self.__call__()

    def _create_system_message(self) -> str:
        """Create system message from agent config"""
        return (
            f"Role: {self.config['role']}\n"
            f"Goal: {self.config['goal']}"
        )


class Task:
    """Base class for workflow tasks"""
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        agent: Agent,
        output_file: Optional[str] = None,
        context: Optional[List['Task']] = None,
    ):
        self.name = name
        self.config = config
        self.agent = agent
        self.output_file = output_file
        self.context = context or []

    def __call__(self) -> Dict[str, Any]:
        """Return task configuration"""
        return {
            "name": self.name,
            "config": self.config,
            "agent": self.agent(),
            "output_file": self.output_file,
            "context": [ctx() for ctx in self.context],
        }

    def get_description(self) -> str:
        """Get task description"""
        return (
            f"Task: {self.name}\n"
            f"Description: {self.config.get('description', '')}\n"
            f"Expected Output: {self.config.get('expected_output', '')}"
        )

########################################
# Decorators to mark agents and tasks
########################################

_global_workflow_counter = 0

def agent(func):
    """Decorator to mark a method as an agent definition."""
    global _global_workflow_counter
    func.__workflow_decorator_type__ = "agent"
    func.__workflow_decorator_order__ = _global_workflow_counter
    _global_workflow_counter += 1
    return func

def task(func):
    """Decorator to mark a method as a task definition."""
    global _global_workflow_counter
    func.__workflow_decorator_type__ = "task"
    func.__workflow_decorator_order__ = _global_workflow_counter
    _global_workflow_counter += 1
    return func

########################################
# WorkflowBase as a Class Decorator
########################################

class BaseWorkflowMixin:
    """
    Mixin class that provides base workflow functionalities.
    """

    def __init__(
        self,
        llm_config: Optional[Dict[str, Any]] = None,
        state_transition_function: Optional[Callable] = None,
        max_rounds: int = 20,
        verbose: bool = True,
    ):
        self.llm_config = llm_config or {
            "config_list": [{"model": "gpt-4"}],
            "temperature": 0.7
        }
        self.state_transition_function = state_transition_function
        self.max_rounds = max_rounds
        self.verbose = verbose

        # Retrieve agents_config and tasks_config from class attributes
        self.agents_config = getattr(self.__class__, 'agents_config', {})
        self.tasks_config = getattr(self.__class__, 'tasks_config', {})

        # Add llm_config to each agent's config
        for agent_config in self.agents_config.values():
            agent_config['llm_config'] = self.llm_config

    @property
    def agents(self):
        """Returns all defined agents in the workflow."""
        return list(self._agents.values())

    @property
    def tasks(self):
        """Returns all defined tasks in the workflow."""
        return list(self._tasks.values())

    def get_default_state_transition(self):
        """Creates a default state transition function based on agent order"""
        agents_list = self.agents_in_order
        
        def default_transition(last_speaker, groupchat):
            if not last_speaker:  # Initial state
                return agents_list[0].agent
            
            for i, current_agent in enumerate(agents_list):
                if last_speaker == current_agent.agent:
                    # If there's a next agent, transition to it
                    if i < len(agents_list) - 1:
                        return agents_list[i + 1].agent
                    # If this is the last agent, end the workflow
                    return None
            
            return None  # Default case
        
        return default_transition

    def kickoff(self, message: str):
        """Starts the workflow."""
        # Use default state transition if none provided
        if not self.state_transition_function:
            self.state_transition_function = self.get_default_state_transition()

        groupchat = autogen.GroupChat(
            agents=[agent.agent for agent in self.agents],
            messages=[],
            max_round=self.max_rounds,
            speaker_selection_method=self.state_transition_function,
        )

        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=self.llm_config
        )

        if self.verbose:
            print("Starting the workflow...")
        
        # Start with initial message if provided
        first_agent = self.agents_in_order[0].agent
        if message:
            first_agent.initiate_chat(manager, message=message)
        else:
            manager.run()


def WorkflowBase(cls):
    """
    Class decorator that transforms a user-defined class into a workflow-capable class.
    It inspects @agent and @task decorated methods, and registers them.
    """

    # Extract agent and task methods
    agent_methods = []
    task_methods = []

    for name, method in cls.__dict__.items():
        if callable(method) and hasattr(method, '__workflow_decorator_type__'):
            dtype = method.__workflow_decorator_type__
            order = method.__workflow_decorator_order__
            if dtype == 'agent':
                agent_methods.append((order, name, method))
            elif dtype == 'task':
                task_methods.append((order, name, method))

    # Sort by order of definition
    agent_methods.sort(key=lambda x: x[0])
    task_methods.sort(key=lambda x: x[0])

    class WrappedWorkflow(BaseWorkflowMixin, cls):

        def __init__(self, *args, **kwargs):
            BaseWorkflowMixin.__init__(self, *args, **kwargs)
            self.config_dir = Path(__file__).parent
            self._load_configs()
            super().__init__()

            self._agents = {}
            self._tasks = {}

            # Instantiate agents
            for _, name, method in agent_methods:
                agent_instance = method(self)
                if not isinstance(agent_instance, Agent):
                    raise TypeError(f"Agent '{name}' must return an Agent instance.")
                self._agents[name] = agent_instance

            # Instantiate tasks
            for _, name, method in task_methods:
                task_instance = method(self)
                if not isinstance(task_instance, Task):
                    raise TypeError(f"Task '{name}' must return a Task instance.")
                self._tasks[name] = task_instance

        def _load_configs(self):
            """Load configuration files"""
            with open(self.config_dir / 'config/agents.yaml') as f:
                self.agents_config: dict = yaml.safe_load(f)
            with open(self.config_dir / 'config/tasks.yaml') as f:
                self.tasks_config: dict = yaml.safe_load(f)

        def define_groupchat(self, user_proxy, workflow_agents):
            """Define the group chat with the specified agents"""
            groupchat = autogen.GroupChat(
                agents=workflow_agents,
                messages=[],
                max_round=50
            )
            manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": self.agents_config})
            return manager, groupchat

        def run(self, workflow_name: str, inputs: Dict[str, Any], max_round: int = 10) -> List[Dict[str, str]]:
            """Run a workflow with the specified agents and tasks"""
            user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=max_round
            )

            # Get agents for the workflow
            workflow_agents = list(self._agents.values())
            workflow_agents.append(user_proxy)

            # Create group chat and manager
            manager, groupchat = self.define_groupchat(user_proxy, workflow_agents)

            # Initialize the chat with the first task
            initial_message = self._tasks.get(workflow_name, "")
            if not initial_message:
                raise ValueError(f"Task {workflow_name} not found")

            # Run the chat
            chat_result = manager.run(
                inputs,
                sender=user_proxy,
                messages=initial_message
            )
            return chat_result

        @property
        def agents_in_order(self):
            return [self._agents[name] for _, name, _ in agent_methods]

        @property
        def tasks_in_order(self):
            return [self._tasks[name] for _, name, _ in task_methods]

    WrappedWorkflow.__name__ = cls.__name__
    WrappedWorkflow.__doc__ = cls.__doc__
    return WrappedWorkflow

if __name__ == "__main__":
    ########################################
    # Example Usage
    ########################################

    @WorkflowBase
    class LabActionProtocolInterpreter:
        """LabActionProtocolInterpreter crew"""
        agents_config = {
            "protocol_interpreter": {
                "role": "interpreter", 
                "goal": "Interpret protocols"
            },
            "protocol_workflow_engineer": {
                "role": "engineer", 
                "goal": "Refine workflow"
            }
        }

        tasks_config = {
            "visual_analysis_task": {
                "description": "Analyze visual data"
            },
            "lab_action_report_task": {
                "description": "Report lab actions"
            }
        }

        @agent
        def protocol_interpreter(self) -> Agent:
            return Agent(
                name="ProtocolInterpreter",
                config=self.agents_config['protocol_interpreter'],
                verbose=True
            )

        @agent
        def workflow_engineer(self) -> Agent:
            return Agent(
                name="WorkflowEngineer",
                config=self.agents_config['protocol_workflow_engineer'],
                verbose=True
            )

        @task
        def interpretation_task(self) -> Task:
            return Task(
                name="InterpretationTask",
                config=self.tasks_config['visual_analysis_task'],
                agent=self.protocol_interpreter()
            )

        @task
        def reporting_task(self) -> Task:
            return Task(
                name="ReportingTask",
                config=self.tasks_config['lab_action_report_task'],
                context=[self.interpretation_task()],
                agent=self.workflow_engineer(),
                output_file='report.md'
            )


    # Initialize workflow with custom llm_config
    workflow = LabActionProtocolInterpreter(
        llm_config={
            "config_list": [{"model": "gpt-4"}],
            "temperature": 0.7
        },
        max_rounds=10,
        verbose=True
    )
    
    # Start the workflow with an initial message
    workflow.kickoff("Analyze the protocol for DNA extraction")
