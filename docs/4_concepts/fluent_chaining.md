# Fluent Chaining Standard

In FerrumOS, all peripheral initialization and hardware pin configuration strictly follow the **Fluent Chaining (Method Chaining)** pattern.

```javascript
// Atomic output configuration
const relay = GPIO.output(15)
    .openDrain(true)
    .pullUp()
    .invert(true)
    .initial(false);
```

---

## ⚡ The Problem with Imperative Mutation

In conventional embedded frameworks, developers frequently configure pins imperatively line-by-line:

```javascript
// ❌ FORBIDDEN in FerrumOS - Leads to hardware glitches
const relay = GPIO.output(15);
relay.open_drain = true;    // Re-configures register
relay.pull_up = true;       // Re-configures register again
relay.initial = false;      // Glitch! Pin may float momentarily
```

### Why Imperative Setup is Dangerous:
1. **Hardware Pin Glitches**: During multi-step register writes, a pin may momentarily enter an undefined floating state or output an unintended pulse. This can inadvertently trigger sensitive relays, MOSFET gates, or latching circuits.
2. **Multiple CPU / Register Traps**: Each assignment generates a separate runtime trap and hardware register read-modify-write cycle.
3. **Partial Initialization Bugs**: If an exception occurs halfway through configuration, the hardware is left in an inconsistent half-initialized state.

---

## 🛡️ Atomic Initialization via Fluent Chaining

FerrumOS eliminates hardware glitches by treating chained calls as an atomic hardware specification.

When you chain methods:
1. Each chained call (`.openDrain()`, `.pullUp()`, `.invert()`, `.initial()`) mutates an internal immutable descriptor structure in registers.
2. The final hardware registers on the RISC-V SoC are committed **in a single atomic write cycle**.
3. Pins transition from safe high-impedance mode directly into their desired state without glitching.

---

## 📐 Fluent Chaining Rules

1. **Chain Everything at Declaration**:
   Always configure modes, resistors, inversion, and initial states in a single statement.
2. **No Config Objects**:
   Do not pass dictionary objects (e.g. `{ openDrain: true }`). Method chaining provides full TypeScript/JavaScript autocomplete and compile-time type verification.
3. **Immutable Hardware Binding**:
   Once initialized, hardware bindings cannot be redefined imperatively. To alter mode dynamically, declare a new handle or re-bind atomically.
