import krpc
import asyncio
from typing import Dict, Any

class KRPCBridge:
    def __init__(self, host: str = "192.168.1.X"):  # KSP machine LAN IP
        self.host = host
        self.conn = None
        self.vessels = {}

    def connect(self):
        self.conn = krpc.connect(
            name="KSP Dashboard",
            address=self.host,
            rpc_port=50000,
            stream_port=50001
        )
        self.space_center = self.conn.space_center

    def get_vessel_data(self) -> Dict[str, Any]:
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
