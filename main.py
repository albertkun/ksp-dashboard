from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from telemetry import KRPCBridge


app = FastAPI(title="KSP Dashboard")


# Initialize the bridge (reads config)
bridge = KRPCBridge()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten this later
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/vessels")
async def get_vessels():
    try:
        return bridge.get_vessel_data()
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
