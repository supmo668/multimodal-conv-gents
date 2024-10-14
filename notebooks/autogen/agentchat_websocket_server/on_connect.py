from datetime import datetime
from tempfile import TemporaryDirectory

from websockets.sync.client import connect as ws_connect

import autogen
from autogen.io.websockets import IOWebsockets

config_list = autogen.config_list_from_json(
    "conf/OAI_CONFIG_LIST.txt",
    filter_dict={
        # "model": ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
        "model": ["gpt-3.5-turbo"],
    },
)

llm_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}

llm_config_stream = {"stream": True, **llm_config}

def on_connect(iostream: IOWebsockets) -> None:
    print(f" - on_connect(): Connected to client using IOWebsockets {iostream}", flush=True)

    print(" - on_connect(): Receiving message from client.", flush=True)

    # 1. Receive Initial Message
    initial_msg = iostream.input()

    # 2. Instantiate ConversableAgent
    agent = autogen.ConversableAgent(
        name="chatbot",
        system_message="Complete a task given to you and reply TERMINATE when the task is done. If asked about the weather, use tool 'weather_forecast(city)' to get the weather forecast for a city.",
        llm_config=llm_config_stream
    )

    # 3. Define UserProxyAgent
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        system_message="A proxy for the user.",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config=False,
    )

    # 4. Define Agent-specific Functions
    def weather_forecast(city: str) -> str:
        return f"The weather forecast for {city} at {datetime.now()} is sunny."

    autogen.register_function(
        weather_forecast, caller=agent, executor=user_proxy, description="Weather forecast for a city"
    )

    # 5. Initiate conversation
    print(
        f" - on_connect(): Initiating chat with agent {agent} using message '{initial_msg}'",
        flush=True,
    )
    user_proxy.initiate_chat(  # noqa: F704
        agent, message=initial_msg,
    )