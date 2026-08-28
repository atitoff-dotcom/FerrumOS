"""
Ferrum Realtime Protocol (FRP v1) Python Implementation
========================================================
High-performance binary communication with ESP32-C6 FerrumOS nodes.
Uses Python standard library struct for zero-overhead packing/unpacking.
"""

import socket
import struct
import time
from typing import Dict, Any, List, Optional

# Constants matching Rust firmware
FRP_MAGIC = b"FRP\x01"
RWP_MAGIC = FRP_MAGIC  # Backward compatibility

FRP_MSG_GET_STATUS = 0x01
FRP_MSG_STATUS_RESP = 0x02
FRP_MSG_UPLOAD_BYTECODE = 0x03
FRP_MSG_UPLOAD_RESP = 0x04
FRP_MSG_REBOOT = 0x05
FRP_MSG_LIST_TASKS = 0x06
FRP_MSG_LIST_RESP = 0x07
FRP_MSG_DELETE_TASK = 0x08
FRP_MSG_DELETE_RESP = 0x09
FRP_MSG_FLASH_COMMIT = 0x0A
FRP_MSG_FLASH_COMMIT_RESP = 0x0B
FRP_MSG_FLASH_ERASE = 0x0C
FRP_MSG_FLASH_ERASE_RESP = 0x0D

# Backward compatibility aliases
RWP_MSG_GET_STATUS = FRP_MSG_GET_STATUS
RWP_MSG_STATUS_RESP = FRP_MSG_STATUS_RESP
RWP_MSG_UPLOAD_BYTECODE = FRP_MSG_UPLOAD_BYTECODE
RWP_MSG_UPLOAD_RESP = FRP_MSG_UPLOAD_RESP
RWP_MSG_REBOOT = FRP_MSG_REBOOT
RWP_MSG_LIST_TASKS = FRP_MSG_LIST_TASKS
RWP_MSG_LIST_RESP = FRP_MSG_LIST_RESP
RWP_MSG_DELETE_TASK = FRP_MSG_DELETE_TASK
RWP_MSG_DELETE_RESP = FRP_MSG_DELETE_RESP
RWP_MSG_FLASH_COMMIT = FRP_MSG_FLASH_COMMIT
RWP_MSG_FLASH_COMMIT_RESP = FRP_MSG_FLASH_COMMIT_RESP
RWP_MSG_FLASH_ERASE = FRP_MSG_FLASH_ERASE
RWP_MSG_FLASH_ERASE_RESP = FRP_MSG_FLASH_ERASE_RESP

# Binary struct layout for FrpStatusResponse (52 bytes)
FRP_STATUS_FMT = "<4sBBBBBBBBbB2xIHHHHII16s"
FRP_STATUS_SIZE = struct.calcsize(FRP_STATUS_FMT)
RWP_STATUS_FMT = FRP_STATUS_FMT
RWP_STATUS_SIZE = FRP_STATUS_SIZE

# Binary struct layout for FrpUploadResponse (8 bytes)
FRP_UPLOAD_RESP_FMT = "<4sBBH"
FRP_UPLOAD_RESP_SIZE = struct.calcsize(FRP_UPLOAD_RESP_FMT)
RWP_UPLOAD_RESP_FMT = FRP_UPLOAD_RESP_FMT
RWP_UPLOAD_RESP_SIZE = FRP_UPLOAD_RESP_SIZE

# Binary struct layout for FrpFlashCommitResponse (7 bytes)
FRP_FLASH_COMMIT_RESP_FMT = "<4sBBB"
FRP_FLASH_COMMIT_RESP_SIZE = struct.calcsize(FRP_FLASH_COMMIT_RESP_FMT)
RWP_FLASH_COMMIT_RESP_FMT = FRP_FLASH_COMMIT_RESP_FMT
RWP_FLASH_COMMIT_RESP_SIZE = FRP_FLASH_COMMIT_RESP_SIZE


def calc_crc16(data: bytes) -> int:
    """Computes CRC16-CCITT (0x1021, init 0xFFFF) matching Rust ferrum-compiler."""
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def package_frb(bytecode: bytes) -> bytes:
    """Packages raw bytecode into a cross-platform .frb container."""
    crc = calc_crc16(bytecode)
    length = len(bytecode)
    header = b"FRB\x01" + struct.pack("<HH", crc, length)
    return header + bytecode


def package_rhb(bytecode: bytes) -> bytes:
    return package_frb(bytecode)


def unpackage_frb(pkg: bytes) -> bytes:
    """Unpackages a .frb or legacy .rhb container and verifies CRC16."""
    if len(pkg) < 8:
        raise ValueError("Package too short (< 8 bytes)")
    if pkg[:4] != b"FRB\x01" and pkg[:4] != b"RHB\x01":
        raise ValueError("Invalid Magic header in .frb container (expected FRB\\x01)")
    expected_crc, length = struct.unpack("<HH", pkg[4:8])
    if len(pkg) < 8 + length:
        raise ValueError(f"Truncated package: expected {length} bytes, got {len(pkg) - 8}")
    payload = pkg[8:8 + length]
    actual_crc = calc_crc16(payload)
    if expected_crc != actual_crc:
        raise ValueError(f"CRC16 checksum mismatch (expected 0x{expected_crc:04X}, calculated 0x{actual_crc:04X})")
    return payload


def unpackage_rhb(pkg: bytes) -> bytes:
    return unpackage_frb(pkg)


class FrpClient:
    """High-speed binary client for communicating with FerrumOS nodes."""

    @staticmethod
    def get_status(ip: str, port: int = 80, timeout: float = 3.0) -> Dict[str, Any]:
        """Queries 48-byte binary telemetry from a node."""
        t_start = time.perf_counter()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            # Send GET_STATUS frame: [FRP\x01] [0x01]
            sock.sendall(b"FRP\x01\x01")
            data = sock.recv(128)
            latency_ms = (time.perf_counter() - t_start) * 1000.0

        if len(data) < FRP_STATUS_SIZE:
            raise ConnectionError(f"Received invalid status response size: {len(data)} bytes (expected {FRP_STATUS_SIZE})")

        unpacked = struct.unpack(FRP_STATUS_FMT, data[:FRP_STATUS_SIZE])
        (
            magic, msg_type, v_maj, v_min, v_pat, cpu, l10, l1m, l5m, rssi, ch,
            uptime, free_kb, used_kb, b_size, errors, steps, reqs, script_raw
        ) = unpacked

        if (magic != FRP_MAGIC and magic != b"RWP\x01") or msg_type != FRP_MSG_STATUS_RESP:
            raise ValueError(f"Invalid magic or msg_type in response: {magic!r}, {msg_type}")

        script_id = script_raw.split(b"\x00")[0].decode("utf-8", errors="replace")
        if not script_id:
            script_id = "none"

        return {
            "system": {
                "device": "FerrumOS-ESP32C6",
                "version": f"{v_maj}.{v_min}.{v_pat}",
                "semver": (v_maj, v_min, v_pat),
                "uptime_sec": uptime,
                "cpu_usage_pct": cpu,
                "load_avg": [round(l10 / 100.0, 2), round(l1m / 100.0, 2), round(l5m / 100.0, 2)],
                "msg_requests": reqs
            },
            "memory": {
                "free_heap_kb": free_kb,
                "used_heap_kb": used_kb
            },
            "wifi": {
                "rssi_dbm": rssi,
                "channel": ch,
                "latency_ms": round(latency_ms, 2)
            },
            "vm": {
                "active_script": script_id,
                "bytecode_size": b_size,
                "instructions_executed": steps,
                "errors": errors
            }
        }

    @staticmethod
    def list_tasks(ip: str, port: int = 80, timeout: float = 2.0) -> List[Dict[str, Any]]:
        """Queries full list of all active tasks registered in the microcontroller's RAM."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.sendall(b"FRP\x01\x06")
            data = sock.recv(512)

        if len(data) < 6 or (data[:4] != b"FRP\x01" and data[:4] != b"RWP\x01") or data[4] != FRP_MSG_LIST_RESP:
            raise ValueError(f"Invalid LIST_RESP frame (len {len(data)})")

        task_count = data[5]
        offset = 6
        tasks = []
        status_map = {0: "Loaded", 1: "Running", 2: "WaitingDelay", 3: "Stopped", 4: "Failed", 5: "WaitingIpc", 6: "WaitingMqtt"}

        for _ in range(task_count):
            if offset + 40 > len(data):
                break
            id_len = data[offset]
            offset += 1
            id_bytes = data[offset:offset + 32]
            offset += 32
            task_id = id_bytes[:id_len].decode("utf-8", errors="replace")
            status_code = data[offset]
            offset += 1
            bytecode_size, = struct.unpack("<H", data[offset:offset + 2])
            offset += 2
            exec_count, = struct.unpack("<I", data[offset:offset + 4])
            offset += 4

            tasks.append({
                "id": task_id,
                "status": status_map.get(status_code, "Running"),
                "size": bytecode_size,
                "execution_count": exec_count,
                "verified": True
            })
        return tasks

    @staticmethod
    def delete_task(ip: str, task_id: str, port: int = 80, timeout: float = 2.0) -> bool:
        """Unloads a task from the microcontroller's RAM registry via binary FRP."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            id_raw = task_id.encode("utf-8")[:32]
            frame = b"FRP\x01\x08" + bytes([len(id_raw)]) + id_raw
            sock.sendall(frame)
            data = sock.recv(16)

        if len(data) >= 6 and (data[:4] == b"FRP\x01" or data[:4] == b"RWP\x01") and data[4] == FRP_MSG_DELETE_RESP:
            return data[5] == 0
        return False

    @staticmethod
    def reboot(ip: str, port: int = 80, timeout: float = 2.0) -> bool:
        """Sends a software reset command to the node via binary FRP."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((ip, port))
                frame = b"FRP\x01\x05"
                sock.sendall(frame)
                data = sock.recv(16)
            return len(data) >= 6 and (data[:4] == b"FRP\x01" or data[:4] == b"RWP\x01") and data[4] == 0x06 and data[5] == 0
        except Exception:
            return False

    @staticmethod
    def upload_bytecode(ip: str, frb_bytes: bytes, script_id: str = "main", port: int = 80, timeout: float = 3.0) -> Dict[str, Any]:
        """Uploads a .frb container to a node via binary FRP socket under a specific task ID."""
        id_bytes = script_id.encode("utf-8")
        if len(id_bytes) > 32:
            raise ValueError(f"Task ID '{script_id}' ({len(id_bytes)} bytes) exceeds maximum allowed length of 32 bytes.")
        if len(id_bytes) == 0:
            raise ValueError("Task ID cannot be empty.")

        t_start = time.perf_counter()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            id_raw = id_bytes[:32]
            frame = b"FRP\x01\x03" + bytes([len(id_raw)]) + id_raw + frb_bytes
            sock.sendall(frame)
            data = sock.recv(64)
            latency_ms = (time.perf_counter() - t_start) * 1000.0

        if len(data) < FRP_UPLOAD_RESP_SIZE:
            raise ConnectionError(f"Received invalid upload ACK size: {len(data)} bytes")

        magic, msg_type, status, loaded_bytes = struct.unpack(FRP_UPLOAD_RESP_FMT, data[:FRP_UPLOAD_RESP_SIZE])
        if (magic != FRP_MAGIC and magic != b"RWP\x01") or msg_type != FRP_MSG_UPLOAD_RESP:
            raise ValueError("Invalid ACK frame received")

        return {
            "status": "ok" if status == 0 else f"error_{status}",
            "loaded_bytes": loaded_bytes,
            "latency_ms": round(latency_ms, 2)
        }

    @staticmethod
    def commit_to_flash(ip: str, port: int = 80, timeout: float = 4.0) -> Dict[str, Any]:
        """Commits all currently running RAM tasks to non-volatile NOR Flash partition (0x300000)."""
        t_start = time.perf_counter()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.sendall(b"FRP\x01\x0A")
            data = sock.recv(16)
            latency_ms = (time.perf_counter() - t_start) * 1000.0

        if len(data) >= 7 and (data[:4] == b"FRP\x01" or data[:4] == b"RWP\x01") and data[4] == FRP_MSG_FLASH_COMMIT_RESP:
            magic, msg_type, status, saved_count = struct.unpack(FRP_FLASH_COMMIT_RESP_FMT, data[:7])
            return {
                "status": "ok" if status == 0 else "error",
                "saved_count": saved_count,
                "latency_ms": round(latency_ms, 2)
            }
        return {"status": "error", "saved_count": 0, "latency_ms": round(latency_ms, 2)}

    @staticmethod
    def erase_flash(ip: str, port: int = 80, timeout: float = 4.0) -> bool:
        """Erases the persistent Flash storage partition on the node."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.sendall(b"FRP\x01\x0C")
            data = sock.recv(16)

        if len(data) >= 6 and (data[:4] == b"FRP\x01" or data[:4] == b"RWP\x01") and data[4] == FRP_MSG_FLASH_ERASE_RESP:
            return data[5] == 0
        return False


# Backward compatibility alias
RwpClient = FrpClient

