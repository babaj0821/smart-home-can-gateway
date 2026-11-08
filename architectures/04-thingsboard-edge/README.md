# Architecture 04 — ThingsBoard Edge and Local Rule Chains

**Tested during the internship; implementation files pending for this repository.** This architecture was not merely a hypothetical diagram: the report describes its scenario-processing design, resource tuning, desktop trials and attempts to run ThingsBoard Edge together with Gateway on an Orange Pi Zero 3. Those board trials **did not reach stable operation**. The fact that source/exported Rule Chains are **not yet pushed here** should not be confused with a claim that the architecture was never tested.

This is **one of four evaluated alternatives**, with benefits and constraints that differ from the Python Local Processor designs. It may suit other organizational environments, particularly when adequate hardware resources and ThingsBoard operational expertise are available. It is not presented as universally better or worse.

[← Main repository](../../README.md) · [Architecture comparison](../../docs/architecture-comparison.md) · [Organizational selection guide](../../docs/organization-selection-guide.md)

## Conceptual architecture

![ThingsBoard Edge with a virtual Scenario Controller, Root and Scenario Engine Rule Chains, and CAN Gateway — figure 3-8 from the internship report](../../docs/diagrams/thingsboard-edge-overview.png)

```text
                           Remote ThingsBoard Server
                                 (when connected)
                                         ^
                                         |
                          Local ThingsBoard Edge
                     +--------------------------------+
                     | Root Rule Chain                |
                     |   |                            |
                     |   +-- Direct device RPC ------+----+
                     |   |                                 |
                     |   +-- Virtual Scenario Controller   |
                     |             |                       |
                     |      Scenario Engine Rule Chain     |
                     |             |                       |
                     |      Per-device RPC ----------------+
                     +-------------------------------------+
                                                           |
                                                ThingsBoard Gateway
                                               CAN Connector/converters
                                                           |
                                                    SocketCAN / can0
                                                           |
                                                    Physical CAN devices
```

Unlike architectures 01–03, named scenario definitions and actions are processed through **ThingsBoard Edge Rule Chains**, rather than a separate Python Scenario Engine. The Gateway keeps responsibility for CAN frames and the device RPC downlink. This is the tested **design intent** from the report, not an exported deployable Edge configuration.

## Scenario execution flow examined in the report

1. Maintain scenario definitions as **server-side attributes** associated with a virtual **Scenario Controller** device; each action specifies target device, RPC method and parameters.
2. A widget or client requests a named scenario such as `night` without transmitting all its implementation details.
3. A **Root Rule Chain** routes direct-device RPC along the ordinary Gateway path, and scenario-related requests to a **Scenario Engine Rule Chain**.
4. The Scenario Engine Rule Chain loads the definition, expands each action into a device-targeted request, changes the originator when necessary, and invokes the RPC Request flow.
5. The Gateway's CAN Connector/downlink converter generates the corresponding CAN frames. Device telemetry flows back through the Gateway to the local ThingsBoard environment and, when available/configured, the central server.

## Engineering evaluation: strengths and limitations

**Strengths**
- Uses **ThingsBoard's native Rule Chain model** for scenario routing, decomposition, and device-specific RPC.
- Avoids a separate bespoke Python Local Processor / Scenario Engine in the intended design.
- Fits an organization that already manages ThingsBoard workflows and can dedicate sufficient resources to an Edge installation.

**Limitations**
- The tested Orange Pi Zero 3 did not have sufficient practical headroom for stable Edge + Gateway + supporting-service operation under the reported tuning attempts.
- The report describes high RAM pressure: an initial ~1.3 GB Edge estimate versus ~700 MB free during testing; a 600 MiB-restricted container used approximately 595 MiB, before all other service demand was accounted for.
- Swap pressure, severe system slowdown, crashes and manual resets occurred in the board experiments, including trials without Docker.
- An organization adopting this design must provision and validate the Edge runtime and its rule-engine operations on actual deployment hardware.

**Organizational fit:** consider this design when **native platform automation is a priority** and a host with adequate RAM/CPU is available. It is not a good assumption for a memory-limited board until a **stable feasibility test** passes. A more resource-constrained deployment may choose to evaluate one of the Python Local Processor alternatives, but no universal ranking is implied.

## Test outcome versus source availability

| Question | Status |
|---|---|
| Was the architecture designed and tried during the internship? | **Yes** — described with Rule Chains, scenario attributes, and Edge installation/resource tests. |
| Did Edge and Gateway run stably together on the tested Orange Pi Zero 3? | **No** — not under the tested hardware and tuning conditions. |
| Are exported Rule Chains, source files, and Edge deployment configs included in this repository? | **Not yet** — will be added in a future push when the actual files are available. |
| Does this rule out Edge for other organizations? | **No** — hardware capacity, operational requirements and platform expertise can differ. |

## Future additions

When the actual experiment files are supplied, this folder can receive Edge Rule Chain exports and related source, while deployment/configuration belongs in a **centralized [`config/04-thingsboard-edge/`](../../config/README.md)** directory. The current repository does **not** invent any filenames, resource profiles, endpoints, credentials or test results beyond the report.

For organizational selection, see the [four-way comparison](../../docs/architecture-comparison.md) and [selection guide](../../docs/organization-selection-guide.md).
