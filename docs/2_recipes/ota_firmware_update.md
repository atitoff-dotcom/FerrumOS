# How-To: Over-The-Air (OTA) Updates & Hot-Swap

`Status: 🟢 Hot-Swap Live (v5.0) / 🟣 Dual-Boot Kernel (Roadmap Phase 8)` • `Targets: ESP32-C6, ESP32-C3`

> [!NOTE]
> **Current Capabilities:**
> - **Live Bytecode Hot-Swap (Ready in v5.0)**: Injects updated JavaScript bytecode in <100ms via Studio/CLI without restarting peripherals or breaking network sockets.
> - **A/B Dual-Boot Kernel OTA (Roadmap Phase 8)**: Upgrading the core Rust operating system kernel binary over Wi-Fi is scheduled for Phase 8 in [ROADMAP.md](https://github.com/atitoff-dotcom/FerrumOS).

FerrumOS features a dual-layer update model:
1. **Script/Bytecode Hot-Swap**: Replace task logic on a live device in **< 100 ms** without rebooting the microcontroller or dropping network connections.
2. **Kernel Dual-Boot A/B**: Safe over-the-air update of the underlying Rust operating system kernel with automatic rollback on boot failure.

---

## 1. Bytecode Hot-Swap from Studio

When you click **Deploy** in FerrumOS Studio:
1. The compiler generates bytecode (.fbc).
2. The bytecode is streamed over the wire protocol (Frame `0x03`).
3. The virtual machine pauses the target task, swaps the execution buffer, resets local frame pointers, and resumes execution seamlessly.

---

## 2. A/B Dual-Boot Kernel Firmware Update

For updating the core operating system:
- **Partition A**: Currently running active kernel.
- **Partition B**: Target partition receiving the new binary.

```bash
# Upload new kernel binary via Ferrum CLI
ferrum ota-push --target 192.168.1.150 --firmware build/esp32c6_firmware.bin
```

### Anti-Brick Rollback Mechanism
1. After flashing Partition B, the bootloader marks it as `STATE_PENDING_VERIFY`.
2. The device reboots into Partition B.
3. The new kernel must complete self-tests (connect to network, verify hardware) within 30 seconds and call `System.confirmBoot()`.
4. If a watchdog reset or panic occurs before confirmation, the hardware bootloader automatically reverts to Partition A.
