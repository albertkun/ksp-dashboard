from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from telemetry import KRPCBridge

import math
from typing import Any

def sanitize_floats(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: sanitize_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_floats(x) for x in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    return obj

app = FastAPI(title="KSP Dashboard")


# Initialize the bridge (reads config)
bridge = KRPCBridge()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten this later
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "KSP Dashboard is running"}


@app.get("/api/vessels")
async def get_vessels():
    try:
        raw_data = bridge.get_vessel_data()  # your KRPC telemetry
        safe_data = sanitize_floats(raw_data)
        return safe_data
    except Exception as e:
        return {"error": str(e)}



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
        except Exception as e:
            await websocket.send_json({"error": str(e)})
            break
