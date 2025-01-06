from datetime import datetime
from tempfile import TemporaryDirectory

from websockets.sync.client import connect as ws_connect
from autogen.io.websockets import IOWebsockets, IOStream

from agents import agent1, manager


def on_connect(iostream: IOWebsockets) -> None:
    print(f" - on_connect(): Connected to client using IOWebsockets {iostream}", flush=True)

    try:
        
        import asyncio
        asyncio.create_task(human_proxy.monitor_hand_raise())
            
        # 1. Receive Initial Message
        initial_msg = "talk about anything you want"
        # initial_msg = iostream.input()  # Blocking until a message is received
        # if initial_msg:
        #     print(f"Received message from client: {initial_msg}", flush=True)

        with IOStream.set_default(iostream):
            # 2. Initiate the chat with the agent
            print(f"Initiating chat with agent using message '{initial_msg}'", flush=True)
            # This is where your chat initiation logic happens
            agent1.initiate_chat(
                manager, 
                message=initial_msg,
                clear_history=False  # Set clear_history based on your business logic
            )
        
        # 3. After the chat initiation, close the connection
        # print("Closing WebSocket connection after chat initiation.", flush=True)
        # IOStream.get_default().close()  # Close the IOStream connection

    except Exception as e:
        # Handle any exceptions and ensure the connection is closed in case of failure
        print(f"Error during WebSocket communication: {str(e)}", flush=True)
        # iostream.close()  # Close the IOStream connection
