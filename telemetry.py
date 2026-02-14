import krpc
from typing import Dict, Any
from config import KSP_HOST, KSP_RPC_PORT, KSP_STREAM_PORT


class KRPCBridge:
    def __init__(self, host: str = KSP_HOST):
        self.host = host
        self.rpc_port = KSP_RPC_PORT
        self.stream_port = KSP_STREAM_PORT
        self.conn = None
        self.space_center = None
        self.connected = False

    def connect(self):
        if self.conn is None:
            try:
                self.conn = krpc.connect(
                    name="KSP Dashboard",
                    address=self.host,
                    rpc_port=self.rpc_port,
                    stream_port=self.stream_port
                )
                self.space_center = self.conn.space_center
                self.connected = True
                print(f"Connected to KRPC at {self.host}:{self.rpc_port}")
            except Exception as e:
                print(f"Failed to connect to KRPC: {e}")
                self.connected = False
                raise

    def ensure_connected(self):
        if not self.connected:
            self.connect()

    def get_vessel_data(self) -> Dict[str, Any]:
        try:
            self.ensure_connected()
            data = {}
            for vessel in self.space_center.vessels:
                flight = vessel.flight()
                data[vessel.name] = {
                    "type": vessel.type,
                    "altitude": flight.mean_altitude,
                    "speed": flight.speed,
                    "fuel": {
                        "liquid_fuel": vessel.resources.amount("LiquidFuel"),
                        "oxidizer": vessel.resources.amount("Oxidizer"),
                    },
                    "orbit": {
                        "apoapsis": vessel.orbit.apoapsis_altitude,
                        "periapsis": vessel.orbit.periapsis_altitude,
                    } if vessel.orbit is not None else None,
                }
            return data
        except Exception as e:
            self.connected = False
            raise
