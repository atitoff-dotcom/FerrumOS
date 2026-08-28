"""
FerrumOS Pre-Flight Hardware, Driver & Cross-Script Context Validator
===================================================================
Static analysis and hardware safety validation before OTA deployment:
1. Board Pinout Map & Forbidden Pins (Flash SPI / Strapping)
2. Driver Dependency Resolution & Bus Config
3. Pin & Bus Collision Matrix across active parallel tasks (Digital Twin `current/`)
4. Infinite Loop CPU Starvation Check
5. Resource extraction for Pinout Grid & Bus Map visualization
"""

import re
from typing import List, Dict, Tuple, Set, Any, Optional

HARDWARE_PROFILES = {
    "esp32c6_supermini": {
        "name": "ESP32-C6 SuperMini (RISC-V)",
        "valid_gpios": set(range(0, 24)),
        "forbidden_gpios": {
            24, 25, 26, 27, 28, 29, 30  # Flash SPI / Internal IO
        },
        "strapping_gpios": {8, 9, 15},   # Strapping / Boot pins (warn on input pull)
        "default_led_gpio": 15,
    },
    "esp32c6_devkit": {
        "name": "ESP32-C6 DevKitC-1",
        "valid_gpios": set(range(0, 31)),
        "forbidden_gpios": {24, 25, 26, 27, 28, 29, 30},
        "strapping_gpios": {8, 9, 15},
        "default_led_gpio": 8,
    }
}

# Known standard I2C addresses for common sensors
KNOWN_I2C_DEVICES = {
    "bme280": "0x76",
    "bmp280": "0x76",
    "oled": "0x3C",
    "ssd1306": "0x3C",
    "sh1106": "0x3C",
    "mpu6050": "0x68",
    "aht20": "0x38",
    "sht30": "0x44",
    "ds3231": "0x68",
    "pcf8574": "0x27"
}


class ValidationError:
    def __init__(self, level: str, message: str, line: Optional[int] = None):
        self.level = level  # "ERROR", "WARNING", "INFO"
        self.message = message
        self.line = line

    def __str__(self):
        line_info = f" (Line {self.line})" if self.line else ""
        return f"[{self.level}]{line_info} {self.message}"


class PreFlightValidator:
    """Multi-stage static and cross-context validator for FerrumOS JavaScript scripts."""

    def __init__(self, target_board: str = "esp32c6_supermini"):
        self.target_board = target_board
        self.profile = HARDWARE_PROFILES.get(target_board, HARDWARE_PROFILES["esp32c6_supermini"])

    def extract_resources(self, code: str) -> Dict[str, Any]:
        """Extracts claimed GPIO pins and configured busses from JS script."""
        pins: Dict[int, str] = {}
        i2c_busses: List[Dict[str, Any]] = []
        spi_busses: List[Dict[str, Any]] = []
        uart_busses: List[Dict[str, Any]] = []
        ow_busses: List[Dict[str, Any]] = []

        # 1. GPIO Output / Input bindings: bind_gpio_output("led", 15)
        for m in re.finditer(r'bind_gpio_(?:output|input)\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*\)', code):
            alias, pin = m.group(1), int(m.group(2))
            pins[pin] = f"GPIO:{alias}"

        # 2. Direct gpio.<method>(pin, ...)
        for m in re.finditer(r'gpio\.(?:write|read|mode|output|input|high|low|toggle|set_mode|config)\s*\(\s*(\d+)', code):
            pin = int(m.group(1))
            if pin not in pins:
                pins[pin] = f"DirectGPIO:{pin}"

        # 3. RGB LED: rgb.write(pin, r, g, b) / rgb.set(pin, r, g, b)
        for m in re.finditer(r'rgb\.(?:write|set)\s*\(\s*(\d+)', code):
            pin = int(m.group(1))
            pins[pin] = f"RGB_WS2812:{pin}"

        # 4. I2C Bus: bind_i2c_bus("sensors", sda, scl)
        for m in re.finditer(r'bind_i2c_bus\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', code):
            alias, sda, scl = m.group(1), int(m.group(2)), int(m.group(3))
            # Detect device addresses used in code
            devices = []
            for dev_name, default_addr in KNOWN_I2C_DEVICES.items():
                if dev_name in code.lower():
                    devices.append(f"{dev_name.upper()} ({default_addr})")
            # Also find explicit hex addresses like 0x76, 0x3C
            for hex_m in re.finditer(r'\b0x[0-9a-fA-F]{2}\b', code):
                addr_hex = hex_m.group(0).upper()
                if addr_hex not in [d.split("(")[-1].rstrip(")") for d in devices]:
                    devices.append(f"Custom ({addr_hex})")

            i2c_busses.append({
                "alias": alias,
                "sda": sda,
                "scl": scl,
                "devices": devices or ["Generic I2C (0x??)"]
            })

        # 5. 1-Wire: bind_onewire_bus("alias", pin)
        for m in re.finditer(r'bind_onewire_bus\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*\)', code):
            alias, pin = m.group(1), int(m.group(2))
            ow_busses.append({"alias": alias, "pin": pin})
            pins[pin] = f"1Wire:{alias}"

        # 6. SPI: bind_spi_bus("alias", cs, sck, mosi, miso)
        for m in re.finditer(r'bind_spi_bus\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*(\d+))?\s*\)', code):
            alias = m.group(1)
            cs, sck, mosi = int(m.group(2)), int(m.group(3)), int(m.group(4))
            miso = int(m.group(5)) if m.group(5) else None
            spi_busses.append({"alias": alias, "cs": cs, "sck": sck, "mosi": mosi, "miso": miso})
            pins[cs] = f"SPI_CS:{alias}"

        # 7. UART: bind_uart("alias", tx, rx, baud)
        for m in re.finditer(r'bind_uart(?:_bus)?\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*(\d+))?\s*\)', code):
            alias = m.group(1)
            tx, rx = int(m.group(2)), int(m.group(3))
            baud = int(m.group(4)) if m.group(4) else 115200
            uart_busses.append({"alias": alias, "tx": tx, "rx": rx, "baud": baud})
            pins[tx] = f"UART_TX:{alias}"
            pins[rx] = f"UART_RX:{alias}"

        return {
            "pins": pins,
            "busses": {
                "i2c": i2c_busses,
                "spi": spi_busses,
                "uart": uart_busses,
                "onewire": ow_busses
            }
        }

    def validate(self, script_code: str, existing_pin_claims: Optional[Dict[int, str]] = None) -> Tuple[bool, List[ValidationError], Dict[int, str]]:
        """
        Runs standard single-script pre-flight validation.
        """
        errors: List[ValidationError] = []
        new_claims: Dict[int, str] = dict(existing_pin_claims or {})

        # Stage 1: Syntax & Bracket Matching
        self._check_syntax_and_brackets(script_code, errors)

        # Stage 2: Hardware Profile & Pinout Validation
        self._check_pin_allocations(script_code, errors, new_claims)

        # Stage 3: Driver Dependency & Bus Compliance
        self._check_driver_compliance(script_code, errors)

        # Stage 4: CPU Starvation & Delay Checks
        self._check_cpu_starvation(script_code, errors)

        has_blocking_errors = any(e.level == "ERROR" for e in errors)
        return not has_blocking_errors, errors, new_claims

    def validate_with_context(self, script_code: str, task_id: str, current_manifest: Dict[str, Any]) -> Tuple[bool, List[ValidationError], Dict[str, Any]]:
        """
        Contextual Cross-Validation against the node's `current/` state.
        Verifies that the new/updated task does not conflict with other active tasks in RAM.
        """
        # Run single script checks first
        is_valid, errors, _ = self.validate(script_code)
        resources = self.extract_resources(script_code)

        active_tasks = current_manifest.get("active_tasks", {})

        # 0. Check Task ID length (Max 32 bytes for RWP wire protocol)
        task_id_bytes = len(task_id.encode("utf-8"))
        if task_id_bytes > 32:
            errors.append(ValidationError(
                "ERROR",
                f"Имя задачи '{task_id}' ({task_id_bytes} байт) превышает максимальную длину 32 байта. Пожалуйста, сократите имя скрипта."
            ))
        if task_id_bytes == 0:
            errors.append(ValidationError(
                "ERROR",
                "Имя задачи не может быть пустым."
            ))

        # 1. Check Max Tasks limit
        max_tasks = 8
        if task_id not in active_tasks and len(active_tasks) >= max_tasks:
            errors.append(ValidationError("ERROR", f"Task limit reached ({len(active_tasks)}/{max_tasks}). Unload an existing task first."))

        # 2. Check Pin Collisions against other active tasks (excluding self for safe update)
        for other_id, other_meta in active_tasks.items():
            if other_id == task_id:
                continue  # Self-update is allowed

            other_pins = other_meta.get("pins", {})
            for pin_num, tag in resources["pins"].items():
                pin_key = str(pin_num)
                if pin_key in other_pins or pin_num in other_pins:
                    other_tag = other_pins.get(pin_key) or other_pins.get(pin_num)
                    errors.append(ValidationError(
                        "ERROR",
                        f"Hardware Pin {pin_num} collision! Requested by '{task_id}' ({tag}), but already claimed by active task '{other_id}' ({other_tag})"
                    ))

            # 3. Check Bus Conflicts (I2C sharing vs address clash)
            cand_i2c_list = resources["busses"].get("i2c", [])
            other_i2c_list = other_meta.get("busses", {}).get("i2c", [])
            for cand_i2c in cand_i2c_list:
                for other_i2c in other_i2c_list:
                    # Check SDA/SCL configuration
                    if cand_i2c["sda"] == other_i2c["sda"] and cand_i2c["scl"] == other_i2c["scl"]:
                        # Shared bus! Check for device collisions
                        cand_devs = set(cand_i2c.get("devices", []))
                        other_devs = set(other_i2c.get("devices", []))
                        overlap = cand_devs.intersection(other_devs)
                        if overlap:
                            errors.append(ValidationError(
                                "WARNING",
                                f"Shared I2C Bus (SDA {cand_i2c['sda']}, SCL {cand_i2c['scl']}) device overlap: {overlap} already in use by '{other_id}'"
                            ))
                    elif cand_i2c["sda"] == other_i2c["sda"] or cand_i2c["scl"] == other_i2c["scl"]:
                        errors.append(ValidationError(
                            "ERROR",
                            f"I2C Pin conflict with task '{other_id}': partial SDA/SCL match (Candidate: SDA {cand_i2c['sda']}, SCL {cand_i2c['scl']} vs Active: SDA {other_i2c['sda']}, SCL {other_i2c['scl']})"
                        ))

        has_blocking = any(e.level == "ERROR" for e in errors)
        return not has_blocking, errors, resources

    def _check_syntax_and_brackets(self, code: str, errors: List[ValidationError]):
        stack = []
        pairs = {')': '(', '}': '{', ']': '['}
        in_string = False
        quote_char = None
        escape = False

        for line_idx, line in enumerate(code.splitlines(), start=1):
            i = 0
            while i < len(line):
                ch = line[i]
                if escape:
                    escape = False
                    i += 1
                    continue
                if ch == '\\' and in_string:
                    escape = True
                    i += 1
                    continue
                if not in_string and (ch == '"' or ch == "'"):
                    in_string = True
                    quote_char = ch
                elif in_string and ch == quote_char:
                    in_string = False
                    quote_char = None
                elif not in_string:
                    if ch in '({[':
                        stack.append((ch, line_idx))
                    elif ch in ')}]':
                        if not stack:
                            errors.append(ValidationError("ERROR", f"Unmatched closing '{ch}'", line_idx))
                        else:
                            top, top_line = stack.pop()
                            if top != pairs[ch]:
                                errors.append(ValidationError("ERROR", f"Mismatched '{ch}', expected closing for '{top}' from line {top_line}", line_idx))
                i += 1

        if in_string:
            errors.append(ValidationError("ERROR", f"Unclosed string literal '{quote_char}' at end of script"))
        while stack:
            top, top_line = stack.pop()
            errors.append(ValidationError("ERROR", f"Unclosed opening '{top}'", top_line))

    def _check_pin_allocations(self, code: str, errors: List[ValidationError], claims: Dict[int, str]):
        valid_gpios = self.profile["valid_gpios"]
        forbidden_gpios = self.profile["forbidden_gpios"]

        # Parse GPIO Output / Input bindings
        gpio_matches = re.finditer(r'bind_gpio_(?:output|input)\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*\)', code)
        for m in gpio_matches:
            alias, pin_str = m.group(1), m.group(2)
            pin = int(pin_str)
            self._validate_single_pin(pin, f"GPIO:{alias}", valid_gpios, forbidden_gpios, claims, errors)

        # Parse direct gpio.write(pin, val) / gpio.read(pin)
        direct_gpio_matches = re.finditer(r'gpio\.(?:write|read)\s*\(\s*(\d+)', code)
        for m in direct_gpio_matches:
            pin = int(m.group(1))
            self._validate_single_pin(pin, f"DirectGPIO:{pin}", valid_gpios, forbidden_gpios, claims, errors)

        # Parse RGB LED: rgb.write(pin, r, g, b) / rgb.set(pin, r, g, b)
        rgb_matches = re.finditer(r'rgb\.(?:write|set)\s*\(\s*(\d+)', code)
        for m in rgb_matches:
            pin = int(m.group(1))
            self._validate_single_pin(pin, f"RGB_WS2812:{pin}", valid_gpios, forbidden_gpios, claims, errors)

        # Parse I2C: bind_i2c_bus("alias", sda, scl)
        i2c_matches = re.finditer(r'bind_i2c_bus\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', code)
        for m in i2c_matches:
            alias, sda, scl = m.group(1), int(m.group(2)), int(m.group(3))
            self._validate_single_pin(sda, f"I2C_SDA:{alias}", valid_gpios, forbidden_gpios, claims, errors)
            self._validate_single_pin(scl, f"I2C_SCL:{alias}", valid_gpios, forbidden_gpios, claims, errors)

        # Parse 1-Wire: bind_onewire_bus("alias", pin)
        ow_matches = re.finditer(r'bind_onewire_bus\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*\)', code)
        for m in ow_matches:
            alias, pin = m.group(1), int(m.group(2))
            self._validate_single_pin(pin, f"1Wire:{alias}", valid_gpios, forbidden_gpios, claims, errors)

    def _validate_single_pin(self, pin: int, tag: str, valid: Set[int], forbidden: Set[int], claims: Dict[int, str], errors: List[ValidationError]):
        if pin in forbidden:
            errors.append(ValidationError("ERROR", f"Pin {pin} is FORBIDDEN on {self.profile['name']} (reserved for Flash/Internal). Request: '{tag}'"))
            return
        if pin not in valid:
            errors.append(ValidationError("ERROR", f"Pin {pin} does not exist on {self.profile['name']} (valid range: 0..{max(valid)}). Request: '{tag}'"))
            return
        if pin in claims and claims[pin] != tag:
            errors.append(ValidationError("ERROR", f"Hardware Pin {pin} collision! Requested by '{tag}', but already claimed by '{claims[pin]}'"))
            return
        claims[pin] = tag

    def _check_driver_compliance(self, code: str, errors: List[ValidationError]):
        if "ds18b20" in code and not re.search(r'bind_onewire_bus|ds18b20\.init', code):
            errors.append(ValidationError("WARNING", "DS18B20 sensor used without explicit 'bind_onewire_bus' declaration"))

        if "bme280" in code and not re.search(r'bind_i2c_bus', code):
            errors.append(ValidationError("WARNING", "BME280 I2C sensor used without 'bind_i2c_bus' declaration"))

        if "modbus" in code and not re.search(r'bind_uart|modbus\.init', code):
            errors.append(ValidationError("WARNING", "Modbus RTU used without UART bus configuration"))

    def _check_cpu_starvation(self, code: str, errors: List[ValidationError]):
        for m in re.finditer(r'while\s*\(\s*(?:true|1)\s*\)\s*\{', code):
            start = m.end()
            depth = 1
            idx = start
            while idx < len(code) and depth > 0:
                if code[idx] == '{':
                    depth += 1
                elif code[idx] == '}':
                    depth -= 1
                idx += 1
            body = code[start:idx]
            if not re.search(r'\b(?:delay|delay_ms|yield|ipc\.wait|bus\.wait|mqtt\.wait)\s*\(', body):
                errors.append(ValidationError("ERROR", "Infinite loop `while(true)` without `delay(...)`, `ipc.wait(...)` or `mqtt.wait(...)` detected! This will cause 100% CPU lockup and trigger watchdog."))
