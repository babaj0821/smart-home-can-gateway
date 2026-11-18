# Assumptions, repository changes, and open items

The user requested a reorganized, GitHub-ready starting point. This document makes explicit which settings and implementation details were **assumed or reconstructed** rather than provided as complete, verified source.

## Working assumptions

| Topic | Working assumption | Why it is reasonable / what to verify |
|---|---|---|
| Linux board | Orange Pi Zero 3 with a suitable Linux distribution, e.g., Ubuntu Noble | Named in the report; verify kernel, GPIO mappings, and actual board revision |
| CAN adapter | MCP2515 over SPI with a Linux `can0` interface | Present in the Device Tree source and report; pin mapping and bus timing are hardware-dependent |
| Gateway software | 3.8.4 for architecture 03; the separately uploaded gateway patch Dockerfile named 3.8.3 | The reason I chose a different version of ThingsBoard Gateway was a problem in 3.8.3 that sometimes deleted the custom connectors, so for the 4th architecture I changed it to 3.8.4.|
| IoT transport | ThingsBoard Gateway communicates with the ThingsBoard server over the configured network/MQTT transport | Based on the report and gateway configuration; your server host, port, and credentials are not in the public repository |
| Smart Panel RPC | gRPC on host loopback `127.0.0.1:50051` | Present in both the original server code and Scenario Connector config |
| Host/container routing | Linux Docker host networking for the gateway container | The supplied code uses host loopback for gRPC; the reorganized Compose file retains `network_mode: host` |
| Python | Python 3.11 or 3.12 is a reasonable development target | Archived Python bytecode was for 3.11/3.12; final environment still needs testing |
| Device-specific CAN messages | **Intentionally anonymized / not guessed** | The user explicitly replaced device-specific values with placeholders; preserve redactions rather than inventing protocol mappings |
| ThingsBoard Edge | **Tested during internship; source to be uploaded later** | The report describes the Rule Chain implementation idea and unsuccessful stability trials on Orange Pi Zero 3; no runnable Edge implementation files are supplied in this public snapshot |

## Changes made to the supplied code tree

1. Renamed the misspelled top-level directories to `01-parallel-socketcan`, `02-gateway-integrated`, and `03-scenario-connector`, keeping their internal module layouts to avoid breaking imports.
2. Removed `__pycache__` directories and compiled Python files; added a root `.gitignore`.
3. Extracted original architecture figures from the report and placed them under `docs/diagrams/` with meaningful English filenames.
4. Moved non-identifying example scenarios to `examples/scenarios.json` within each implementation. Runtime scenario databases and the writable device registry are **not tracked**; each corresponding storage class can initialize missing files.
5. Removed hard-coded ThingsBoard device tokens from the parallel MQTT configuration and architecture 03 Docker Compose reference; supplied `.env.example` templates. The uploader reports that token-like strings were anonymized; rotate any credential that was actually deployed or exposed.
6. Replaced hard-coded Unix-socket authentication keys in the gateway-integrated host code with required `GATEWAY_AUTHKEY` and `SMART_PANEL_AUTHKEY` environment variables. Also replaced two literal IPC keys in the newly supplied `gateway_patch/tb_gateway_service.py` with matching environment lookups. Their remote peers must use identical private keys.
7. Repaired a Python syntax error in `01-parallel-socketcan/canbus/can_interface.py` and changed its basic classic CAN frame representation to the standard Linux `struct can_frame` layout (`=IB3x8s`). **No project-specific CAN payload format was invented.**
8. Added `03-scenario-connector/smart_panel_shared/can_scenario_bridge.py`, which was **missing from the supplied archive** but imported by its converter and Scenario Connector. The added implementation is a bounded, in-process FIFO queue matching the existing `push_telemetry`, `get_telemetry`, and `telemetry_qsize` calls. It is new/reconstructed code, not an assertion about the missing original.
9. Updated the sample Docker Compose source mounts for the provided CAN converter, Scenario Connector and shared helper folders; added `requirements-host.txt` and one queue-only unit test. The Compose file now lives at root `config/03-scenario-connector/docker-compose.yml`.
10. Added **only** `gateway_patch/tb_gateway_service.py` from the newly supplied `thingsboard-gateway.zip` into architecture 02, preserving its upstream copyright header and bundling a file-scoped Apache-2.0 license copy. No upstream backup versions, `can_connector.py`, patch scripts, bytecode, or Dockerfile were included.

11. Documented **architecture 04**, including the report's real ThingsBoard Edge experimentation and unstable Orange Pi Zero 3 result. The source/configuration files have not been supplied and were not invented.
12. **Centralized deployment configuration under root `config/`**: architecture-specific `.env.example` files, architecture 03 Gateway JSON/statistics and Compose template, and the MCP2515 Device Tree overlay. Adjusted documentation commands and Compose bind mounts to the new locations.
13. Reframed the project as a comparison of **four tested architectures with distinct organizational trade-offs**, not as a single universally best design. See [Comparison](architecture-comparison.md) and [Organizational selection guide](organization-selection-guide.md).

The user confirmed that device protocol constants, identifiers and configuration values in the supplied source were intentionally anonymized. Treat them as **redactions**, not proof of an implementation gap in the original environment. This public package does not restore private values.

See [Publication and redaction review](publication-review.md) for the concrete remaining identifiers and static security checks.

The repository documents **four tested architectural approaches** with different strengths and limitations. Only **three** have implementation files in this public archive. The Edge evaluation is preserved even though its files are still to be pushed; lack of repository source does not mean lack of internship testing. There is no universal architecture recommendation—organizations should choose according to their requirements.

## Known functional limitations

### Parallel SocketCAN

- `canbus/can_protocol.py` contains **intentional redactions** (`"decided"`, `"OPERATION_BIT"`, `"DEVICE_ID_MASK"`, text bounds, and `"index"` values). The original values were hidden intentionally; use the private device specification to configure them before running `test.py` against any CAN bus.
- `main.py` is empty in the supplied archive; the actual prototype is in `test.py`.
- `integrations/thingsboard/tb_bridge_test.py` constructs `ScenarioBridge()` without the `scenario_engine` argument required by its constructor. It was left unchanged and should not be presented as a working integration test.
- The parallel path uses an independent ThingsBoard MQTT bridge; this is a design issue, not just a documentation issue.

### Gateway-integrated local processing

- The newly supplied **modified `tb_gateway_service.py` is now included** alongside the host client and scenario service. It exposes the cache updater, manager and local RPC path. The extra `CAN Connector` call into `update_local_data` is not present in that file and must still be wired in the installed gateway; the upstream CAN connector source was intentionally not duplicated.
- `/tmp/gateway` is served by the supplied modified `tb_gateway_service.py` when `managerEnabled` is enabled; the host and container must share the socket and `GATEWAY_AUTHKEY`, and the module must match the deployed upstream ThingsBoard Gateway version.
- The host-side scenario service also opens `/tmp/smart_panel`. Its peer protocol and deployment are not fully documented in the provided code.
- The host-side code uses Python object proxies, which require special attention to trust boundaries and matching Python/runtime assumptions.

### Scenario Connector

- The in-process queue helper is reconstructed, not hardware-tested. It uses bounded memory and **drops a new telemetry message if the queue is full**. The caller logs whether it was enqueued, but no persistence/replay mechanism was added.
- The Scenario Connector implementation accesses APIs on the original CAN Connector. API signatures and implementation details may differ across ThingsBoard Gateway versions, even when the core Gateway class itself is not patched.
- The local gRPC server uses **insecure gRPC** on loopback, and the UI has no direct CAN access. Do not expose `50051` beyond a trusted local system without proper security controls.
- The default converter configuration contains device-specific identifiers, typos, and generic expression fields inherited from the original project. Review [`../config/03-scenario-connector/gateway/padnaCanGateway.json`](../config/03-scenario-connector/gateway/padnaCanGateway.json) against physical devices instead of assuming its placeholders are validated examples.
- The Compose mounts have been aligned with the archive structure, but no live Docker, MQTT, GTK4, or CAN hardware end-to-end test has been completed in this workspace.

### ThingsBoard Edge (tested; source files pending)

- No Edge code, exported Rule Chains, or configuration was supplied yet. Its README is a report-based outline, not an install guide.
- The tested Orange Pi Zero 3 deployment was not stable when running Edge and Gateway together; this is a hardware-and-configuration-specific observation, not a general performance benchmark.
- Future Edge documentation must be updated from the actual pushed files, not assumed from the concept.

### MCP2515 overlay

- The supplied overlay targets `&spi1` and uses `reg = <1>`, while the report's troubleshooting narrative describes the physical controller as connected to **SPI0** and conflicts on Armbian. The mismatch is preserved rather than silently corrected. Verify against the exact kernel Device Tree and wiring.
- The original overlay includes an interrupt comment that conflicts with its numeric interrupt flags. Check the board's pin controller binding and edge polarity before deploying.
- CAN bitrate, transceiver wiring, and termination values must match the actual equipment. They cannot be inferred safely from the archive.

## Before making the repository public

- The uploader says token-like fields were intentionally anonymized. Values cannot be verified as live or dummy from source alone; rotate credentials **if they were actually used and exposed**, and keep all real tokens out of Git.
- Confirm you have permission to publish code and diagrams developed in a company internship; avoid publishing proprietary device protocol details without authorization.
- Choose a LICENSE file only after confirming rights; none was created automatically.
- Review the actual commit history before publishing and check for `.env`, backup files, generated datasets, logs, and device credentials.
- Run realistic SocketCAN/ThingsBoard/gRPC tests on your intended Linux host and hardware before describing the project as production-ready.
