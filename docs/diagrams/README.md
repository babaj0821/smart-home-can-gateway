# Architecture figure index

I included the architecture figures from my own internship evaluation to explain the four designs. I use English filenames for navigation. These are **conceptual engineering diagrams**, not independently verified physical wiring diagrams or measured simulation results.

| File | Figure in my original evaluation | What it illustrates |
|---|---|---|
| [`linux-can-stack.png`](linux-can-stack.png) | Figure 3-1 | CAN network → MCP2515 → SPI/kernel → SocketCAN → gateway |
| [`parallel-socketcan-overview.png`](parallel-socketcan-overview.png) | Figure 3-3 | Layered Local Processor with independent CAN path and MQTT integration |
| [`parallel-socketcan-duplicate-paths.png`](parallel-socketcan-duplicate-paths.png) | Figure 3-4 | Duplicate gateway/local-processor communication paths |
| [`gateway-integrated-overview.png`](gateway-integrated-overview.png) | Figure 3-7 | Gateway telemetry hook, local Unix socket, RPC path |
| [`thingsboard-edge-overview.png`](thingsboard-edge-overview.png) | Figure 3-8 | ThingsBoard Edge local Rule Chains, virtual Scenario Controller, Gateway and CAN devices |
| [`scenario-connector-grpc.png`](scenario-connector-grpc.png) | Figure 3-9 | Gateway container and host Local Processor communicating via gRPC |
| [`scenario-telemetry-event-bus.png`](scenario-telemetry-event-bus.png) | Figure 3-10 | First telemetry forwarding prototype using an Event Bus |
| [`scenario-telemetry-queue.png`](scenario-telemetry-queue.png) | Figure 3-11 | Refined telemetry path with a direct queue |
| [`scenario-rpc-event-bus.png`](scenario-rpc-event-bus.png) | Figure 3-12 | First local RPC approach using a custom CAN connector |
| [`scenario-rpc-native-gateway.png`](scenario-rpc-native-gateway.png) | Figure 3-13 | Refined local RPC route through the original CAN Connector |
| [`scenario-connector-complete.png`](scenario-connector-complete.png) | Figure 3-14 | Complete Scenario Connector design including GTK4 UI and gRPC (one of four evaluated approaches) |

I use these figures to document architecture choices; deployment still requires checking real CAN wiring, interface versions, and host resources.
