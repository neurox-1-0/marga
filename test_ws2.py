import asyncio
import websockets
import json

async def listen():
    uri = "ws://127.0.0.1:8000/ws/dashboard"
    try:
        async with websockets.connect(uri) as ws:
            print("Connected to WebSocket, waiting for messages...")
            while True:
                msg = await ws.recv()
                print(f"Received: {msg}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(listen())
