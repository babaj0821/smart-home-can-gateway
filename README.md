# CAN Smart Home Gateway — Four Tested Architecture Approaches

**My comparative IoT engineering project exploring four ways to combine CAN devices, ThingsBoard Gateway, and local smart-home automation.**

The central question is not *“Which architecture won?”* It is **“Which architecture fits an organization's requirements, hardware budget, software maintenance model, and operational constraints?”**

During my internship, **I designed, implemented or configured, tested, and evaluated four architecture approaches**. Each has different strengths and limitations. I also trialed ThingsBoard Edge, but **I could not get Edge and Gateway to run stably together on my Orange Pi Zero 3 test setup**. This is a limitation of my tested environment, not evidence that Edge cannot work on more capable hardware.

> **Repository scope:** I include prototype source for approaches **01–03** and my design and evaluation of **04 — ThingsBoard Edge**. The Edge Rule Chain exports and deployment configuration are **not included**. These are experimental implementations and observations, not four production-certified deployments. I share them so others can compare the trade-offs and adapt the ideas to their own constraints.

## The shared problem

A CAN-based smart home may need to receive telemetry, control devices from ThingsBoard, and execute local scenarios even during a remote-server outage. In this project, I investigated simplifying an earlier device-to-gateway route that used an intermediate board, while preserving useful local processing.

Across the alternatives, the main responsibilities are:

- **CAN communication:** send and receive frames through Linux SocketCAN and the gateway's CAN Connector.
- **Telemetry and RPC:** translate device data into ThingsBoard-friendly events and convert commands back to CAN frames.
- **Local automation:** interpret a named scenario such as *Night* into actions for individual devices.
- **Operations and UI:** expose status, configuration, and control without assuming permanent access to the cloud.

The four architectures distribute these responsibilities differently. They are **alternatives**, not four services that should all run together.

## Four architectures at a glance

| Approach | Main idea | Strengths | Trade-offs | Relevant organizational priorities |
|---|---|---|---|---|
| **[01 — Parallel SocketCAN](architectures/01-parallel-socketcan/README.md)** | Gateway and Local Processor use separate sockets on the same `can0` interface. | Independent local CAN control; light processing path; minimal need to customize Gateway internals. | CAN decoding and server-facing logic may be duplicated; parallel device-control paths are harder to coordinate. | Direct bus access, independent local control, simple lightweight hosts. |
| **[02 — Gateway-integrated](architectures/02-gateway-integrated/README.md)** | Gateway exposes decoded state and local RPC access over a Unix-domain socket. | One CAN conversion path; high-level API for the Local Processor; reuses Gateway downlink. | Changes to Gateway core/handlers; upgrade/maintenance burden; shared-socket deployment complexity. | Centralized device access and willingness to maintain a customized Gateway. |
| **[03 — Scenario Connector + gRPC](architectures/03-scenario-connector/README.md)** | A dedicated Gateway connector bridges converted telemetry and local commands to a host-side service. | Clear separation of responsibilities; no direct CAN dependency in local logic; reuses CAN Connector RPC. | More processes/IPC, gRPC and queue lifecycle management; connector API/version dependencies. | Modular integration, local services, separate UI and scenario logic. |
| **[04 — ThingsBoard Edge](architectures/04-thingsboard-edge/README.md)** | Local ThingsBoard Rule Chains perform scenario orchestration; Gateway remains CAN-facing. | Reuses ThingsBoard rule-engine concepts and familiar tooling; avoids a separate bespoke Python Scenario Engine. | Higher runtime resource demand; instability on my tested low-memory board; Edge exports are not included. | Organizations with sufficient edge hardware and an existing ThingsBoard operating model. |

**Evidence boundary:** my conclusions are *qualitative engineering observations*, not a controlled performance benchmark or a universal ranking. Each architecture README explains what I tested and what remains unverified.

➡ **[Detailed trade-off comparison](docs/architecture-comparison.md)** · **[Organization-oriented selection guide](docs/organization-selection-guide.md)**

## Architecture diagrams

Each alternative has its own dedicated README, including diagrams and data flows I developed during the evaluation:

- [01 · Parallel SocketCAN: two independent paths](architectures/01-parallel-socketcan/README.md#architecture-diagram)
- [02 · Gateway-integrated: hooks, local IPC, and RPC](architectures/02-gateway-integrated/README.md#architecture)
- [03 · Scenario Connector: telemetry queue, gRPC, and UI](architectures/03-scenario-connector/README.md#complete-system-architecture)
- [04 · ThingsBoard Edge: local Rule Chain experiment](architectures/04-thingsboard-edge/README.md#conceptual-architecture)

The project uses **Smart Panel** to mean the broader local system, **Local Processor** for the process orchestrating local actions, and **Scenario Engine** for the component that expands named scenarios into device commands. Their locations and interfaces vary by architecture; the UI is not itself the Scenario Engine.

## Repository structure

```text
smart-home-can-gateway/
├── README.md
├── LICENSE                       # MIT terms for project-authored files
├── architectures/
│   ├── 01-parallel-socketcan/    # Direct-CAN local processor prototype
│   ├── 02-gateway-integrated/    # Unix IPC and customized Gateway service
│   ├── 03-scenario-connector/    # Connector, gRPC service, GTK4 UI
│   └── 04-thingsboard-edge/      # Edge design and evaluation (no deployable exports)
├── config/                       # Shared root for deployment configuration
│   ├── README.md                 # Configuration map and usage instructions
│   ├── 01-parallel-socketcan/    # Environment template
│   ├── 02-gateway-integrated/    # Environment template
│   ├── 03-scenario-connector/    # Compose, environment template, Gateway JSON
│   │   └── gateway/              # ThingsBoard Gateway connector settings
│   └── hardware/                 # MCP2515 Device Tree overlay source
├── hardware/                     # CAN/SPI/SocketCAN setup documentation
├── docs/
│   ├── architecture-comparison.md
│   ├── organization-selection-guide.md
│   ├── engineering-notes.md
│   └── diagrams/                 # Architecture figures from my evaluation
├── tests/                        # Limited non-hardware checks
└── NOTICE                        # Third-party source attribution
```

**I keep deployment configuration centralized in the root [`config/`](config/README.md) directory.** Each architecture keeps its own source and documentation, while deployment templates, Gateway JSON and the hardware overlay live together in appropriately named subdirectories. I aligned the Docker Compose bind mounts and setup instructions with this layout. Application modules that *read* environment variables remain next to their Python importers.

## How to evaluate an architecture for your organization

Start with your **constraints**, not a preset winner:

1. **Hardware resources:** Can the target host support ThingsBoard Edge and Gateway simultaneously? Do you have RAM/CPU budget beyond an Orange Pi Zero 3-class environment?
2. **CAN ownership:** Is independent direct bus access desirable, or must all commands pass through a single Gateway-controlled path?
3. **Maintenance:** Is it acceptable to patch upstream Gateway code, or would a connector-based extension be preferable?
4. **Local services:** Is the team comfortable operating gRPC, Docker-to-host networking, and queues?
5. **Existing platform skills:** Would native ThingsBoard Rule Chains be easier to maintain than custom Python scenario logic?
6. **Availability and test coverage:** Which functions must continue offline, and what failure/recovery tests will be required before release?

Use the [selection guide](docs/organization-selection-guide.md) to weight these questions according to your own requirements. The diagrams show different architectural possibilities—not a claim that one design dominates every other design.

## Getting started and validation

Read the chosen architecture's README and the [Linux CAN / MCP2515 guide](hardware/README.md). All deployment configuration lives under [`config/`](config/README.md). I deliberately replaced some private CAN protocol values and service settings with placeholders. The public examples are **not** complete physical-device configurations; restoring them requires the appropriate private device specification.

A limited repository-level check is available:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q architectures tests
```

These checks **do not** substitute for physical CAN, outage/recovery, ThingsBoard, UI, or ThingsBoard Edge hardware tests. The source code for the Edge experiment is not yet in this repository.

For reproducibility constraints, security boundaries, and integration gaps, see my [engineering notes](docs/engineering-notes.md). I have kept the intentionally abstract CAN mappings intact instead of inventing device protocol values. The diagrams illustrate my architecture evaluation and are not substitutes for wiring validation.

## Licensing and attribution

My original project source and documentation are provided under the repository [MIT license](LICENSE), subject to any underlying third-party rights. **The modified ThingsBoard Gateway service is an exception:** it retains ThingsBoard's copyright, remains governed by **Apache License 2.0**, and includes a copy of that license in its [source folder](architectures/02-gateway-integrated/gateway_patch/LICENSE-APACHE-2.0.txt). I document the upstream attribution and my modifications in the [NOTICE](NOTICE) file. This project is independent of ThingsBoard and does not redistribute ThingsBoard Server or Edge source.

**I share four evaluated approaches to help other teams make evidence-based architecture choices rather than claim one design is universally best.**
