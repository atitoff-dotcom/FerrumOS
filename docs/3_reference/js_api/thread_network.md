# Thread & 802.15.4 Network Reference

`Status: 🔵 Preview / RFC` • `Target: ESP32-C6 (802.15.4)` • `Milestone: Roadmap Phase 9`

> [!NOTE]
> The Thread mesh and Matter-over-Thread stack is currently in architectural design. Low-level radio arbitration and policies are specified in [Radio Architecture](../../rfcs/0007-brokerless-decentralized-fabric.md).

The `Thread` module provides native IPv6 mesh networking over IEEE 802.15.4 radio for low-power sensors and Matter ecosystems.

---

## Sending Telemetry Frames: `Thread.endpoint(uri)`

```javascript
Thread.endpoint("coap://[fd00::1]/sensors/climate")
    .confirmable(false)
    .payload({ temp: 22.5, humidity: 45 })
    .send();
```

### Chained Configuration Methods
- `.confirmable(enabled: boolean)` — Sets whether CoAP CON (Confirmable / requires ACK) or NON (Non-confirmable) mode is used. For battery conservation, use `false`.
- `.payload(data: object | string | number[])` — Encodes payload as compact JSON/CBOR.
- `.timeoutMs(ms: number)` — Sets transmission response timeout.
- `.send(): boolean` — Transmits frame to parent router via 6LoWPAN.
