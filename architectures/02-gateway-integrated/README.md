# Architecture 02 — Gateway-Integrated Local Processing

This **tested architecture alternative** retains **ThingsBoard Gateway as the only process that accesses the physical CAN network**. A separate host-side **Local Processor** obtains high-level device state and sends commands through the gateway rather than opening a second SocketCAN socket. The architecture adds a Unix-domain-socket IPC interface and integrates local commands with the existing gateway RPC pipeline.

> **Source status:** The host-side source from `internship.zip` and the **customized gateway service file supplied separately** are included. The provided gateway service is not an entire ThingsBoard installation. Its telemetry cache also requires a small call from the CAN connector, described below. Hardware and end-to-end compatibility have not been tested in this repackaging.

[← Main repository](../../README.md) · [Architecture comparison](../../docs/architecture-comparison.md) · [Publication review](../../docs/publication-review.md)

## Architecture

![Gateway-integrated CAN, telemetry, Unix socket and RPC flow](../../docs/diagrams/gateway-integrated-overview.png)

```text
          Physical CAN devices
                  |
              CAN / can0
                  |
    ThingsBoard Gateway (Docker)
         |                 |
  CAN Connector       MQTT / ThingsBoard
         |
    CAN converters
         |
   Converted telemetry / local RPC handling
         |
  GatewayManager over /tmp/gateway (Unix socket)
         |
  Local Processor (host)
         |-- Device Manager / state cache
         |-- Scenario Engine + JSON scenario storage
         `-- Terminal UI and scenario command service
```

**The key distinction from architecture 01:** the local application no longer interprets raw CAN frames or duplicates their conversion. It uses gateway-level concepts such as device name, state and RPC method.

## Source code included

| File or directory | Responsibility |
|---|---|
| [`gateway_patch/tb_gateway_service.py`](gateway_patch/tb_gateway_service.py) | **Modified upstream ThingsBoard Gateway service** with a `GatewayManager`, exposed local device APIs, `send_local_rpc(...)`, device-state cache, and scenario-command forwarding. This is the only source file taken from the new `thingsboard-gateway.zip`. |
| [`gateway/gateway_client.py`](gateway/gateway_client.py) | Connects to the gateway's manager proxy at a shared Unix socket and calls `get_local_devices`, `get_device_data`, `get_available_connectors`, and `send_local_rpc`. |
| [`devices/`](devices/) | Device models and a Device Manager that use the gateway client. |
| [`scenario/scenario_engine.py`](scenario/scenario_engine.py) | Translates a named scenario into device commands. |
| [`scenario/scenario_storage.py`](scenario/scenario_storage.py) | Scenario JSON persistence. |
| [`scenario/scenario_rpc_server.py`](scenario/scenario_rpc_server.py) | A second IPC endpoint for scenario-management requests (`/tmp/smart_panel`). |
| [`terminal/`](terminal/) | Host-side local terminal interface. |
| [`examples/scenarios.json`](examples/scenarios.json) | Sanitized example scenarios, **not real deployment data**. |

The gateway file is based on **ThingsBoard upstream code** and retains its Apache-2.0 header. The bundled [Apache-2.0 license](gateway_patch/LICENSE-APACHE-2.0.txt) applies to that modified upstream file, **not automatically to all other project files**. Avoid copying the entire upstream distribution into this repository. All other files in this repository are original work, licensed under <MIT / Apache-2.0>; see `LICENSE`.

## Data and command paths

### 1. CAN telemetry to the Local Processor

1. A CAN frame reaches the Gateway's original CAN Connector.
2. The connector's Uplink Converter decodes the frame into ThingsBoard-style converted data.
3. The Gateway exposes **`update_local_data(converted_data)`**, which stores the latest telemetry and attributes by device name.
4. A host-side `GatewayClient` reads device state using **`get_device_data(device_name)`**; device management and scenarios work on structured data, not raw CAN frames.
5. The normal gateway uplink to ThingsBoard continues separately.

**Important integration detail:** In the supplied gateway service, `update_local_data` is **defined but not called inside `tb_gateway_service.py`**. The separate source ZIP also included an upstream `can_connector.py` with a call to `self.__gateway.update_local_data(new_data)` before `send_to_storage(...)`. Per the request to keep only the relevant gateway file, that entire upstream connector is **not republished here**. When integrating, confirm your installed CAN connector calls the cache updater after conversion; otherwise the Local Processor's state cache will remain empty. This is an upstream-version-specific integration step, not a missing secret value.

### 2. Local RPC to CAN device

1. The Scenario Engine expands a high-level request (e.g., *Night*) into per-device methods and parameters.
2. The host-side `GatewayClient` calls `send_local_rpc(content)` via the Gateway manager.
3. The modified Gateway queues the command in its normal RPC-to-device pipeline.
4. The existing CAN Connector's server-side RPC handler and Downlink Converter build the required CAN command.

The same gateway service file also contains code to forward `getScenarios`, `runScenario`, and related methods to the optional scenario IPC service on `/tmp/smart_panel`. These are experimental additions in the supplied snapshot; do not assume they exist in stock upstream releases.

## Two local IPC channels

| Channel | Default shared path | Direction | Environment key |
|---|---|---|---|
| Gateway manager | `/tmp/gateway` | Local Processor → Gateway API | `GATEWAY_AUTHKEY` |
| Scenario command listener | `/tmp/smart_panel` | Gateway → Local Processor's scenario service | `SMART_PANEL_AUTHKEY` |

The gateway runs in a container and the Local Processor runs on the Linux host. A Unix socket path **must refer to the same shared filesystem location** in both processes (the report used a `/tmp` bind mount). For a hardened environment, use a dedicated shared directory with minimal permissions, rather than mounting all of `/tmp`.

The uploaded upstream-derived service had **literal IPC authentication values** in the source. In this public-ready version, both have been replaced with **mandatory environment variables** matching the sanitized host client. No credential values have been guessed or restored. The socket-path environment variables are optional overrides; deployment permissions and socket cleanup still need validation.

## Running a compatible installation

**Prerequisites:** a ThingsBoard Gateway version compatible with this customized `tb_gateway_service.py`; a working Linux `can0`; suitable CAN Connector and converters; Docker or an equivalent process environment; Python for the host client; and shared Unix-socket paths.

The source archive's Gateway Dockerfile referred to **`thingsboard/tb-gateway:3.8.3`**. The Scenario Connector experiment uses **3.8.4**. This does **not** prove that replacing the gateway service in either version is safe without review. Check the complete upstream module dependencies and test with a matching image before modifying a deployment.

For the host-side environment:

```bash
cd architectures/02-gateway-integrated
cp ../../config/02-gateway-integrated/.env.example .env
# Put UNIQUE, private IPC keys in .env; use the same values inside the Gateway container.
set -a; . ./.env; set +a
# Only after your patched Gateway manager is available on the shared Unix socket:
python3 main.py
```

If the separate scenario management service is required:

```bash
set -a; . ./.env; set +a
python3 -m scenario.scenario_rpc_server
```

The Gateway container must receive `GATEWAY_AUTHKEY` and `SMART_PANEL_AUTHKEY` too (e.g., via its own non-committed environment file or Compose `environment:` mapping), and must share the Unix socket locations. **Simply copying this file into a repository does not install the patch in a running ThingsBoard Gateway.** Review the upstream module location, version, dependencies, and CAN-telemetry hook before deployment.

To use the example scenario storage, copy the sanitized fixture to `scenario/data.json`. Runtime storage files are ignored by Git.

## Engineering evaluation: strengths and limitations

**What was tested in the internship:** exposing processed telemetry to local logic, injecting local device RPC into Gateway's usual downlink path, and using Unix-domain-socket IPC between the Dockerized Gateway and the host Local Processor.

**Strengths**
- Centralizes CAN decoding and command conversion in a single Gateway-controlled pipeline.
- Allows the Local Processor to work with device states and RPC abstractions rather than raw CAN frames.
- Reuses the existing CAN Connector for actual device communication.

**Limitations**
- Telemetry hooks, the local manager interface and RPC handling depend on customized upstream Gateway code.
- Those changes must be maintained and rechecked when Gateway versions change.
- Host/container IPC requires explicit shared-socket paths, permissions and authentication.

**Organizational fit:** consider this approach if a team values a **single CAN authority** and is willing to maintain its own customized ThingsBoard Gateway distribution. Teams that need to avoid changing Gateway core code may prefer to investigate [03 — Scenario Connector](../03-scenario-connector/README.md); organizations with stronger native ThingsBoard expertise should also compare [04 — Edge](../04-thingsboard-edge/README.md).

## Boundaries and cautions

- CAN payloads/IDs masked elsewhere in the source are **intentional example/redaction values**; do not substitute plausible numeric guesses and do not use unverified commands on physical actuators.
- The gateway source includes a debug `print` of the live local telemetry cache. That is not a committed credential, but may reveal device states in deployment logs; remove or redact it in production.
- Manager proxies use Python serialization and are suitable only for **trusted local peers**. Preserve UNIX file permissions and protect the IPC keys.
- This is a customized upstream module, not a self-contained or tested fork of ThingsBoard Gateway. Only `tb_gateway_service.py` from the new archive was included; backups, connector copies, bytecode, Dockerfile and patch utilities were deliberately excluded.

See [Source redaction and publication review](../../docs/publication-review.md) before publishing.
