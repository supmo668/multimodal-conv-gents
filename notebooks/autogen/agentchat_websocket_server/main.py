from autogen.io.websockets import IOWebsockets
from contextlib import asynccontextmanager  # noqa: E402
from pathlib import Path  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.responses import HTMLResponse  # noqa: E402
import uvicorn

from on_connect import on_connect

html_path = Path(__file__).parent / "chat.html"
from autogen.io.websockets import IOWebsockets
from contextlib import asynccontextmanager

@asynccontextmanager
async def run_websocket_server(app):
    try:
        # Start the WebSocket server
        with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8080) as uri:
            print(f"WebSocket server started at {uri}.", flush=True)
            yield  # Ensure this yield is reached

    except Exception as e:
        print(f"WebSocket server failed: {str(e)}", flush=True)
        # Handle any cleanup if necessary

# Define FastAPI app to manage WebSocket server lifecycle
app = FastAPI(lifespan=run_websocket_server)

@app.get("/")
async def get():
    html_file = Path(html_path)
    html_content = html_file.read_text()
    return HTMLResponse(content=html_content, media_type="text/html")


import asyncio

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()  # Use await to run the server asynchronously

if __name__ == "__main__":
    # Run the FastAPI server
    asyncio.run(main())