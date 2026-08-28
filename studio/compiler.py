"""
FerrumOS Pure Python JavaScript Bytecode Compiler
==================================================
Native Python compiler for FerrumOS VM bytecode.
Compiles subset of JS/Rhai scripts into binary opcodes and .frb containers
with zero external dependencies (no Rust/Cargo required on host!).
"""

import struct
from typing import List, Tuple, Optional, Dict, Any
from .protocol import package_frb, package_rhb

# FerrumOS Bytecode Opcodes (matching Rust VM)
OP_NOP = 0x00
OP_LOG_STR = 0x01
OP_BIND_GPIO = 0x02
OP_GPIO_WRITE = 0x03
OP_GPIO_READ = 0x04
OP_DELAY_MS = 0x05
OP_PUSH_I32 = 0x06
OP_POP = 0x07
OP_ADD = 0x08
OP_SUB = 0x09
OP_MUL = 0x0A
OP_DIV = 0x0B
OP_STORE_VAR = 0x0C
OP_LOAD_VAR = 0x0D
OP_JUMP = 0x0E
OP_JUMP_IF_ZERO = 0x0F
OP_EQ = 0x10
OP_NE = 0x11
OP_LT = 0x12
OP_GT = 0x13
OP_LE = 0x14
OP_GE = 0x15
OP_JUMP_IF_TRUE = 0x16
OP_GPIO_WRITE_DYNAMIC = 0x17
OP_RGB_SET_DYNAMIC = 0x18
OP_CONFIG_PIN_FILTER = 0x19
OP_MOD = 0x1A
OP_CONFIG_BUTTON = 0x1B
OP_BUTTON_READ = 0x1C
OP_BUTTON_WAIT = 0x1D

BTN_EVENT_NONE = 0
BTN_EVENT_CLICK = 1
BTN_EVENT_DOUBLE_CLICK = 2
BTN_EVENT_LONG_PRESS = 3
BTN_EVENT_RELEASE = 4
BTN_EVENT_HOLD = 5

OP_IPC_SEND = 0x20
OP_IPC_RECV = 0x21
OP_IPC_AVAILABLE = 0x22
OP_STATE_SET = 0x23
OP_STATE_GET = 0x24
OP_IPC_PUBLISH = 0x25
OP_IPC_WAIT = 0x26
OP_MQTT_PUBLISH = 0x27
OP_MQTT_SUBSCRIBE = 0x28
OP_MQTT_WAIT = 0x29
OP_MQTT_AVAILABLE = 0x2A
OP_MQTT_RECV = 0x2B
OP_MQTT_CONNECTED = 0x2C
OP_HA_DISCOVERY = 0x2D
OP_MQTT_CONFIG = 0x2E
OP_HALT = 0xFF

# GPIO Config Flags (Packed into 1 Byte)
GPIO_DIR_IN = 0x00
GPIO_DIR_OUT = 0x01

GPIO_TYPE_PUSH_PULL = 0x00
GPIO_TYPE_OPEN_DRAIN = 0x02

GPIO_PULL_NONE = 0x00
GPIO_PULL_UP = 0x04
GPIO_PULL_DOWN = 0x08

GPIO_INIT_LOW = 0x00
GPIO_INIT_HIGH = 0x10
GPIO_HAS_INIT = 0x20
GPIO_FLAG_INVERT = 0x40
GPIO_INVERT = 0x40


def fnv1a_hash(s: str) -> int:
    """Computes a 32-bit signed integer hash for IPC channels and State keys."""
    h = 2166136261
    for b in s.encode("utf-8"):
        h = ((h ^ b) * 16777619) & 0xFFFFFFFF
    if h > 0x7FFFFFFF:
        return h - 0x100000000
    return h


class Token:
    def __init__(self, kind: str, value: Any = None):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r})"


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def peek(self) -> Optional[str]:
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None

    def next_char(self) -> Optional[str]:
        if self.pos < len(self.text):
            c = self.text[self.pos]
            self.pos += 1
            return c
        return None

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < len(self.text):
            ch = self.next_char()
            if ch.isspace():
                continue

            # Comments //
            if ch == "/" and self.peek() == "/":
                self.next_char()
                while self.pos < len(self.text) and self.next_char() != "\n":
                    pass
                continue

            if ch == ".":
                tokens.append(Token("DOT"))
            elif ch == ",":
                tokens.append(Token("COMMA"))
            elif ch == ";":
                tokens.append(Token("SEMI"))
            elif ch == "(":
                tokens.append(Token("LPAREN"))
            elif ch == ")":
                tokens.append(Token("RPAREN"))
            elif ch == "{":
                tokens.append(Token("LBRACE"))
            elif ch == "}":
                tokens.append(Token("RBRACE"))
            elif ch == ":":
                tokens.append(Token("COLON"))
            elif ch == "+":
                tokens.append(Token("PLUS"))
            elif ch == "-":
                tokens.append(Token("MINUS"))
            elif ch == "*":
                tokens.append(Token("STAR"))
            elif ch == "/":
                tokens.append(Token("SLASH"))
            elif ch == "%":
                tokens.append(Token("MOD"))
            elif ch == "=":
                if self.peek() == "=":
                    self.next_char()
                    tokens.append(Token("EQEQ"))
                else:
                    tokens.append(Token("ASSIGN"))
            elif ch == "!":
                if self.peek() == "=":
                    self.next_char()
                    tokens.append(Token("NOTEQ"))
                else:
                    raise SyntaxError(f"Unexpected '!' at pos {self.pos}")
            elif ch == "<":
                if self.peek() == "=":
                    self.next_char()
                    tokens.append(Token("LTEQ"))
                else:
                    tokens.append(Token("LT"))
            elif ch == ">":
                if self.peek() == "=":
                    self.next_char()
                    tokens.append(Token("GTEQ"))
                else:
                    tokens.append(Token("GT"))
            elif ch in ('"', "'"):
                quote = ch
                s = []
                while True:
                    c = self.next_char()
                    if c is None:
                        raise SyntaxError("Unterminated string literal")
                    if c == quote:
                        break
                    s.append(c)
                tokens.append(Token("STRING", "".join(s)))
            elif ch.isdigit():
                num_str = [ch]
                while self.peek() and self.peek().isdigit():
                    num_str.append(self.next_char())
                tokens.append(Token("NUMBER", int("".join(num_str))))
            elif ch.isalpha() or ch == "_":
                ident_chars = [ch]
                while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
                    ident_chars.append(self.next_char())
                ident = "".join(ident_chars)
                if ident in ("let", "var", "const"):
                    tokens.append(Token("LET"))
                elif ident == "while":
                    tokens.append(Token("WHILE"))
                elif ident == "if":
                    tokens.append(Token("IF"))
                elif ident == "else":
                    tokens.append(Token("ELSE"))
                elif ident == "true":
                    tokens.append(Token("TRUE"))
                elif ident == "false":
                    tokens.append(Token("FALSE"))
                else:
                    tokens.append(Token("IDENT", ident))
            else:
                raise SyntaxError(f"Unrecognized character: {ch!r} at pos {self.pos}")

        return tokens


class Compiler:
    def __init__(self):
        self.bytecode = bytearray()
        self.var_names: List[str] = []

    def get_var_slot(self, name: str) -> int:
        if name in self.var_names:
            return self.var_names.index(name)
        if len(self.var_names) >= 32:
            raise ValueError("Maximum 32 variables exceeded in script")
        self.var_names.append(name)
        return len(self.var_names) - 1

    def compile(self, src: str) -> bytes:
        lexer = Lexer(src)
        tokens = lexer.tokenize()
        idx = 0
        while idx < len(tokens):
            idx = self.compile_statement(tokens, idx)

        self.bytecode.append(OP_HALT)
        return bytes(self.bytecode)

    def parse_gpio_config_args(self, tokens: List[Token], idx: int, default_dir: int = GPIO_DIR_OUT) -> Tuple[int, dict, int]:
        flags = default_dir
        filters = {
            "debounce_ms": 0,
            "delayed_on_ms": 0,
            "delayed_off_ms": 0,
            "auto_off_ms": 0,
        }
        if idx >= len(tokens):
            return flags, filters, idx
        tok = tokens[idx]
        if tok.kind == "STRING":
            val = str(tok.value).lower()
            idx += 1
            if val in ("out", "output"):
                flags = (flags & ~0x01) | GPIO_DIR_OUT
            elif val in ("in", "input"):
                flags = (flags & ~0x01) | GPIO_DIR_IN
            elif val in ("input_pullup", "in_pullup", "in_up"):
                flags = (flags & ~0x01) | GPIO_DIR_IN | GPIO_PULL_UP
            elif val in ("input_pulldown", "in_pulldown", "in_down"):
                flags = (flags & ~0x01) | GPIO_DIR_IN | GPIO_PULL_DOWN
            elif val in ("output_opendrain", "open_drain", "out_od"):
                flags = (flags & ~0x01) | GPIO_DIR_OUT | GPIO_TYPE_OPEN_DRAIN
            elif val in ("out_od_pullup", "open_drain_pullup"):
                flags = (flags & ~0x01) | GPIO_DIR_OUT | GPIO_TYPE_OPEN_DRAIN | GPIO_PULL_UP
        elif tok.kind == "LBRACE":
            idx += 1
            while idx < len(tokens) and tokens[idx].kind != "RBRACE":
                key_tok = tokens[idx]
                if key_tok.kind not in ("IDENT", "STRING"):
                    raise SyntaxError("Expected property name in gpio config object")
                key = str(key_tok.value).lower()
                idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "COLON":
                    raise SyntaxError("Expected ':' after property name in gpio config")
                idx += 1
                if idx >= len(tokens):
                    raise SyntaxError("Expected property value in gpio config")
                val_tok = tokens[idx]
                idx += 1

                if key in ("direction", "mode", "dir"):
                    val = str(val_tok.value).lower()
                    if val in ("out", "output", "1"):
                        flags = (flags & ~0x01) | GPIO_DIR_OUT
                    elif val in ("in", "input", "0"):
                        flags = (flags & ~0x01) | GPIO_DIR_IN
                elif key in ("type", "driver"):
                    val = str(val_tok.value).lower()
                    if val in ("open_drain", "od"):
                        flags = (flags & ~0x02) | GPIO_TYPE_OPEN_DRAIN
                    elif val in ("push_pull", "pp"):
                        flags = (flags & ~0x02) | GPIO_TYPE_PUSH_PULL
                elif key in ("pull", "pullup", "pulldown"):
                    val = str(val_tok.value).lower()
                    flags = flags & ~0x0C
                    if val in ("up", "pullup", "pull_up"):
                        flags |= GPIO_PULL_UP
                    elif val in ("down", "pulldown", "pull_down"):
                        flags |= GPIO_PULL_DOWN
                    elif val in ("none", "floating", "0"):
                        flags |= GPIO_PULL_NONE
                elif key in ("initial", "init", "level"):
                    flags |= GPIO_HAS_INIT
                    if val_tok.kind in ("TRUE", "NUMBER") and val_tok.value in (True, 1):
                        flags |= GPIO_INIT_HIGH
                    else:
                        flags &= ~GPIO_INIT_HIGH
                elif key in ("invert", "inverted"):
                    if (val_tok.kind == "TRUE") or (val_tok.kind == "NUMBER" and val_tok.value in (True, 1)):
                        flags |= GPIO_FLAG_INVERT
                    else:
                        flags &= ~GPIO_FLAG_INVERT
                elif key in ("debounce", "debounce_ms"):
                    filters["debounce_ms"] = int(val_tok.value)
                elif key in ("delayed_on", "delayed_on_ms"):
                    filters["delayed_on_ms"] = int(val_tok.value)
                elif key in ("delayed_off", "delayed_off_ms"):
                    filters["delayed_off_ms"] = int(val_tok.value)
                elif key in ("delayed_on_off", "delayed_on_off_ms"):
                    filters["delayed_on_ms"] = int(val_tok.value)
                    filters["delayed_off_ms"] = int(val_tok.value)
                elif key in ("auto_off", "auto_off_ms"):
                    filters["auto_off_ms"] = int(val_tok.value)

                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "RBRACE":
                raise SyntaxError("Expected '}' closing gpio config object")
            idx += 1
        return flags, filters, idx

    def parse_button_config_args(self, tokens: List[Token], idx: int) -> Tuple[int, dict, dict, int]:
        flags = GPIO_DIR_IN | GPIO_PULL_UP | GPIO_FLAG_INVERT
        filters = {
            "debounce_ms": 25,
            "delayed_on_ms": 0,
            "delayed_off_ms": 0,
            "auto_off_ms": 0,
        }
        btn_opts = {
            "click_ms": 350,
            "double_click_ms": 250,
            "long_press_ms": 800,
        }
        if idx >= len(tokens):
            return flags, filters, btn_opts, idx
        
        tok = tokens[idx]
        if tok.kind == "LBRACE":
            idx += 1
            while idx < len(tokens) and tokens[idx].kind != "RBRACE":
                key_tok = tokens[idx]
                if key_tok.kind not in ("IDENT", "STRING"):
                    raise SyntaxError("Expected property name in button config object")
                key = str(key_tok.value).lower()
                idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "COLON":
                    raise SyntaxError("Expected ':' after property name in button config")
                idx += 1
                if idx >= len(tokens):
                    raise SyntaxError("Expected property value in button config")
                val_tok = tokens[idx]
                idx += 1

                if key in ("pull", "pullup", "pulldown"):
                    val = str(val_tok.value).lower()
                    flags = flags & ~0x0C
                    if val in ("up", "pullup", "pull_up"):
                        flags |= GPIO_PULL_UP
                    elif val in ("down", "pulldown", "pull_down"):
                        flags |= GPIO_PULL_DOWN
                    elif val in ("none", "floating", "0"):
                        flags |= GPIO_PULL_NONE
                elif key in ("invert", "inverted"):
                    if (val_tok.kind == "TRUE") or (val_tok.kind == "NUMBER" and val_tok.value in (True, 1)):
                        flags |= GPIO_FLAG_INVERT
                    else:
                        flags &= ~GPIO_FLAG_INVERT
                elif key in ("debounce", "debounce_ms"):
                    filters["debounce_ms"] = int(val_tok.value)
                elif key in ("click", "click_ms", "single_click_ms"):
                    btn_opts["click_ms"] = int(val_tok.value)
                elif key in ("double_click", "double_click_ms", "doubleclick_ms"):
                    btn_opts["double_click_ms"] = int(val_tok.value)
                elif key in ("long_press", "long_press_ms", "longpress_ms", "hold_ms"):
                    btn_opts["long_press_ms"] = int(val_tok.value)

                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "RBRACE":
                raise SyntaxError("Expected '}' closing button config object")
            idx += 1
        return flags, filters, btn_opts, idx

    def compile_statement(self, tokens: List[Token], idx: int) -> int:
        if idx >= len(tokens):
            return idx

        tok = tokens[idx]
        if tok.kind == "SEMI":
            return idx + 1

        if tok.kind == "LET":
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "IDENT":
                raise SyntaxError("Expected variable name after 'let'")
            var_name = tokens[idx].value
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "ASSIGN":
                raise SyntaxError("Expected '=' in variable declaration")
            idx += 1
            idx = self.compile_expression(tokens, idx)
            slot = self.get_var_slot(var_name)
            self.bytecode.append(OP_STORE_VAR)
            self.bytecode.append(slot)
            if idx < len(tokens) and tokens[idx].kind == "SEMI":
                idx += 1
            return idx

        if tok.kind == "WHILE":
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError("Expected '(' after while")
            idx += 1
            loop_start_pc = len(self.bytecode)

            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                raise SyntaxError("Expected ')' after while condition")
            idx += 1

            self.bytecode.append(OP_JUMP_IF_ZERO)
            patch_jump_offset = len(self.bytecode)
            self.bytecode.extend(b"\x00\x00\x00\x00")

            if idx >= len(tokens) or tokens[idx].kind != "LBRACE":
                raise SyntaxError("Expected '{' for while block")
            idx += 1
            while idx < len(tokens) and tokens[idx].kind != "RBRACE":
                idx = self.compile_statement(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "RBRACE":
                raise SyntaxError("Expected '}' closing while block")
            idx += 1

            # Loop jump back
            self.bytecode.append(OP_JUMP)
            self.bytecode.extend(struct.pack("<I", loop_start_pc))

            # Patch exit PC
            loop_exit_pc = len(self.bytecode)
            self.bytecode[patch_jump_offset:patch_jump_offset + 4] = struct.pack("<I", loop_exit_pc)
            return idx

        if tok.kind == "IF":
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError("Expected '(' after if")
            idx += 1
            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                raise SyntaxError("Expected ')' after if condition")
            idx += 1

            self.bytecode.append(OP_JUMP_IF_ZERO)
            patch_else_jump = len(self.bytecode)
            self.bytecode.extend(b"\x00\x00\x00\x00")

            if idx >= len(tokens) or tokens[idx].kind != "LBRACE":
                raise SyntaxError("Expected '{' for if block")
            idx += 1
            while idx < len(tokens) and tokens[idx].kind != "RBRACE":
                idx = self.compile_statement(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "RBRACE":
                raise SyntaxError("Expected '}' closing if block")
            idx += 1

            has_else = (idx < len(tokens) and tokens[idx].kind == "ELSE")
            if has_else:
                idx += 1
                self.bytecode.append(OP_JUMP)
                patch_exit_jump = len(self.bytecode)
                self.bytecode.extend(b"\x00\x00\x00\x00")

                else_start_pc = len(self.bytecode)
                self.bytecode[patch_else_jump:patch_else_jump + 4] = struct.pack("<I", else_start_pc)

                if idx < len(tokens) and tokens[idx].kind == "IF":
                    idx = self.compile_statement(tokens, idx)
                elif idx < len(tokens) and tokens[idx].kind == "LBRACE":
                    idx += 1
                    while idx < len(tokens) and tokens[idx].kind != "RBRACE":
                        idx = self.compile_statement(tokens, idx)
                    if idx >= len(tokens) or tokens[idx].kind != "RBRACE":
                        raise SyntaxError("Expected '}' closing else block")
                    idx += 1
                else:
                    idx = self.compile_statement(tokens, idx)

                exit_pc = len(self.bytecode)
                self.bytecode[patch_exit_jump:patch_exit_jump + 4] = struct.pack("<I", exit_pc)
            else:
                exit_pc = len(self.bytecode)
                self.bytecode[patch_else_jump:patch_else_jump + 4] = struct.pack("<I", exit_pc)
            return idx

        # delay(...) or sleep(...)
        if tok.kind == "IDENT" and tok.value in ("delay", "sleep"):
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError("Expected '(' after delay")
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "NUMBER":
                raise SyntaxError("Expected number in delay(...)")
            ms = int(tokens[idx].value)
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                raise SyntaxError("Expected ')' after delay argument")
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "SEMI":
                idx += 1
            self.bytecode.append(OP_DELAY_MS)
            self.bytecode.extend(struct.pack("<I", ms))
            return idx

        # print(...) or console.log(...)
        if tok.kind == "IDENT" and tok.value in ("print", "console"):
            if tok.value == "console":
                idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "DOT":
                    raise SyntaxError("Expected '.' after console")
                idx += 1
                if idx >= len(tokens) or tokens[idx].value != "log":
                    raise SyntaxError("Expected 'log' after console.")

            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError("Expected '(' after print/log")
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "STRING":
                raise SyntaxError("Expected string literal in print(...)")
            msg = str(tokens[idx].value).encode("utf-8")
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                raise SyntaxError("Expected ')' closing print")
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "SEMI":
                idx += 1

            self.bytecode.append(OP_LOG_STR)
            self.bytecode.extend(struct.pack("<H", len(msg)))
            self.bytecode.extend(msg)
            return idx

        # gpio.<method>(...)
        if tok.kind == "IDENT" and tok.value == "gpio":
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "DOT":
                raise SyntaxError("Expected '.' after gpio")
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "IDENT":
                raise SyntaxError("Expected method name after gpio.")
            method = tokens[idx].value
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError(f"Expected '(' after gpio.{method}")
            idx += 1

            if method in ("mode", "set_mode", "config", "setup"):
                if idx >= len(tokens) or tokens[idx].kind != "NUMBER":
                    raise SyntaxError("Expected pin number in gpio.mode")
                pin = tokens[idx].value
                idx += 1
                flags = GPIO_DIR_OUT
                filters = {"debounce_ms": 0, "delayed_on_ms": 0, "delayed_off_ms": 0, "auto_off_ms": 0}
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    flags, filters, idx = self.parse_gpio_config_args(tokens, idx, default_dir=GPIO_DIR_OUT)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing gpio.mode")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                self.bytecode.append(OP_BIND_GPIO)
                self.bytecode.append(pin & 0xFF)
                self.bytecode.append(flags & 0xFF)
                if any(filters.values()):
                    self.bytecode.append(OP_CONFIG_PIN_FILTER)
                    self.bytecode.append(pin & 0xFF)
                    self.bytecode.extend(struct.pack("<HHHH",
                        filters["debounce_ms"],
                        filters["delayed_on_ms"],
                        filters["delayed_off_ms"],
                        filters["auto_off_ms"],
                    ))
                return idx

            elif method in ("output", "out"):
                if idx >= len(tokens) or tokens[idx].kind != "NUMBER":
                    raise SyntaxError("Expected pin number in gpio.output")
                pin = tokens[idx].value
                idx += 1
                flags = GPIO_DIR_OUT
                filters = {"debounce_ms": 0, "delayed_on_ms": 0, "delayed_off_ms": 0, "auto_off_ms": 0}
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    flags, filters, idx = self.parse_gpio_config_args(tokens, idx, default_dir=GPIO_DIR_OUT)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing gpio.output")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                self.bytecode.append(OP_BIND_GPIO)
                self.bytecode.append(pin & 0xFF)
                self.bytecode.append(flags & 0xFF)
                if any(filters.values()):
                    self.bytecode.append(OP_CONFIG_PIN_FILTER)
                    self.bytecode.append(pin & 0xFF)
                    self.bytecode.extend(struct.pack("<HHHH",
                        filters["debounce_ms"],
                        filters["delayed_on_ms"],
                        filters["delayed_off_ms"],
                        filters["auto_off_ms"],
                    ))
                return idx

            elif method in ("input", "in"):
                if idx >= len(tokens) or tokens[idx].kind != "NUMBER":
                    raise SyntaxError("Expected pin number in gpio.input")
                pin = tokens[idx].value
                idx += 1
                flags = GPIO_DIR_IN
                filters = {"debounce_ms": 0, "delayed_on_ms": 0, "delayed_off_ms": 0, "auto_off_ms": 0}
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    flags, filters, idx = self.parse_gpio_config_args(tokens, idx, default_dir=GPIO_DIR_IN)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing gpio.input")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                self.bytecode.append(OP_BIND_GPIO)
                self.bytecode.append(pin & 0xFF)
                self.bytecode.append(flags & 0xFF)
                if any(filters.values()):
                    self.bytecode.append(OP_CONFIG_PIN_FILTER)
                    self.bytecode.append(pin & 0xFF)
                    self.bytecode.extend(struct.pack("<HHHH",
                        filters["debounce_ms"],
                        filters["delayed_on_ms"],
                        filters["delayed_off_ms"],
                        filters["auto_off_ms"],
                    ))
                return idx

            elif method in ("button", "btn"):
                if idx >= len(tokens) or tokens[idx].kind != "NUMBER":
                    raise SyntaxError(f"Expected pin number in gpio.{method}")
                pin = tokens[idx].value
                idx += 1
                flags = GPIO_DIR_IN | GPIO_PULL_UP | GPIO_FLAG_INVERT
                filters = {"debounce_ms": 25, "delayed_on_ms": 0, "delayed_off_ms": 0, "auto_off_ms": 0}
                btn_opts = {"click_ms": 350, "double_click_ms": 250, "long_press_ms": 800}
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    flags, filters, btn_opts, idx = self.parse_button_config_args(tokens, idx)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError(f"Expected ')' closing gpio.{method}")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                self.bytecode.append(OP_BIND_GPIO)
                self.bytecode.append(pin & 0xFF)
                self.bytecode.append(flags & 0xFF)
                if any(filters.values()):
                    self.bytecode.append(OP_CONFIG_PIN_FILTER)
                    self.bytecode.append(pin & 0xFF)
                    self.bytecode.extend(struct.pack("<HHHH",
                        filters["debounce_ms"],
                        filters["delayed_on_ms"],
                        filters["delayed_off_ms"],
                        filters["auto_off_ms"],
                    ))
                self.bytecode.append(OP_CONFIG_BUTTON)
                self.bytecode.append(pin & 0xFF)
                self.bytecode.extend(struct.pack("<HHH",
                    btn_opts["click_ms"],
                    btn_opts["double_click_ms"],
                    btn_opts["long_press_ms"],
                ))
                return idx

            elif method == "write":
                idx = self.compile_expression(tokens, idx)
                if idx >= len(tokens) or tokens[idx].kind != "COMMA":
                    raise SyntaxError("Expected ',' in gpio.write(pin, val)")
                idx += 1
                idx = self.compile_expression(tokens, idx)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing gpio.write")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                self.bytecode.append(OP_GPIO_WRITE_DYNAMIC)
                return idx

            elif method == "high":
                idx = self.compile_expression(tokens, idx)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing gpio.high")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", 1))
                self.bytecode.append(OP_GPIO_WRITE_DYNAMIC)
                return idx

            elif method == "low":
                idx = self.compile_expression(tokens, idx)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing gpio.low")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", 0))
                self.bytecode.append(OP_GPIO_WRITE_DYNAMIC)
                return idx

            elif method in ("read", "get", "is_high", "is_low"):
                idx = self.compile_expression(tokens, idx)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError(f"Expected ')' closing gpio.{method}")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                self.bytecode.append(OP_GPIO_READ)
                self.bytecode.append(OP_POP)
                return idx

            else:
                raise SyntaxError(f"Unknown gpio method '{method}'")

        # rgb.set(pin, r, g, b) or rgb.write(pin, r, g, b)
        if tok.kind == "IDENT" and tok.value == "rgb":
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "DOT":
                raise SyntaxError("Expected '.' after rgb")
            idx += 1
            if idx >= len(tokens) or tokens[idx].value not in ("write", "set"):
                raise SyntaxError("Expected 'set' or 'write' after rgb.")
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError("Expected '(' after rgb.set")
            idx += 1
            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "COMMA":
                raise SyntaxError("Expected ',' after pin in rgb.set(pin, r, g, b)")
            idx += 1
            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "COMMA":
                raise SyntaxError("Expected ',' after r in rgb.set(pin, r, g, b)")
            idx += 1
            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "COMMA":
                raise SyntaxError("Expected ',' after g in rgb.set(pin, r, g, b)")
            idx += 1
            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                raise SyntaxError("Expected ')' closing rgb.set")
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "SEMI":
                idx += 1

            self.bytecode.append(OP_RGB_SET_DYNAMIC)
            return idx

        # ipc.send / ipc.publish / bus.emit
        if tok.kind == "IDENT" and tok.value in ("ipc", "bus"):
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "DOT":
                raise SyntaxError(f"Expected '.' after {tok.value}")
            idx += 1
            method = tokens[idx].value
            if method not in ("send", "post", "publish", "emit"):
                raise SyntaxError(f"Expected 'send', 'post', 'publish' or 'emit' after {tok.value}.")
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError(f"Expected '(' after {tok.value}.{method}")
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "STRING":
                chan_id = fnv1a_hash(tokens[idx].value)
                idx += 1
                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", chan_id))
            else:
                idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "COMMA":
                raise SyntaxError(f"Expected ',' in {tok.value}.{method}(channel, val)")
            idx += 1
            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                raise SyntaxError(f"Expected ')' closing {tok.value}.{method}")
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "SEMI":
                idx += 1
            if method in ("publish", "emit"):
                self.bytecode.append(OP_IPC_PUBLISH)
            else:
                self.bytecode.append(OP_IPC_SEND)
            return idx

        # state.set(key, val)
        if tok.kind == "IDENT" and tok.value == "state":
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "DOT":
                raise SyntaxError("Expected '.' after state")
            idx += 1
            if tokens[idx].value != "set":
                raise SyntaxError("Expected 'set' after state.")
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError("Expected '(' after state.set")
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "STRING":
                key_id = fnv1a_hash(tokens[idx].value)
                idx += 1
                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", key_id))
            else:
                idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "COMMA":
                raise SyntaxError("Expected ',' in state.set(key, val)")
            idx += 1
            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                raise SyntaxError("Expected ')' closing state.set")
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "SEMI":
                idx += 1
            self.bytecode.append(OP_STATE_SET)
            return idx

        # mqtt.publish / mqtt.subscribe / mqtt.ha_discovery
        if tok.kind == "IDENT" and tok.value == "mqtt":
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "DOT":
                raise SyntaxError("Expected '.' after mqtt")
            idx += 1
            method = tokens[idx].value
            idx += 1
            if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                raise SyntaxError(f"Expected '(' after mqtt.{method}")
            idx += 1

            if method in ("connect", "config"):
                if idx >= len(tokens) or tokens[idx].kind != "STRING":
                    raise SyntaxError("Expected string host/IP in mqtt.connect(host, ...)")
                host_str = tokens[idx].value
                idx += 1
                port = 1883
                user_str = ""
                pass_str = ""
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "NUMBER":
                        port = tokens[idx].value
                        idx += 1
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "STRING":
                        user_str = tokens[idx].value
                        idx += 1
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "STRING":
                        pass_str = tokens[idx].value
                        idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing mqtt.connect")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1

                octets = [192, 168, 1, 114]
                try:
                    parts = [int(p) for p in host_str.split(".")]
                    if len(parts) == 4:
                        octets = parts
                except Exception:
                    pass

                self.bytecode.append(OP_MQTT_CONFIG)
                self.bytecode.extend(bytes(octets))
                self.bytecode.extend(struct.pack("<H", port))

                u_bytes = user_str.encode("utf-8")
                self.bytecode.extend(struct.pack("<H", len(u_bytes)))
                self.bytecode.extend(u_bytes)

                p_bytes = pass_str.encode("utf-8")
                self.bytecode.extend(struct.pack("<H", len(p_bytes)))
                self.bytecode.extend(p_bytes)
                return idx

            elif method == "publish":
                if idx >= len(tokens) or tokens[idx].kind != "STRING":
                    raise SyntaxError("Expected string topic in mqtt.publish(topic, val)")
                topic_str = tokens[idx].value
                idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "COMMA":
                    raise SyntaxError("Expected ',' after topic in mqtt.publish")
                idx += 1
                idx = self.compile_expression(tokens, idx)
                qos = 0
                retain = 0
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "NUMBER":
                        qos = tokens[idx].value
                        idx += 1
                    if idx < len(tokens) and tokens[idx].kind == "COMMA":
                        idx += 1
                        if tokens[idx].kind in ("TRUE", "NUMBER"):
                            retain = 1
                            idx += 1
                        elif tokens[idx].kind == "FALSE":
                            retain = 0
                            idx += 1
                
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing mqtt.publish")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1

                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", qos))
                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", retain))

                topic_bytes = topic_str.encode("utf-8")
                self.bytecode.append(OP_MQTT_PUBLISH)
                self.bytecode.extend(struct.pack("<H", len(topic_bytes)))
                self.bytecode.extend(topic_bytes)
                return idx

            elif method == "subscribe":
                if idx >= len(tokens) or tokens[idx].kind != "STRING":
                    raise SyntaxError("Expected string topic in mqtt.subscribe(topic)")
                topic_str = tokens[idx].value
                idx += 1
                qos = 0
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "NUMBER":
                        qos = tokens[idx].value
                        idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing mqtt.subscribe")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1

                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", qos))

                topic_bytes = topic_str.encode("utf-8")
                self.bytecode.append(OP_MQTT_SUBSCRIBE)
                self.bytecode.extend(struct.pack("<H", len(topic_bytes)))
                self.bytecode.extend(topic_bytes)
                return idx

            elif method == "ha_discovery":
                comp = "sensor"
                name = "Sensor"
                topic = "home/sensor"
                unit = ""
                dev_class = ""
                if idx < len(tokens) and tokens[idx].kind == "STRING":
                    comp = tokens[idx].value
                    idx += 1
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "STRING":
                        name = tokens[idx].value
                        idx += 1
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "STRING":
                        topic = tokens[idx].value
                        idx += 1
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "STRING":
                        unit = tokens[idx].value
                        idx += 1
                if idx < len(tokens) and tokens[idx].kind == "COMMA":
                    idx += 1
                    if tokens[idx].kind == "STRING":
                        dev_class = tokens[idx].value
                        idx += 1
                if idx < len(tokens) and tokens[idx].kind == "RPAREN":
                    idx += 1
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1

                ha_cfg_json = f'{{"name":"{name}","state_topic":"{topic}"'
                if unit:
                    ha_cfg_json += f',"unit_of_measurement":"{unit}"'
                if dev_class:
                    ha_cfg_json += f',"device_class":"{dev_class}"'
                ha_cfg_json += f',"unique_id":"ferrum_{topic.replace("/", "_")}"}}'

                ha_topic = f"homeassistant/{comp}/ferrum_{topic.replace('/', '_')}/config"
                cfg_bytes = ha_cfg_json.encode("utf-8")
                top_bytes = ha_topic.encode("utf-8")

                self.bytecode.append(OP_HA_DISCOVERY)
                self.bytecode.extend(struct.pack("<H", len(cfg_bytes)))
                self.bytecode.extend(cfg_bytes)
                self.bytecode.extend(struct.pack("<H", len(top_bytes)))
                self.bytecode.extend(top_bytes)
                return idx

        # var assignment: a = 5;
        if tok.kind == "IDENT":
            var_name = tok.value
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "ASSIGN":
                idx += 1
                idx = self.compile_expression(tokens, idx)
                slot = self.get_var_slot(var_name)
                self.bytecode.append(OP_STORE_VAR)
                self.bytecode.append(slot)
                if idx < len(tokens) and tokens[idx].kind == "SEMI":
                    idx += 1
                return idx

        raise SyntaxError(f"Unexpected token at statement start: {tok}")

    def compile_expression(self, tokens: List[Token], idx: int) -> int:
        return self.compile_comparison(tokens, idx)

    def compile_comparison(self, tokens: List[Token], idx: int) -> int:
        idx = self.compile_additive(tokens, idx)
        while idx < len(tokens):
            k = tokens[idx].kind
            if k == "EQEQ":
                idx += 1
                idx = self.compile_additive(tokens, idx)
                self.bytecode.append(OP_EQ)
            elif k == "NOTEQ":
                idx += 1
                idx = self.compile_additive(tokens, idx)
                self.bytecode.append(OP_NE)
            elif k == "LT":
                idx += 1
                idx = self.compile_additive(tokens, idx)
                self.bytecode.append(OP_LT)
            elif k == "LTEQ":
                idx += 1
                idx = self.compile_additive(tokens, idx)
                self.bytecode.append(OP_LE)
            elif k == "GT":
                idx += 1
                idx = self.compile_additive(tokens, idx)
                self.bytecode.append(OP_GT)
            elif k == "GTEQ":
                idx += 1
                idx = self.compile_additive(tokens, idx)
                self.bytecode.append(OP_GE)
            else:
                break
        return idx

    def compile_additive(self, tokens: List[Token], idx: int) -> int:
        idx = self.compile_multiplicative(tokens, idx)
        while idx < len(tokens):
            k = tokens[idx].kind
            if k == "PLUS":
                idx += 1
                idx = self.compile_multiplicative(tokens, idx)
                self.bytecode.append(OP_ADD)
            elif k == "MINUS":
                idx += 1
                idx = self.compile_multiplicative(tokens, idx)
                self.bytecode.append(OP_SUB)
            else:
                break
        return idx

    def compile_multiplicative(self, tokens: List[Token], idx: int) -> int:
        idx = self.compile_primary(tokens, idx)
        while idx < len(tokens):
            k = tokens[idx].kind
            if k == "STAR":
                idx += 1
                idx = self.compile_primary(tokens, idx)
                self.bytecode.append(OP_MUL)
            elif k == "SLASH":
                idx += 1
                idx = self.compile_primary(tokens, idx)
                self.bytecode.append(OP_DIV)
            elif k == "MOD":
                idx += 1
                idx = self.compile_primary(tokens, idx)
                self.bytecode.append(OP_MOD)
            else:
                break
        return idx

    def compile_primary(self, tokens: List[Token], idx: int) -> int:
        if idx >= len(tokens):
            raise SyntaxError("Unexpected end of expression")

        tok = tokens[idx]
        if tok.kind == "MINUS":
            idx += 1
            if idx < len(tokens) and tokens[idx].kind == "NUMBER":
                val = -int(tokens[idx].value)
                idx += 1
                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", val))
                return idx
            else:
                idx = self.compile_primary(tokens, idx)
                self.bytecode.append(OP_PUSH_I32)
                self.bytecode.extend(struct.pack("<i", -1))
                self.bytecode.append(OP_MUL)
                return idx

        if tok.kind == "NUMBER":
            val = int(tok.value)
            idx += 1
            self.bytecode.append(OP_PUSH_I32)
            self.bytecode.extend(struct.pack("<i", val))
            return idx

        if tok.kind == "TRUE":
            idx += 1
            self.bytecode.append(OP_PUSH_I32)
            self.bytecode.extend(struct.pack("<i", 1))
            return idx

        if tok.kind == "FALSE":
            idx += 1
            self.bytecode.append(OP_PUSH_I32)
            self.bytecode.extend(struct.pack("<i", 0))
            return idx

        if tok.kind == "STRING":
            val_str = str(tok.value).lower()
            if val_str == "click":
                val = BTN_EVENT_CLICK
            elif val_str in ("double_click", "doubleclick"):
                val = BTN_EVENT_DOUBLE_CLICK
            elif val_str in ("long_press", "longpress", "hold"):
                val = BTN_EVENT_LONG_PRESS
            elif val_str == "release":
                val = BTN_EVENT_RELEASE
            elif val_str == "none":
                val = BTN_EVENT_NONE
            else:
                val = fnv1a_hash(tok.value)
            idx += 1
            self.bytecode.append(OP_PUSH_I32)
            self.bytecode.extend(struct.pack("<i", val))
            return idx

        if tok.kind == "IDENT":
            if tok.value in ("ipc", "bus") and idx + 1 < len(tokens) and tokens[idx + 1].kind == "DOT":
                idx += 2
                if idx >= len(tokens) or tokens[idx].value not in ("recv", "available", "wait"):
                    raise SyntaxError(f"Expected 'recv', 'available' or 'wait' after ipc., got {tokens[idx] if idx < len(tokens) else 'EOF'}")
                method = tokens[idx].value
                idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                    raise SyntaxError(f"Expected '(' after ipc.{method}")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "STRING":
                    chan_id = fnv1a_hash(tokens[idx].value)
                    idx += 1
                    self.bytecode.append(OP_PUSH_I32)
                    self.bytecode.extend(struct.pack("<i", chan_id))
                else:
                    idx = self.compile_expression(tokens, idx)

                if method == "wait":
                    if idx < len(tokens) and tokens[idx].kind == "COMMA":
                        idx += 1
                        idx = self.compile_expression(tokens, idx)
                    else:
                        # Default 0 ms timeout
                        self.bytecode.append(OP_PUSH_I32)
                        self.bytecode.extend(struct.pack("<i", 0))

                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError(f"Expected ')' closing ipc.{method}")
                idx += 1
                if method == "recv":
                    self.bytecode.append(OP_IPC_RECV)
                elif method == "available":
                    self.bytecode.append(OP_IPC_AVAILABLE)
                elif method == "wait":
                    self.bytecode.append(OP_IPC_WAIT)
                return idx

            if tok.value == "state" and idx + 1 < len(tokens) and tokens[idx + 1].kind == "DOT":
                idx += 2
                if idx >= len(tokens) or tokens[idx].value != "get":
                    raise SyntaxError(f"Expected 'get' after state., got {tokens[idx] if idx < len(tokens) else 'EOF'}")
                idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                    raise SyntaxError("Expected '(' after state.get")
                idx += 1
                if idx < len(tokens) and tokens[idx].kind == "STRING":
                    key_id = fnv1a_hash(tokens[idx].value)
                    idx += 1
                    self.bytecode.append(OP_PUSH_I32)
                    self.bytecode.extend(struct.pack("<i", key_id))
                else:
                    idx = self.compile_expression(tokens, idx)
                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError("Expected ')' closing state.get")
                idx += 1
                self.bytecode.append(OP_STATE_GET)
                return idx

            if tok.value == "mqtt" and idx + 1 < len(tokens) and tokens[idx + 1].kind == "DOT":
                idx += 2
                method = tokens[idx].value
                idx += 1
                if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                    raise SyntaxError(f"Expected '(' after mqtt.{method}")
                idx += 1

                if method == "connected":
                    if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                        raise SyntaxError("Expected ')' after mqtt.connected")
                    idx += 1
                    self.bytecode.append(OP_MQTT_CONNECTED)
                    return idx

                if idx >= len(tokens) or tokens[idx].kind != "STRING":
                    raise SyntaxError(f"Expected string topic in mqtt.{method}(topic)")
                topic_str = tokens[idx].value
                idx += 1

                if method == "wait":
                    if idx < len(tokens) and tokens[idx].kind == "COMMA":
                        idx += 1
                        idx = self.compile_expression(tokens, idx)
                    else:
                        self.bytecode.append(OP_PUSH_I32)
                        self.bytecode.extend(struct.pack("<i", 0))

                if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                    raise SyntaxError(f"Expected ')' closing mqtt.{method}")
                idx += 1

                topic_bytes = topic_str.encode("utf-8")
                if method == "wait":
                    self.bytecode.append(OP_MQTT_WAIT)
                elif method == "recv":
                    self.bytecode.append(OP_MQTT_RECV)
                elif method == "available":
                    self.bytecode.append(OP_MQTT_AVAILABLE)
                self.bytecode.extend(struct.pack("<H", len(topic_bytes)))
                self.bytecode.extend(topic_bytes)
                return idx

            if tok.value == "gpio" and idx + 1 < len(tokens) and tokens[idx + 1].kind == "DOT":
                idx += 2
                method = tokens[idx].value if idx < len(tokens) else ""
                if method in ("button", "btn"):
                    idx += 1
                    if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                        raise SyntaxError("Expected '(' after gpio.button")
                    idx += 1
                    if idx >= len(tokens) or tokens[idx].kind != "NUMBER":
                        raise SyntaxError("Expected pin number in gpio.button")
                    pin = tokens[idx].value
                    idx += 1
                    flags = GPIO_DIR_IN | GPIO_PULL_UP | GPIO_FLAG_INVERT
                    filters = {"debounce_ms": 25, "delayed_on_ms": 0, "delayed_off_ms": 0, "auto_off_ms": 0}
                    btn_opts = {"click_ms": 350, "double_click_ms": 250, "long_press_ms": 800}
                    if idx < len(tokens) and tokens[idx].kind == "COMMA":
                        idx += 1
                        flags, filters, btn_opts, idx = self.parse_button_config_args(tokens, idx)
                    if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                        raise SyntaxError("Expected ')' closing gpio.button")
                    idx += 1
                    self.bytecode.append(OP_BIND_GPIO)
                    self.bytecode.append(pin & 0xFF)
                    self.bytecode.append(flags & 0xFF)
                    if any(filters.values()):
                        self.bytecode.append(OP_CONFIG_PIN_FILTER)
                        self.bytecode.append(pin & 0xFF)
                        self.bytecode.extend(struct.pack("<HHHH",
                            filters["debounce_ms"],
                            filters["delayed_on_ms"],
                            filters["delayed_off_ms"],
                            filters["auto_off_ms"],
                        ))
                    self.bytecode.append(OP_CONFIG_BUTTON)
                    self.bytecode.append(pin & 0xFF)
                    self.bytecode.extend(struct.pack("<HHH",
                        btn_opts["click_ms"],
                        btn_opts["double_click_ms"],
                        btn_opts["long_press_ms"],
                    ))
                    # Push pin number so variable receives pin id
                    self.bytecode.append(OP_PUSH_I32)
                    self.bytecode.extend(struct.pack("<i", pin))
                    return idx

                if method in ("read", "get", "is_high", "is_low"):
                    idx += 1
                    if idx >= len(tokens) or tokens[idx].kind != "LPAREN":
                        raise SyntaxError(f"Expected '(' after gpio.{method}")
                    idx += 1
                    idx = self.compile_expression(tokens, idx)
                    if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                        raise SyntaxError(f"Expected ')' closing gpio.{method}")
                    idx += 1
                    self.bytecode.append(OP_GPIO_READ)
                    if method == "is_high":
                        self.bytecode.append(OP_PUSH_I32)
                        self.bytecode.extend(struct.pack("<i", 1))
                        self.bytecode.append(OP_EQ)
                    elif method == "is_low":
                        self.bytecode.append(OP_PUSH_I32)
                        self.bytecode.extend(struct.pack("<i", 0))
                        self.bytecode.append(OP_EQ)
                    return idx

            # Method calls on button instance: btn.read(), btn.wait([timeout])
            if idx + 1 < len(tokens) and tokens[idx + 1].kind == "DOT":
                method_tok = tokens[idx + 2] if idx + 2 < len(tokens) else None
                if method_tok and method_tok.value in ("read", "wait") and idx + 3 < len(tokens) and tokens[idx + 3].kind == "LPAREN":
                    var_name = tok.value
                    method_name = method_tok.value
                    idx += 4
                    if method_name == "wait":
                        if idx < len(tokens) and tokens[idx].kind != "RPAREN":
                            idx = self.compile_expression(tokens, idx)
                        else:
                            self.bytecode.append(OP_PUSH_I32)
                            self.bytecode.extend(struct.pack("<i", 0))
                    if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                        raise SyntaxError(f"Expected ')' closing {var_name}.{method_name}")
                    idx += 1
                    
                    slot = self.get_var_slot(var_name)
                    self.bytecode.append(OP_LOAD_VAR)
                    self.bytecode.append(slot)
                    
                    if method_name == "read":
                        self.bytecode.append(OP_BUTTON_READ)
                    elif method_name == "wait":
                        self.bytecode.append(OP_BUTTON_WAIT)
                    return idx

            var_name = tok.value
            idx += 1
            slot = self.get_var_slot(var_name)
            self.bytecode.append(OP_LOAD_VAR)
            self.bytecode.append(slot)
            return idx

        if tok.kind == "LPAREN":
            idx += 1
            idx = self.compile_expression(tokens, idx)
            if idx >= len(tokens) or tokens[idx].kind != "RPAREN":
                raise SyntaxError("Expected ')' closing expression")
            idx += 1
            return idx

        raise SyntaxError(f"Expected primary expression, got {tok}")


def compile_js_to_bytecode(src: str) -> bytes:
    """Compiles JavaScript source string to binary FerrumOS VM opcodes."""
    compiler = Compiler()
    return compiler.compile(src)


def compile_js_to_frb(src: str) -> bytes:
    """Compiles JavaScript source string into a complete .frb container (Magic + CRC16 + Bytecode)."""
    raw_bytecode = compile_js_to_bytecode(src)
    return package_frb(raw_bytecode)


# Backward compatibility alias
compile_js_to_rhb = compile_js_to_frb
