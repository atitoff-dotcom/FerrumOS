"""
FerrumOS Digital Twin & Node Storage Manager
============================================
Manages persistent state, active running task mirrors, device passports,
live hardware reconciliation via binary FRP protocol directly with ESP32-C6,
and versioned snapshots under `storage/nodes/<node_id>/`.
"""

import json
import shutil
import datetime
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional

from .protocol import FrpClient


class DigitalTwinManager:
    """Manages the server-side digital twin and live hardware synchronization for FerrumOS nodes."""

    def __init__(self, base_storage_path: str = "storage/nodes"):
        self.base_path = Path(base_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_node_dir(self, node_id: str) -> Path:
        node_dir = self.base_path / node_id
        node_dir.mkdir(parents=True, exist_ok=True)
        return node_dir

    def init_node(self, node_id: str, board: str = "esp32c6_supermini", ip: str = "127.0.0.1", port: int = 80, description: str = "") -> Dict[str, Any]:
        """Initializes storage structure for a node if not already present."""
        node_dir = self.get_node_dir(node_id)
        current_dir = node_dir / "current"
        snapshots_dir = node_dir / "snapshots"
        current_dir.mkdir(parents=True, exist_ok=True)
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        device_file = node_dir / "device.json"
        if not device_file.exists():
            passport = {
                "node_id": node_id,
                "board": board,
                "ip": ip,
                "port": port,
                "description": description or f"FerrumOS Node ({board})",
                "arch": "riscv32imac",
                "flash_size_mb": 4,
                "ram_kb": 512,
                "heap_kb": 110,
                "max_tasks": 8,
                "created_at": datetime.datetime.now().isoformat()
            }
            device_file.write_text(json.dumps(passport, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            passport = json.loads(device_file.read_text(encoding="utf-8"))

        manifest_file = current_dir / "state.json"
        if not manifest_file.exists():
            manifest = {
                "node_id": node_id,
                "updated_at": datetime.datetime.now().isoformat(),
                "active_tasks": {},
                "claimed_pins": {},
                "shared_busses": {
                    "i2c": [],
                    "spi": [],
                    "uart": [],
                    "onewire": []
                }
            }
            manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        return passport

    def get_device_info(self, node_id: str) -> Dict[str, Any]:
        device_file = self.get_node_dir(node_id) / "device.json"
        if device_file.exists():
            try:
                return json.loads(device_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return self.init_node(node_id)

    def get_current_manifest(self, node_id: str) -> Dict[str, Any]:
        self.init_node(node_id)
        manifest_file = self.get_node_dir(node_id) / "current" / "state.json"
        if manifest_file.exists():
            try:
                return json.loads(manifest_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"node_id": node_id, "active_tasks": {}, "claimed_pins": {}, "shared_busses": {}}

    def _save_manifest(self, node_id: str, manifest: Dict[str, Any]):
        manifest_file = self.get_node_dir(node_id) / "current" / "state.json"
        manifest["updated_at"] = datetime.datetime.now().isoformat()
        manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    def fetch_live_tasks_from_chip(self, ip: str, port: int = 80, timeout: float = 2.0) -> Optional[List[Dict[str, Any]]]:
        """
        Queries the live microcontroller hardware via binary RWP task list (RWP_MSG_LIST_TASKS 0x06).
        """
        try:
            tasks = RwpClient.list_tasks(ip, port=port, timeout=timeout)
            if isinstance(tasks, list):
                return [t for t in tasks if t.get("id") and t.get("id").strip() and t.get("id") != "none"]
        except Exception:
            pass

        return None

    def reconcile_with_hardware(self, node_id: str, ip: str, port: int = 80) -> Dict[str, Any]:
        """
        Synchronizes Digital Twin mirror with live tasks running in the ESP32-C6 microcontroller's RAM.
        """
        manifest = self.get_current_manifest(node_id)
        live_scripts = self.fetch_live_tasks_from_chip(ip, port)

        if live_scripts is not None:
            current_tasks = manifest.get("active_tasks", {})
            updated_tasks = {}

            from .validator import PreFlightValidator
            validator = PreFlightValidator()

            for s in live_scripts:
                task_id = s.get("id", "").strip()
                if not task_id or task_id == "none":
                    continue
                existing = current_tasks.get(task_id, {})

                # Check if we have source code locally in current/ or scripts/
                current_js = self.get_node_dir(node_id) / "current" / f"{task_id}.js"
                repo_js = Path("scripts") / f"{task_id}.js"

                if current_js.exists():
                    code = current_js.read_text(encoding="utf-8")
                    res = validator.extract_resources(code)
                    pins_map, busses_map = res["pins"], res["busses"]
                elif repo_js.exists():
                    code = repo_js.read_text(encoding="utf-8")
                    res = validator.extract_resources(code)
                    pins_map, busses_map = res["pins"], res["busses"]
                else:
                    pins_map = existing.get("pins", {})
                    busses_map = existing.get("busses", {})

                frb_sz = s.get("size", 0)
                if frb_sz == 0:
                    frb_file = self.get_node_dir(node_id) / "current" / f"{task_id}.frb"
                    rhb_file = self.get_node_dir(node_id) / "current" / f"{task_id}.rhb"
                    if frb_file.exists():
                        frb_sz = len(frb_file.read_bytes())
                    elif rhb_file.exists():
                        frb_sz = len(rhb_file.read_bytes())
                    elif existing.get("frb_size") or existing.get("rhb_size"):
                        frb_sz = existing.get("frb_size", existing.get("rhb_size"))

                updated_tasks[task_id] = {
                    "task_id": task_id,
                    "status": s.get("status", "Running"),
                    "execution_count": s.get("execution_count", 0),
                    "frb_size": frb_sz,
                    "deployed_at": existing.get("deployed_at", datetime.datetime.now().isoformat()),
                    "live": True,
                    "verified": s.get("verified", True),
                    "pins": pins_map,
                    "busses": busses_map
                }

            manifest["active_tasks"] = updated_tasks
            self._rebuild_allocations(manifest)
            self._save_manifest(node_id, manifest)

        return manifest

    def save_task(self, node_id: str, task_id: str, js_code: str, frb_bytes: bytes, resource_claims: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves a deployed task to the node's `current/` mirror,
        recalculates resource allocations, and creates an automatic snapshot.
        """
        self.init_node(node_id)
        current_dir = self.get_node_dir(node_id) / "current"

        # 1. Save source JS and compiled .frb binary
        js_file = current_dir / f"{task_id}.js"
        frb_file = current_dir / f"{task_id}.frb"

        js_file.write_text(js_code, encoding="utf-8")
        frb_file.write_bytes(frb_bytes)

        # 2. Update Manifest
        manifest = self.get_current_manifest(node_id)
        active_tasks = manifest.setdefault("active_tasks", {})

        active_tasks[task_id] = {
            "task_id": task_id,
            "status": "Running",
            "execution_count": 0,
            "js_size": len(js_code.encode("utf-8")),
            "frb_size": len(frb_bytes),
            "deployed_at": datetime.datetime.now().isoformat(),
            "live": True,
            "verified": True,
            "persisted": True,
            "storage": "flash",
            "pins": resource_claims.get("pins", {}),
            "busses": resource_claims.get("busses", {})
        }

        # 3. Rebuild global pin & bus allocation maps
        self._rebuild_allocations(manifest)
        self._save_manifest(node_id, manifest)

        # 4. Auto snapshot
        self.create_snapshot(node_id, label=f"deploy_{task_id}")
        return active_tasks[task_id]

    def remove_task(self, node_id: str, task_id: str) -> bool:
        """Removes a task from `current/` mirror and updates allocations."""
        self.init_node(node_id)
        current_dir = self.get_node_dir(node_id) / "current"

        js_file = current_dir / f"{task_id}.js"
        frb_file = current_dir / f"{task_id}.frb"
        rhb_file = current_dir / f"{task_id}.rhb"
        js_file.unlink(missing_ok=True)
        frb_file.unlink(missing_ok=True)
        rhb_file.unlink(missing_ok=True)

        manifest = self.get_current_manifest(node_id)
        active_tasks = manifest.get("active_tasks", {})
        if task_id in active_tasks:
            del active_tasks[task_id]
            self._rebuild_allocations(manifest)
            self._save_manifest(node_id, manifest)
            self.create_snapshot(node_id, label=f"remove_{task_id}")
            return True
        return False

    def _rebuild_allocations(self, manifest: Dict[str, Any]):
        """Recalculates claimed pins and shared busses from all active tasks."""
        claimed_pins = {}
        i2c_busses = []
        spi_busses = []
        uart_busses = []
        ow_busses = []

        for task_id, task_meta in manifest.get("active_tasks", {}).items():
            for pin_str, tag in task_meta.get("pins", {}).items():
                claimed_pins[int(pin_str)] = {
                    "task_id": task_id,
                    "tag": tag,
                    "pin": int(pin_str)
                }

            busses = task_meta.get("busses", {})
            for i2c in busses.get("i2c", []):
                i2c_busses.append({**i2c, "task_id": task_id})
            for spi in busses.get("spi", []):
                spi_busses.append({**spi, "task_id": task_id})
            for uart in busses.get("uart", []):
                uart_busses.append({**uart, "task_id": task_id})
            for ow in busses.get("onewire", []):
                ow_busses.append({**ow, "task_id": task_id})

        manifest["claimed_pins"] = claimed_pins
        manifest["shared_busses"] = {
            "i2c": i2c_busses,
            "spi": spi_busses,
            "uart": uart_busses,
            "onewire": ow_busses
        }

    def get_resource_map(self, node_id: str, board_profile: Dict[str, Any], ip: Optional[str] = None, port: int = 80) -> Dict[str, Any]:
        """
        Generates full resource map for GUI visualization, querying live microcontroller hardware if IP provided.
        """
        if ip:
            manifest = self.reconcile_with_hardware(node_id, ip, port)
        else:
            manifest = self.get_current_manifest(node_id)

        device = self.get_device_info(node_id)

        valid_gpios = board_profile.get("valid_gpios", set(range(0, 24)))
        forbidden_gpios = board_profile.get("forbidden_gpios", {24, 25, 26, 27, 28, 29, 30})
        strapping_gpios = board_profile.get("strapping_gpios", {8, 9, 15})

        pin_matrix = []
        claimed = manifest.get("claimed_pins", {})

        # Merge bus pins for shared marking
        bus_pins = {}
        for i2c in manifest.get("shared_busses", {}).get("i2c", []):
            bus_pins[i2c.get("sda")] = f"I2C_SDA ({i2c.get('alias', 'default')})"
            bus_pins[i2c.get("scl")] = f"I2C_SCL ({i2c.get('alias', 'default')})"

        for pin in range(0, 31):
            if pin in forbidden_gpios:
                status = "forbidden"
                owner = "Flash / Internal SPI"
            elif pin not in valid_gpios:
                status = "invalid"
                owner = "N/A"
            elif str(pin) in claimed or pin in claimed:
                claim_info = claimed.get(str(pin)) or claimed.get(pin)
                status = "claimed"
                owner = f"{claim_info['task_id']} ({claim_info['tag']})"
            elif pin in bus_pins:
                status = "bus"
                owner = bus_pins[pin]
            else:
                status = "free"
                owner = "Available"

            is_strapping = pin in strapping_gpios
            pin_matrix.append({
                "pin": pin,
                "status": status,
                "owner": owner,
                "is_strapping": is_strapping
            })

        return {
            "node_id": node_id,
            "device": device,
            "pin_matrix": pin_matrix,
            "active_tasks": manifest.get("active_tasks", {}),
            "shared_busses": manifest.get("shared_busses", {}),
            "total_tasks": len(manifest.get("active_tasks", {})),
            "max_tasks": device.get("max_tasks", 8)
        }

    def create_snapshot(self, node_id: str, label: str = "manual") -> str:
        """Creates a timestamped full snapshot of `current/`."""
        node_dir = self.get_node_dir(node_id)
        current_dir = node_dir / "current"
        snapshots_dir = node_dir / "snapshots"

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"snapshot_{ts}_{label}"
        target_dir = snapshots_dir / snapshot_name

        if current_dir.exists():
            shutil.copytree(current_dir, target_dir, dirs_exist_ok=True)
            meta = {
                "snapshot_id": snapshot_name,
                "node_id": node_id,
                "label": label,
                "created_at": datetime.datetime.now().isoformat(),
            }
            (target_dir / "snapshot_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return snapshot_name

    def list_snapshots(self, node_id: str) -> List[Dict[str, Any]]:
        """Lists all snapshots available for a node."""
        snapshots_dir = self.get_node_dir(node_id) / "snapshots"
        if not snapshots_dir.exists():
            return []

        results = []
        for s_dir in sorted(snapshots_dir.glob("snapshot_*"), reverse=True):
            if s_dir.is_dir():
                meta_file = s_dir / "snapshot_meta.json"
                if meta_file.exists():
                    try:
                        results.append(json.loads(meta_file.read_text(encoding="utf-8")))
                        continue
                    except Exception:
                        pass
                results.append({
                    "snapshot_id": s_dir.name,
                    "node_id": node_id,
                    "created_at": s_dir.stat().st_ctime
                })
        return results

    def restore_snapshot(self, node_id: str, snapshot_id: str) -> bool:
        """Restores a snapshot to `current/`."""
        node_dir = self.get_node_dir(node_id)
        snapshot_dir = node_dir / "snapshots" / snapshot_id
        if not snapshot_dir.exists():
            return False

        current_dir = node_dir / "current"
        self.create_snapshot(node_id, label="before_restore")

        for item in snapshot_dir.iterdir():
            if item.name == "snapshot_meta.json":
                continue
            if item.is_file():
                shutil.copy2(item, current_dir / item.name)

        return True
