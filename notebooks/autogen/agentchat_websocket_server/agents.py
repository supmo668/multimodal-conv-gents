import json
from autogen import ConversableAgent, GroupChat, GroupChatManager
from autogen.agentchat.conversable_agent import Agent
from llm import llm_config, llm_config

class HandRaiseConversableAgent(ConversableAgent):
    def __init__(self, *args, websocket_uri=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.websocket_uri = websocket_uri  # WebSocket for monitoring
        self.hand_raise = False  # Initial state
        self.default_message = "skip"  # Default message

    async def monitor_hand_raise(self):
        """Monitor the WebSocket for hand-raise signals."""
        if not self.websocket_uri:
            return

        async with IOWebsockets.connect(self.websocket_uri) as ws:
            async for message in ws:
                if "[HUMANSIGNAL]raise-hand" in message:
                    print("Hand-raise signal received.")
                    self.hand_raise = True
                    iostream = IOStream.get_default()
                    if iostream:
                        iostream.output("[HUMANSIGNAL]raise-hand")
                elif "[HUMANSIGNAL]lower-hand" in message:
                    print("Lower-hand signal received.")
                    self.hand_raise = False

    def get_human_input(self, prompt: str) -> str:
        """Override to handle human input based on hand-raise signal."""
        if self.hand_raise:
            print("Hand-raise detected. Awaiting human input...")
            iostream = IOStream.get_default()
            reply = iostream.input(prompt)  # Non-blocking input from IOStream
            self._human_input.append(reply)
            return reply
        else:
            print(f"No hand-raise detected. Returning default message: '{self.default_message}'")
            return self.default_message

human_termination = lambda msg: "[HANDRAISE]" in msg["content"]

agent1 = ConversableAgent(
    "agent1",
    system_message="You are have an indefinite conversation for fun, you can talk about anything but you must always reply and add a question for following up.",
    llm_config=llm_config,
    is_termination_msg=human_termination,
    human_input_mode="NEVER",  # never ask for human input
)
agent2 = ConversableAgent(
    "agent2",
    system_message="You are have an indefinite conversation for fun, you can talk about anything but you must always reply and add a question for following up.",
    llm_config=llm_config,
    is_termination_msg=human_termination,
    human_input_mode="NEVER",  # never ask for human input
)

human_proxy = HandRaiseConversableAgent(
    "human_proxy",
    llm_config=False,  # no LLM used for human proxy
    human_input_mode="ALWAYS",  # always ask for human input
)
def custom_speaker_selection_func(last_speaker: Agent, groupchat: GroupChat):
    """Define a customized speaker selection function.
    A recommended way is to define a transition for each speaker in the groupchat.

    Returns:
        Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
    """
    messages = groupchat.messages
    if len(messages) <= 1:
        return agent1
    if len(messages) <= 2:
        return agent2
    
    if last_speaker is human_proxy:
        if messages[-2]["name"] == "agent1":
            # If it is the planning stage, let the planner to continue
            return agent2
        elif messages[-2]["name"] == "agent2":
            # If the last message is from the scientist, let the scientist to continue
            return agent1

    elif last_speaker in [agent1, agent2]:
        # Always let the user to speak after the agent
        return human_proxy
    
groupchat = GroupChat(
    agents=[human_proxy, agent1, agent2],
    messages=[],
    max_round=20,
    speaker_selection_method=custom_speaker_selection_func,
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)