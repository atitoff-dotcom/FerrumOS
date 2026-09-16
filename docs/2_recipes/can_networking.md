# How-To: CAN Bus Networking & Distributed Signals

`Status: 🟢 Stable (v5.1)` • `Target: ESP32-C6 & ESP32-C3 (TWAI)` • `Since: FerrumOS 5.1` • [RFC-0001 (Distributed CAN)](../rfcs/0001-can-distributed-bus.md)

> [!NOTE]
> **Implementation Status**: Hardware CAN 2.0B / TWAI transmission, non-blocking zero-copy frame queues, and distributed reactive signals (`state.signal().can()`, `.urgent()`) are operational in the ESP32-C6 and ESP32-C3 kernel with sub-0.2ms latency over twisted pair wiring.

This guide explains how to connect multiple autonomous FerrumOS nodes over a twisted pair **CAN / TWAI** bus. Inter-board signals react within 0.2 milliseconds even when Wi-Fi, routers, or central servers are down.

---

## 1. Network Topology

```text
 ═════════════════════════════ CAN Bus (Twisted Pair CAN-H / CAN-L, 250 kbps) ═════════════════════════════
          │                                              │                                      │
          ▼                                              ▼                                      ▼
 ┌─────────────────────────┐            ┌─────────────────────────┐            ┌─────────────────────────┐
 │ Node A: Wall Switch     │            │ Node B: Relay Box       │            │ Node C: Gateway         │
 │ (ESP32-C6 / TWAI)       │            │ (ESP32-C6 / TWAI)       │            │ (Wi-Fi + CAN Gateway)   │
 └─────────────────────────┘            └─────────────────────────┘            └─────────────────────────┘
```

Both ends of the physical CAN bus must have a **120 Ohm termination resistor**.

---

## 2. Transmitter Node (Wall Switch)

The transmitter binds a hardware button to a distributed signal topic. The compiler computes the 29-bit CAN arbitration identifier automatically:

<!-- snippet: id="can_bus_setup" category="Шины данных (I2C / SPI)" title="CAN Bus (TWAI) Network" icon="fa-network-wired" desc="Initialize CAN 2.0B bus and bind distributed reactive signal." badges="['CAN 2.0B', 'TWAI']" -->
```javascript
// Configure CAN bus on standard ESP32-C6 pins (TX=21, RX=22)
CAN.bus()
    .pins(21, 22)
    .baud(250000);

// Configure input button on Node A
const btn = GPIO.input(9)
    .pullUp()
    .button()
    .clickMs(350);

// Distributed reactive signal synchronized across all CAN nodes
const light = state.signal("hallway/light", false).can();

while (true) {
    const event = btn.wait();
    if (event === Button.CLICK) {
        // Toggle distributed signal across all nodes on the bus
        light = !light;
    }
}
```

---

## 3. Receiver Node (Relay Actuator)

The receiver listens to the distributed signal and updates its local relay:

```javascript
// Configure CAN bus on Node B
CAN.bus()
    .pins(21, 22)
    .baud(250000);

// Configure relay on Node B
const relay = GPIO.output(12)
    .openDrain(true)
    .pullUp()
    .invert(true)
    .initial(false);

// Listen to distributed CAN signal
const light = state.signal("hallway/light", false).can();
light.watch((on) => {
    relay.write(on);
});
```

---

## 4. Single-Wire Mode (No Transceiver Required)

For ultra-compact or budget devices (e.g. wall switch cups, leak sensors), FerrumOS supports **Single-Wire CAN (SW-CAN)**. In this mode, no external transceiver chip (SN65HVD230 / TJA1050) is needed:

```text
  ESP32-C6 (Node A)                         ESP32-C6 (Node B)
  ┌────────────────┐                       ┌────────────────┐
  │         GPIO21 ├───┬───────────────┬───┤ GPIO21         │
  │                │   │  Single Wire  │   │                │
  │            GND ├───┼───────────────┼───┤ GND            │
  └────────────────┘   │   (1 Wire)    │   └────────────────┘
                     ┌─┴─┐
                     │ R │ (4.7k Pull-Up to 3.3V)
                     └─┬─┘
                      3.3V
```

### Hardware Configuration
- **Line**: 1 data wire between GPIO pins + common GND.
- **Pull-Up**: One 4.7 kOhm resistor connected between the data line and 3.3V.
- **Operating Speed**: 25 kbps (optimal for open-drain bus capacitance up to 20 meters).

<!-- snippet: id="can_single_wire" category="Шины данных (I2C / SPI)" title="Single-Wire CAN (1 провод)" icon="fa-bolt" desc="Однопроводная шина без внешнего трансивера на 25 kbps." badges="['Single-Wire', 'Zero-Transceiver']" -->
```javascript
// Single-wire configuration on GPIO 21 (25 kbps)
CAN.bus()
    .singleWire(21)
    .baud(25000);

// Deterministic explicit ID or sequential assignment
const light = state.signal("hallway/light", false).can(1);
```

### Comparison: Differential vs Single-Wire

| Parameter | Standard CAN (2-Wire) | Single-Wire CAN (1-Wire) |
| :--- | :--- | :--- |
| **Physical Layer** | CAN-H / CAN-L Twisted Pair | 1 Data Wire + Common GND |
| **Transceiver Chip** | Required (SN65HVD230 / TJA1050) | **None** (Built-in Open-Drain GPIO) |
| **Termination** | 120 Ohm resistors at both ends | Single 4.7k Pull-Up to 3.3V |
| **Speed** | 125 kbps – 1 Mbps (default 250 kbps) | 10 kbps – 50 kbps (recommended 25 kbps) |
| **Max Distance** | Up to 1000 meters | Up to 15–20 meters |
| **Typical Use** | Main building backbone | Wall switches, compact junction boxes |

---

## 5. Why This Architecture Wins

1. **Zero Single Point of Failure**: Lights, valves, and alarms react in 0.2 ms regardless of network outages.
2. **Cold-Chip Operation**: Nodes on the CAN bus can shut down Wi-Fi entirely (`WiFi.mode(OFF)`), cutting power consumption to 15 mA and running cool inside electrical cabinets.
3. **Deterministic Arbitration**: Urgent signals (`.urgent()`) use CAN priority 0 to guarantee delivery over telemetry streams during bus load.
