from websockets.sync.client import connect as ws_connect

# Connect to the WebSocket server
with ws_connect("ws://localhost:8080/ws") as websocket:
    # Send a message to the server
    websocket.send("Hello WebSocket server")

    # Receive and print the response from the server
    while True:
        message = websocket.recv()
        print(f"Received message: {message}")
        if "TERMINATE" in message:
            break
