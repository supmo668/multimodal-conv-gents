from fastapi import FastAPI
from autogen.io.websockets import IOWebsockets
from contextlib import asynccontextmanager
import uvicorn

from .on_connect import on_connect

# Define a FastAPI application and WebSocket server manager
@asynccontextmanager
async def run_websocket_server(app):
    with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8080) as uri:
        print(f"WebSocket server started at {uri}")
        yield

# Define FastAPI app to manage WebSocket server lifecycle
app = FastAPI(lifespan=run_websocket_server)

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)