import json
import subprocess
import datetime
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from .protocol import FrpClient, RwpClient, package_frb, package_rhb
from .validator import PreFlightValidator
from .storage import DigitalTwinManager


class FleetManager:
    def __init__(self, inventory_path: str = "tools/fleet.json", storage_path: str = "storage/nodes"):
        self.inventory_path = Path(inventory_path)
        self.twin = DigitalTwinManager(base_storage_path=storage_path)
        self.nodes: Dict[str, Any] = {}
        self.load_inventory()

    def load_inventory(self):
        if not self.inventory_path.exists():
            default_inventory = {
                "nodes": {
                    "c6_supermini_main": {
                        "ip": "192.168.1.243",
                        "port": 80,
                        "board": "esp32c6_supermini",
                        "description": "ESP32-C6 SuperMini Main Development Board"
                    }
                }
            }
            self.inventory_path.parent.mkdir(parents=True, exist_ok=True)
            self.inventory_path.write_text(json.dumps(default_inventory, indent=2, ensure_ascii=False), encoding="utf-8")
            self.nodes = default_inventory["nodes"]
        else:
            try:
                data = json.loads(self.inventory_path.read_text(encoding="utf-8"))
                self.nodes = data.get("nodes", {})
            except Exception:
                self.nodes = {}

        # Ensure all nodes exist in Digital Twin storage
        for node_id, node in self.nodes.items():
            self.twin.init_node(
                node_id,
                board=node.get("board", "esp32c6_supermini"),
                ip=node.get("ip", "127.0.0.1"),
                port=node.get("port", 80),
                description=node.get("description", "")
            )

    def save_inventory(self):
        self.inventory_path.parent.mkdir(parents=True, exist_ok=True)
        self.inventory_path.write_text(
            json.dumps({"nodes": self.nodes}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def add_node(self, node_id: str, ip: str, port: int = 80, board: str = "esp32c6_supermini", description: str = ""):
        self.nodes[node_id] = {
            "ip": ip,
            "port": port,
            "board": board,
            "description": description or f"FerrumOS Node at {ip}:{port}"
        }
        self.save_inventory()
        self.twin.init_node(node_id, board, ip, port, description)

    def deploy(self, node_id_or_ip: str, script_path: str, task_id: Optional[str] = None, force: bool = False, persist: bool = True) -> bool:
        """Deploys a JS or .frb script to a node with Pre-Flight validation, hot-swap, and Flash persistence."""
        path = Path(script_path)
        if not path.exists():
            print(f"❌ [ERROR] Script file '{script_path}' not found!")
            return False

        # Resolve node IP, port, and board target
        if node_id_or_ip in self.nodes:
            node_id = node_id_or_ip
            node = self.nodes[node_id]
            ip = node["ip"]
            port = node.get("port", 80)
            board = node.get("board", "esp32c6_supermini")
        else:
            node_id = "standalone"
            ip = node_id_or_ip
            port = 80
            board = "esp32c6_supermini"
            self.twin.init_node(node_id, board, ip, port)

        resolved_task_id = task_id or path.stem
        if len(resolved_task_id.encode("utf-8")) > 32:
            print(f"❌ [VALIDATION ERROR] Task ID '{resolved_task_id}' ({len(resolved_task_id.encode('utf-8'))} bytes) exceeds maximum allowed length of 32 bytes.")
            return False

        raw_data = path.read_bytes()

        # If already .frb or .rhb container, deploy directly
        if raw_data.startswith(b"FRB\x01") or raw_data.startswith(b"RHB\x01"):
            frb_pkg = raw_data
            script_code = f"// Raw FRB Binary ({len(frb_pkg)} bytes)"
            resources = {"pins": {}, "busses": {}}
        else:
            script_code = raw_data.decode("utf-8", errors="replace")

            # 1. Run Contextual Pre-Flight Cross-Validation with `current/`
            validator = PreFlightValidator(target_board=board)
            current_manifest = self.twin.get_current_manifest(node_id)
            is_valid, errors, resources = validator.validate_with_context(script_code, resolved_task_id, current_manifest)

            print(f"🔍 [PRE-FLIGHT] Cross-validating task '{resolved_task_id}' for '{node_id}' ({board})...")
            for err in errors:
                icon = "❌" if err.level == "ERROR" else "⚠️"
                print(f"   {icon} {err}")

            if not is_valid and not force:
                print("⛔ [ABORTED] Hardware or Cross-Script validation failed. Fix errors or use --force.")
                return False

            # 2. Compile JS to .frb via Pure Python Compiler (Zero Cargo dependency)
            print(f"🔨 [COMPILING] Compiling '{resolved_task_id}' with native Python compiler...")
            try:
                from .compiler import compile_js_to_frb
                frb_pkg = compile_js_to_frb(script_code)
            except Exception as e:
                print(f"❌ [COMPILER ERROR] Failed to compile JS script: {e}")
                return False

        # 3. Upload over FRP Binary Socket
        print(f"🚀 [FRP DEPLOY] Uploading task '{resolved_task_id}' ({len(frb_pkg)} bytes) to {ip}:{port} (Zero-Downtime Hot-Swap)...")
        try:
            resp = FrpClient.upload_bytecode(ip, frb_pkg, script_id=resolved_task_id, port=port)
            if resp.get("status") == "ok":
                # 4. Save to Digital Twin `current/` and take snapshot
                self.twin.save_task(node_id, resolved_task_id, script_code, frb_pkg, resources)

                # 5. Commit to Flash memory for Auto-Boot on power-up
                if persist:
                    try:
                        time.sleep(0.1)
                        flash_resp = FrpClient.commit_to_flash(ip, port=port)
                        if flash_resp.get("status") == "ok":
                            print(f"  💾 Flash Persistence: Saved {flash_resp.get('saved_count')} task(s) to NOR Flash (Auto-Boot enabled)")
                    except Exception as e:
                        print(f"  ⚠️ [FLASH] Warning committing to flash: {e}")

                print("========================================================")
                print(f"  ✨ FerrumOS Task '{resolved_task_id}' Hot-Swap SUCCESS! 🚀")
                print(f"  Device ACK   : Loaded {resp.get('loaded_bytes')} bytes into RAM")
                print(f"  Transfer Time: {resp.get('latency_ms')} ms")
                print(f"  Digital Twin : Updated 'storage/nodes/{node_id}/current/'")
                print("========================================================")
                return True
            else:
                print(f"❌ [DEPLOY ERROR] Device returned status: {resp}")
                return False
        except Exception as e:
            print(f"❌ [CONNECTION ERROR] Failed to deploy to {ip}:{port}: {e}")
            return False

    def unload_task(self, node_id: str, task_id: str, persist: bool = True) -> bool:
        """Unloads a task from Digital Twin mirror and device via binary FRP."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            ip = node["ip"]
            port = node.get("port", 80)
            
            # 1. Unload from live microcontroller via binary FRP
            try:
                FrpClient.delete_task(ip, task_id, port=port)
                if persist:
                    time.sleep(0.1)
                    FrpClient.commit_to_flash(ip, port=port)
            except Exception as e:
                print(f"⚠️ [FRP] Warning unloading from hardware {ip}:{port}: {e}")

            # 2. Fallback to HTTP DELETE if older firmware
            try:
                import urllib.request
                req = urllib.request.Request(
                    f"http://{ip}:{port}/api/scripts/{task_id}",
                    method="DELETE"
                )
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    pass
            except Exception:
                pass

        # Update Digital Twin mirror
        return self.twin.remove_task(node_id, task_id)
