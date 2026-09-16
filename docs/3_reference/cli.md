# Ferrum CLI Reference

`Status: 🟢 Stable (v5.0)` • `Toolchain: Python / Rust Toolchain`

The `ferrum` CLI toolchain manages building, flashing, and packaging for FerrumOS.

## Core Commands
- `ferrum build` — Compiles user JS scripts into bytecode.
- `ferrum flash --target <chip>` — Flashes kernel and bootloader over USB.
- `ferrum as-build` — Compiles AssemblyScript sources (`.ts` -> `.wasm`).
- `ferrum aot-pack` — Generates Ahead-Of-Time RISC-V binary packages (`.faot`).
- `ferrum aot-info <pkg.faot>` — Inspects symbols and VTable in `.faot` bundle.
