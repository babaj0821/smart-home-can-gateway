# CAN Smart Home Gateway — Four Tested Architecture Approaches

**A comparative IoT engineering project exploring four ways to combine CAN devices, ThingsBoard Gateway, and local smart-home automation.**

The central question is not *“Which architecture won?”* It is **“Which architecture fits an organization's requirements, hardware budget, software maintenance model, and operational constraints?”**

During the internship, **four architectures were designed, tried, and evaluated**. Each has different strengths and limitations. The ThingsBoard Edge experiment was also tested, but **could not run stably alongside Gateway on the Orange Pi Zero 3 configuration used**. This outcome is a limitation of the tested environment, not a statement that Edge cannot work on more capable hardware.

> **What is in this GitHub snapshot?** Source material for approaches **01–03**; an evaluation and architectural explanation for **04 — ThingsBoard Edge**, whose implementation/configuration files will be pushed later. These are prototypes and experiments—not four production-certified deployments. The repository is intended to support comparison, learning, adaptation, and independent organizational selection.

## The shared problem

A CAN-based smart home may need to receive telemetry, control devices from ThingsBoard, and execute local scenarios even during a remote-server outage. The internship investigated simplifying an earlier device-to-gateway route that used an intermediate board, while retaining useful local processing.

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
| **[04 — ThingsBoard Edge](architectures/04-thingsboard-edge/README.md)** | Local ThingsBoard Rule Chains perform scenario orchestration; Gateway remains CAN-facing. | Reuses ThingsBoard rule-engine concepts and familiar tooling; avoids a separate bespoke Python Scenario Engine. | Higher runtime resource demand; instability on the tested low-memory board; files pending in this snapshot. | Organizations with sufficient edge hardware and an existing ThingsBoard operating model. |

**Evidence boundary:** these are *qualitative engineering observations*, not rankings from a controlled performance benchmark. Read each architecture's test observations and limitations before adapting it.

➡ **[Detailed trade-off comparison](docs/architecture-comparison.md)** · **[Organization-oriented selection guide](docs/organization-selection-guide.md)**

## Architecture diagrams

Each alternative has its own dedicated README, including diagrams and data flows from the report:

- [01 · Parallel SocketCAN: two independent paths](architectures/01-parallel-socketcan/README.md#architecture-diagram)
- [02 · Gateway-integrated: hooks, local IPC, and RPC](architectures/02-gateway-integrated/README.md#architecture)
- [03 · Scenario Connector: telemetry queue, gRPC, and UI](architectures/03-scenario-connector/README.md#complete-system-architecture)
- [04 · ThingsBoard Edge: local Rule Chain experiment](architectures/04-thingsboard-edge/README.md#conceptual-architecture)

The project uses **Smart Panel** to mean the broader local system, **Local Processor** for the process orchestrating local actions, and **Scenario Engine** for the component that expands named scenarios into device commands. Their locations and interfaces vary by architecture; the UI is not itself the Scenario Engine.

## Repository structure

```text
smart-home-can-gateway/
├── README.md
├── architectures/
│   ├── 01-parallel-socketcan/    # Direct-CAN local processor prototype
│   ├── 02-gateway-integrated/    # Unix IPC and customized Gateway service
│   ├── 03-scenario-connector/    # Connector, gRPC service, GTK4 UI
│   └── 04-thingsboard-edge/      # Experiment/evaluation; source files to follow
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
│   ├── assumptions-and-open-items.md
│   ├── publication-review.md
│   └── diagrams/                 # Figures extracted from the internship report
├── tests/                        # Limited non-hardware checks
└── PUBLISHING.md
```

**Configuration is deliberately centralized in the root [`config/`](config/README.md) directory.** Each architecture keeps its own source and documentation, while deployment templates, Gateway JSON and the hardware overlay live together in appropriately named subdirectories. The Docker Compose bind mounts and README commands have been updated to this layout. Application modules that *read* environment variables remain next to their Python importers.

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

Read the chosen architecture's README and the [Linux CAN / MCP2515 guide](hardware/README.md). All deployment configuration lives under [`config/`](config/README.md). Values such as CAN identifiers, protocol fields, and server settings were **intentionally anonymized** in the supplied material; no original values are restored or inferred here.

A limited repository-level check is available:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q architectures tests
```

These checks **do not** substitute for physical CAN, outage/recovery, ThingsBoard, UI, or ThingsBoard Edge hardware tests. The source code for the Edge experiment is not yet in this repository.

Before publishing publicly, review [publication/redaction notes](docs/publication-review.md), [assumptions and source changes](docs/assumptions-and-open-items.md), and [GitHub publishing instructions](PUBLISHING.md). Some identifiers, organization names, CAN pin mappings, and diagram labels remain visible for manual review. The user-supplied dummy protocol fields are preserved rather than replaced with fabricated values.

**This repository documents four tested approaches so that different organizations can make their own evidence-based architectural choices.**
