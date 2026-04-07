---
name: clock-systems
description: Physical clocks, Lamport timestamps, vector clocks, Hybrid Logical Clocks, server-assigned monotonic versions for distributed sync
artifact: guidelines/database-design/clock-systems.md
version: 1.0.0
---

## Worker Focus
The worker evaluates clock system selection and justification, understanding limitations of physical clocks, when to use Lamport timestamps, vector clocks, Hybrid Logical Clocks, or server-assigned monotonic versions based on the sync architecture (peer-to-peer vs client-server).

## Verify
- Clock system chosen and justified for the architecture
- Limitations of physical clocks acknowledged (skew, leap seconds)
- HLC preferred and implemented for peer-to-peer or multi-device scenarios
- Server-assigned monotonic versions used for client-server (simpler, no clock skew)
- Clock implementation format specified (e.g., 64-bit for HLC: 32-bit counter + 32-bit clock ID)
- Clock synchronization or drift tolerance documented
