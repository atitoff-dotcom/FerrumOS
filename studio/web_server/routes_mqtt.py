import time
from typing import Optional
from fastapi import APIRouter, HTTPException
from ..fleet import FleetManager
from .models import MqttTestRequest

router = APIRouter(tags=["mqtt"])
fleet = FleetManager()

@router.post("/api/nodes/{node_id}/mqtt/test")
def test_mqtt_connection(node_id: str, req: Optional[MqttTestRequest] = None):
    host = req.host if req and req.host else "192.168.1.114"
    port = req.port if req and req.port else 1883
    user = req.username if req and req.username else "alex"
    pwd = req.password if req and req.password else "bh0020"

    try:
        import paho.mqtt.client as paho_mqtt
        t0 = time.perf_counter()
        client = paho_mqtt.Client(paho_mqtt.CallbackAPIVersion.VERSION2, client_id="ferrum_web_test_probe")
        if user:
            client.username_pw_set(user, pwd)
        client.connect(host, port, keepalive=5)
        client.loop_start()
        time.sleep(0.08)
        client.loop_stop()
        client.disconnect()
        dt_ms = round((time.perf_counter() - t0) * 1000, 1)
        return {
            "ok": True,
            "broker": f"{host}:{port}",
            "latency_ms": dt_ms,
            "message": f"Successfully connected to MQTT Broker ({dt_ms} ms)"
        }
    except Exception as e:
        return {
            "ok": False,
            "broker": f"{host}:{port}",
            "error": str(e),
            "message": f"MQTT Connection failed: {e}"
        }
