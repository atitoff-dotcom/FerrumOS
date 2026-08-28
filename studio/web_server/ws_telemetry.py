import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..fleet import FleetManager
from ..protocol import FrpClient, RwpClient

router = APIRouter(tags=["telemetry"])
fleet = FleetManager()

@router.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            fleet.load_inventory()
            nodes_data = {}

            for node_id, node in fleet.nodes.items():
                ip = node.get("ip")
                frp_port = node.get("frp_port", 4242)
                rwp_port = node.get("port", 80)

                try:
                    telemetry_raw = FrpClient.get_telemetry(ip, port=frp_port, timeout=0.8)
                    if telemetry_raw:
                        nodes_data[node_id] = {
                            "online": True,
                            "ip": ip,
                            "board": node.get("board", "esp32c6_supermini"),
                            "description": node.get("description", ""),
                            "telemetry": telemetry_raw
                        }
                        continue
                except Exception:
                    pass

                try:
                    status = RwpClient.get_status(ip, port=rwp_port, timeout=1.0)
                    nodes_data[node_id] = {
                        "online": True,
                        "ip": ip,
                        "board": node.get("board", "esp32c6_supermini"),
                        "description": node.get("description", ""),
                        "telemetry": status
                    }
                except Exception as e:
                    nodes_data[node_id] = {
                        "online": False,
                        "ip": ip,
                        "board": node.get("board", "esp32c6_supermini"),
                        "error": str(e)
                    }

            await websocket.send_text(json.dumps(nodes_data))
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        pass
