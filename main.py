from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from telemetry import KRPCBridge

app = FastAPI(title="KSP Dashboard")

bridge = KRPCBridge(host="192.168.1.X")  # KSP machine LAN IP
bridge.connect()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/vessels")
async def get_vessels():
    return bridge.get_vessel_data()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = bridge.get_vessel_data()
            await websocket.send_json(data)
            await asyncio.sleep(0.5)  # ~2 Hz
        except WebSocketDisconnect:
            break
