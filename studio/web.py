"""
FerrumOS FastAPI Web Gateway & Real-Time Dashboard (Modular Edition)
====================================================================
Modern async Web Control Center for FerrumOS IoT nodes:
- WebSocket live telemetry streaming (CPU %, Heap RAM, RSSI, VM steps)
- Live Hardware Reconciliation directly with ESP32-C6 REGISTRY in RAM
- Digital Twin (`storage/nodes/<node_id>/current/`) state management & snapshots
- Contextual Cross-Validator & Pin Matrix collision detection
- Interactive Pinout Grid & Shared Busses (I2C, SPI, UART, 1-Wire) Visualizer
- REST API for fleet management, code editor & zero-downtime hot-swap
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .web_server.models import (
    DeployRequest,
    ValidateRequest,
    ScriptSaveRequest,
    MqttTestRequest,
)
from .web_server.routes_nodes import (
    router as nodes_router,
    fleet,
    get_nodes,
    get_node_status,
    get_digital_twin,
    unload_node_task,
    list_node_snapshots,
    restore_node_snapshot,
    validate_script_with_node_context,
    validate_script,
    deploy_script_to_node,
    commit_node_flash,
    erase_node_flash,
)
from .web_server.routes_scripts import (
    router as scripts_router,
    list_scripts,
    read_script,
    save_script,
    delete_script,
)
from .web_server.routes_mqtt import (
    router as mqtt_router,
    test_mqtt_connection,
)
from .web_server.ws_telemetry import (
    router as telemetry_router,
    websocket_telemetry_stream,
)

BASE_DIR = Path(__file__).resolve().parent / "web_server"
DIST_DIR = BASE_DIR / "dist"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="FerrumOS Studio & Digital Twin",
    description="Control Center, Digital Twin & Real-Time Telemetry for FerrumOS IoT Nodes (Svelte 5 & Tailwind 4)",
    version="0.5.0"
)

# Mount Svelte 5 Dist Assets if present
if DIST_DIR.exists() and (DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")

# Mount Static Assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Register Modular API Routers
app.include_router(nodes_router)
app.include_router(scripts_router)
app.include_router(mqtt_router)
app.include_router(telemetry_router)


@app.get("/", response_class=HTMLResponse)
def index_page():
    dist_index = DIST_DIR / "index.html"
    if dist_index.exists():
        return HTMLResponse(content=dist_index.read_text(encoding="utf-8"))
    
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Index template not found")


if __name__ == "__main__":
    import uvicorn
    print("\n🛡️  Starting FerrumOS Studio & Digital Twin on http://127.0.0.1:8000 ...")
    uvicorn.run("tools.ferrum.web:app", host="0.0.0.0", port=8000, reload=True)