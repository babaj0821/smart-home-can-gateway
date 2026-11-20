# Engineering assumptions, integration boundaries, and known limitations

I documented the following details so other developers can interpret my four
architecture experiments without mistaking the public prototype files for
verified production deployments. I deliberately anonymized selected private
CAN protocol constants and connector mappings; I have **not** reconstructed
private values or inferred hardware-specific addresses.

## Versions and assumptions

| Component | My tested/reference context | What remains environment-specific |
|---|---|---|
| Linux gateway | Orange Pi Zero 3, Linux/Ubuntu Noble experiments | Kernel, board revision, GPIO and SPI mappings |
| CAN interface | MCP2515 on SPI, accessed through SocketCAN `can0` | Transceiver, physical wiring, termination, actual bitrate |
| ThingsBoard Gateway | 3.8.3 used in earlier customized-Gateway work; 3.8.4 in the architecture 03 Compose reference | Patch/API compatibility; image tag is not proof of the modified source file's exact upstream base |
| Python | Python 3.11/3.12 development context | External dependencies and GTK availability |
| Local gRPC | `127.0.0.1:50051`, plaintext local channel | Authenticated, encrypted access if expanding beyond a trusted host |
| Docker ↔ host | Host networking for architecture 03 | Isolation, privileges, bind-mount paths and extension loading |
| ThingsBoard Edge | Local Rule Chain experiments on Orange Pi Zero 3 | A stable Edge + Gateway setup was not achieved there; exports are not bundled |

I encountered a Gateway 3.8.3 issue in which some custom connectors sometimes
disappeared, and I used 3.8.4 in later connector experiments. That observation
does not establish which version of a whole-file Gateway patch is compatible.

## 01 — Parallel SocketCAN

- I replaced application-level CAN protocol constants in
  `canbus/can_protocol.py` with deliberate placeholders, including operation
  bit positions, masks and data indexes. This public version **cannot be used
  for physical device control as-is**.
- The interactive prototype is `test.py`; `main.py` is empty.
- `integrations/thingsboard/tb_bridge_test.py` is not an executable automated
  test: it omits the `scenario_engine` constructor argument.
- The independent MQTT bridge and Gateway can both communicate with the
  server; deployments need a coordinated command and state ownership model.

## 02 — Customized Gateway service

- I provide a modified upstream `tb_gateway_service.py` and my host-side
  application. I do **not** include an independently installable Gateway
  distribution or a second upstream CAN Connector source copy.
- The modified service defines `update_local_data` for the cache, but an
  installed CAN Connector must call this method after successful conversion.
  The stock converter path is not automatically wired to the new method by
  this file alone.
- The Gateway Manager (`/tmp/gateway`) and the scenario service
  (`/tmp/smart_panel`) require shared paths, trustworthy local access and
  **separate secret keys from the environment**. I recommend a dedicated
  directory with restricted permissions rather than a shared world-writable
  `/tmp` mount.
- `multiprocessing` Manager/Listener traffic relies on Python pickle and an
  authentication key, not a safe untrusted-message protocol. Only run the IPC
  endpoints with explicitly trusted peers. Keep raw RPC payloads and device
  telemetry out of debug logs.
- The source is tied to upstream Gateway internals; updating a Gateway image
  without rechecking this patched service can break imports and RPC behavior.

## 03 — Scenario Connector and gRPC

- The FIFO helper at `smart_panel_shared/can_scenario_bridge.py` is a bounded
  in-memory implementation added to match the converter/connector API used in
  this repository. It drops new telemetry when full and provides no durable
  replay after a process restart. Only its unit-level behavior was checked in
  this package.
- The Scenario Connector calls Gateway/CAN Connector implementation APIs. I
  have not verified every API signature against the published image in a live
  Docker/CAN system after packaging.
- Local gRPC uses **insecure transport bound to loopback**. Do not expose port
  50051 on an untrusted interface without authentication and TLS or an
  equivalent protected transport.
- The reference Docker service uses host networking and CAN-related Linux
  capabilities. Apply minimum privileges and inspect the deployment
  environment. MQTT port `1883` is typically plaintext; use protected
  networking or TLS-capable configuration for untrusted paths.
- CAN connector settings are *anonymized examples*; converter expressions and
  field names are not a ready-to-run protocol implementation.
- The sample Gateway JSON files retain `remoteConfiguration: true` from my
  experimental settings. This permits remote configuration management when
  supported by the connected ThingsBoard instance. Disable it when remote
  management is not required, and restrict who can change Gateway settings.

## 04 — ThingsBoard Edge

- I evaluated a Rule Chain–based local scenario design and tested Edge under
  resource constraints. On my Orange Pi Zero 3, Edge plus Gateway did not run
  reliably under the attempted settings. This result is **not** a universal
  conclusion about ThingsBoard Edge on other hardware.
- My Edge Rule Chain exports, deployment settings, and runnable Edge project
  files are **not included**. I do not provide invented alternatives here.

## MCP2515 overlay

- The `config/hardware/mcp2515.dts` example uses `&spi1` with `reg = <1>`,
  while the physical SPI debugging I describe used SPI0. This discrepancy is
  preserved in the source; pinmux, chip-select and IRQ settings must be
  matched to the board and kernel actually in use.
- I also encountered swapped CAN-H/CAN-L wiring. A successful internal CAN
  loopback is not proof of a correct physical bus.

## Scope of validation

The repository contains a limited Python unit test suite and syntax checks.
I have not rerun hardware-in-the-loop CAN tests, outage/recovery scenarios,
Gateway container integration, UI display tests, or Edge resource tests on the
publicly packaged version. The architecture conclusions should be read with
those boundaries in mind.
