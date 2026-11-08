# Architecture selection guide for organizations

This guide turns the **four evaluated CAN / ThingsBoard local-processing architectures** into an engineering decision process. There is **no default recommendation**: different companies may prioritize direct CAN access, low-cost hardware, maintainability, centralized protocol translation, or native ThingsBoard automation differently.

Start with the [technical comparison](architecture-comparison.md), then fill in this worksheet for your own environment.

## 1. Document your non-negotiable requirements

| Requirement | Questions to answer before choosing |
|---|---|
| Local availability | Which commands and scenarios must work during loss of central ThingsBoard connectivity? What happens if Gateway itself is down? |
| CAN authority | Can two applications transmit on the CAN bus, or must a single gateway service own command encoding and dispatch? |
| Hardware | What RAM/CPU/storage is available after OS, Gateway, database, UI, and other services have started? |
| Software maintenance | Can your team maintain patches to ThingsBoard Gateway core across upgrades? |
| Integration skills | Does your team prefer Python services, Unix IPC, gRPC, or ThingsBoard Rule Chains? |
| Security boundary | Can IPC safely remain local to a trusted host? How will credentials, RPC privileges and filesystem permissions be managed? |
| Operations | Who monitors queues, reconnects after failures, verifies scenario execution, and troubleshoots the CAN bus? |
| Evidence threshold | Which hardware-in-the-loop, load, outage, restart, and upgrade tests are required for acceptance? |

## 2. Match constraints to alternatives

| If the organization prioritizes… | Examine first | Confirm the trade-off |
|---|---|---|
| Direct local bus control with minimal dependence on Gateway's application APIs | **01 — Parallel SocketCAN** | Duplicate CAN decoding and coordination with the Gateway path are acceptable. |
| One canonical CAN converter and a custom managed Gateway distribution | **02 — Gateway-integrated** | The team can maintain core modifications and a trusted shared Unix socket. |
| An independent local application and UI behind a clear communication interface | **03 — Scenario Connector** | Connector API compatibility, queue behavior, and gRPC operations can be managed. |
| Native ThingsBoard Rule Chains and existing platform administration skills | **04 — ThingsBoard Edge** | Sufficient RAM/CPU and an actual stable Edge + Gateway deployment can be demonstrated. |

These are **starting points for evaluation**, not exhaustive rankings or claims of universal superiority.

## 3. Create your own weighted decision matrix

Replace the blank weights/scores with your organization's policy. Suggested scale: **weight 1–5** (importance) and **score 1–5** (how well the *tested implementation on your hardware* meets it). **Do not pre-fill scores from this report**: the four alternatives were not subjected to an identical benchmark.

| Criterion | Weight (1–5) | 01 score | 02 score | 03 score | 04 score | Evidence / acceptance test |
|---|---:|---:|---:|---:|---:|---|
| Local operation during internet outage | — | — | — | — | — | Disconnect central server, run representative scenarios |
| CAN command authority and consistency | — | — | — | — | — | Verify conflicting command paths and device states |
| RAM and CPU fit | — | — | — | — | — | Run on production-target hardware under load |
| Ease of upgrade/maintenance | — | — | — | — | — | Upgrade Gateway and repeat integration test |
| Deployment/operations effort | — | — | — | — | — | Reboot, restart processes, test reconnection |
| Security and local IPC controls | — | — | — | — | — | Verify socket/network permissions and RPC access |
| Team familiarity | — | — | — | — | — | Estimate training and support effort |

After collecting actual measurements, compute `sum(weight × score)` **only as a decision aid**. Record the risk of any *mandatory requirement* that remains unmet even if a total score looks favorable.

## 4. Minimum validation plan

For every candidate seriously considered, run the same controlled tests on target hardware:

1. Check CAN initialization, frame decoding, telemetry and a known-safe device RPC.
2. Run a local multi-device scenario with the remote server available, then unavailable.
3. Restart Gateway and the local processing service independently; verify reconnect, state restoration and duplicated command handling.
4. Record memory, CPU, disk I/O, queue saturation, and end-to-end command timing under a realistic workload.
5. Upgrade the underlying ThingsBoard Gateway/Edge version and measure the integration work required.
6. Review exposure of credentials, Unix sockets, gRPC listeners, remote dashboards, logs, and CAN protocol constants.

**Edge-specific early gate:** the internship's Orange Pi Zero 3 trial did not stabilize with Edge and Gateway running together, so verify memory headroom *before* investing in migration to the native Rule Chain design.

## 5. Decision record template

```text
Organization / deployment:
Target hardware and OS:
Mandatory offline functions:
CAN ownership policy:
Authorized maintenance and upgrade approach:
Architectures tested on our hardware:
Measured results and dates:
Risks and mitigations:
Chosen approach and reasons:
Fallback / revisit conditions:
Decision owner and review date:
```

The project supports **organizational choice**. It does not claim that any one of these four architectures is best for every environment or that the source snapshot represents fully validated production software.
