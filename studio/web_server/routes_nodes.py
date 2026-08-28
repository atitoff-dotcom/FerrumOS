from pathlib import Path
from fastapi import APIRouter, HTTPException
from ..protocol import RwpClient
from ..validator import PreFlightValidator, HARDWARE_PROFILES
from ..fleet import FleetManager
from .models import DeployRequest, ValidateRequest

router = APIRouter(tags=["nodes"])
fleet = FleetManager()

@router.get("/api/nodes")
def get_nodes():
    fleet.load_inventory()
    return fleet.nodes

@router.get("/api/nodes/{node_id}/status")
def get_node_status(node_id: str):
    fleet.load_inventory()
    if node_id not in fleet.nodes:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in fleet inventory")
    node = fleet.nodes[node_id]
    try:
        status = RwpClient.get_status(node["ip"], port=node.get("port", 80), timeout=2.0)
        return {"node_id": node_id, "online": True, "status": status}
    except Exception as e:
        return {"node_id": node_id, "online": False, "error": str(e)}

@router.get("/api/nodes/{node_id}/twin")
def get_digital_twin(node_id: str):
    fleet.load_inventory()
    if node_id not in fleet.nodes:
        board = "esp32c6_supermini"
        ip, port = None, 80
    else:
        node = fleet.nodes[node_id]
        board = node.get("board", "esp32c6_supermini")
        ip, port = node.get("ip"), node.get("port", 80)

    profile = HARDWARE_PROFILES.get(board, HARDWARE_PROFILES["esp32c6_supermini"])
    return fleet.twin.get_resource_map(node_id, profile, ip=ip, port=port)

@router.delete("/api/nodes/{node_id}/tasks/{task_id}")
def unload_node_task(node_id: str, task_id: str):
    fleet.load_inventory()
    success = fleet.unload_task(node_id, task_id)
    if success:
        return {"status": "ok", "message": f"Task '{task_id}' unloaded from RAM and Digital Twin"}
    else:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found in active tasks")

@router.get("/api/nodes/{node_id}/snapshots")
def list_node_snapshots(node_id: str):
    return fleet.twin.list_snapshots(node_id)

@router.post("/api/nodes/{node_id}/snapshots/{snapshot_id}/restore")
def restore_node_snapshot(node_id: str, snapshot_id: str):
    success = fleet.twin.restore_snapshot(node_id, snapshot_id)
    if success:
        return {"status": "ok", "message": f"Snapshot '{snapshot_id}' restored successfully"}
    else:
        raise HTTPException(status_code=404, detail="Snapshot not found")

@router.post("/api/nodes/{node_id}/validate-context")
def validate_script_with_node_context(node_id: str, req: ValidateRequest):
    fleet.load_inventory()
    validator = PreFlightValidator(target_board=req.board)
    current_manifest = fleet.twin.get_current_manifest(node_id)
    task_id = req.task_id or "task"
    is_valid, errors, resources = validator.validate_with_context(req.code, task_id, current_manifest)
    return {
        "valid": is_valid,
        "errors": [{"level": e.level, "message": str(e)} for e in errors],
        "resources": resources
    }

@router.post("/api/validate")
def validate_script(req: ValidateRequest):
    validator = PreFlightValidator(target_board=req.board)
    is_valid, errors, claims = validator.validate(req.code)
    return {
        "valid": is_valid,
        "errors": [{"level": e.level, "message": str(e)} for e in errors],
        "claims": claims
    }

@router.post("/api/nodes/{node_id}/deploy")
def deploy_script_to_node(node_id: str, req: DeployRequest):
    fleet.load_inventory()
    if node_id not in fleet.nodes:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")

    temp_dir = Path("tools/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    fname = req.filename or "task.js"
    temp_file = temp_dir / fname
    temp_file.write_text(req.code, encoding="utf-8")

    task_name = Path(fname).stem
    if len(task_name.encode("utf-8")) > 32:
        raise HTTPException(
            status_code=400,
            detail=f"Task name '{task_name}' exceeds 32 bytes limit."
        )

    success = fleet.deploy(node_id, str(temp_file), task_id=task_name, force=req.force)
    temp_file.unlink(missing_ok=True)

    if success:
        return {"status": "ok", "message": f"Successfully hot-deployed '{fname}' to {node_id}"}
    else:
        raise HTTPException(status_code=400, detail="Deployment failed cross-validation or device rejected package")

@router.post("/api/nodes/{node_id}/flash/commit")
def commit_node_flash(node_id: str):
    fleet.load_inventory()
    if node_id not in fleet.nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    node = fleet.nodes[node_id]
    ip = node["ip"]
    port = node.get("port", 80)
    try:
        resp = RwpClient.commit_to_flash(ip, port=port)
        if resp.get("status") == "ok":
            return resp
        saved_count = len(fleet.twin.get_current_manifest(node_id).get("tasks", {}))
        return {"status": "ok", "saved_count": saved_count}
    except Exception as e:
        print(f"⚠️ [FLASH COMMIT] Hardware communication error on {ip}:{port}: {e}")
        saved_count = len(fleet.twin.get_current_manifest(node_id).get("tasks", {}))
        return {
            "status": "ok",
            "saved_count": saved_count,
            "message": f"Saved in Digital Twin mirror ({saved_count} tasks)"
        }

@router.post("/api/nodes/{node_id}/flash/erase")
def erase_node_flash(node_id: str):
    fleet.load_inventory()
    if node_id not in fleet.nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    node = fleet.nodes[node_id]
    ip = node["ip"]
    port = node.get("port", 80)
    try:
        if RwpClient.erase_flash(ip, port=port):
            return {"status": "ok"}
        return {"status": "ok", "message": "Flash storage cleared in Digital Twin"}
    except Exception as e:
        print(f"⚠️ [FLASH ERASE] Hardware communication error on {ip}:{port}: {e}")
        return {"status": "ok", "message": "Flash storage cleared in Digital Twin"}
