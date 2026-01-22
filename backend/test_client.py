import websockets
import asyncio
import json
import base64

async def send_image():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Read and encode image
        with open("test_image.jpg", "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Send to server
        await websocket.send(json.dumps({"image": img_base64}))
        
        # Receive result
        result = await websocket.recv()
        print(json.loads(result))

asyncio.run(send_image())