# Public repository review: anonymized values and residual identifiers

This note records a **static, best-effort review** of the supplied archives and the repackaged text/source files. It does **not** prove that every diagram, generated file, runtime database, local Git commit or external service is free of sensitive information. No live credentials were tested.

## Explicitly anonymized / illustrative fields (not evidence of missing original work)

- Architecture 01 `canbus/can_protocol.py`: names such as `OPERATION_BIT`, `DEVICE_ID_MASK`, fake bounds and indexes are **deliberate redactions** of the private CAN device protocol. They make this public copy nonfunctional for physical CAN control **by design**. Do not replace them with unverified numeric guesses.
- Root `config/03-scenario-connector/gateway/tb_gateway.json`: its ThingsBoard host and `security.accessToken` use placeholder text, not a production connection. The Compose sample expects user-supplied values via `.env`.
- Root `config/03-scenario-connector/gateway/padnaCanGateway.json`: mappings like `nodeId`, `command`, `value`, `len`, `dataExpression`, and `xx` are illustrative/anonymized. The actual private CAN protocol and converter expressions are not provided.
- The `.env.example` files now live under root `config/` and contain illustrative variable names and template values; loopback `127.0.0.1` is not a public server IP.

## Items that remain visible and may warrant manual review

| Location | Visible data | Sensitivity / action |
|---|---|---|
| `config/03-scenario-connector/gateway/{padnaCanGateway.json,scenarioConnector.json}` | **UUID-shaped connector IDs** | Not passwords, but may be original installation IDs; replace them with newly generated sample IDs if they were copied from an actual deployment. |
| `config/03-scenario-connector/gateway/{tb_gateway.json,padnaCanGateway.json,scenarioConnector.json}`, some Python names, and architecture figures | **PADNA** branding/device naming | Organization/product naming, not credentials. If employer anonymity or disclosure rights matter, rename these references and review diagram **pixels** as well. |
| `config/hardware/mcp2515.dts`, architecture 01 `devices/` and `test.py` | **Board model, SPI/GPIO mapping, and example CAN IDs / registers** | Technical implementation details; the values may be redacted, but source alone cannot prove they are synthetic. Review if hardware/protocol specifics must remain private. |
| `architectures/02-gateway-integrated/gateway_patch/tb_gateway_service.py` | Gateway-side IPC code, paths, debug telemetry-cache printing | Hard-coded keys from the uploaded file were replaced with required environment variables. **The debug print can reveal device state in runtime logs** and should be disabled in a production deployment. |
| `docs/diagrams/` | Exported architecture figures | Inspect diagrams visually for company/device labels and product-specific design details before public release. The university internship report containing personal details is not part of this archive. |

## Safety changes in the GitHub-ready package

1. Only the modified `gateway_patch/tb_gateway_service.py` was copied from `thingsboard-gateway.zip`; backup gateway files, old variants, unneeded upstream CAN connector copies, compiled bytecode and patch utilities were **excluded**.
2. Plaintext IPC keys at the Gateway manager and Smart Panel client call sites in that file were changed to required `GATEWAY_AUTHKEY` and `SMART_PANEL_AUTHKEY` environment variables. The host client/server already expect these variables. The original submitted values may have been dummy; no claim is made that they were live secrets.
3. The separately uploaded gateway source has the ThingsBoard Apache-2.0 header. The license copy in `gateway_patch/` is **file-scoped** and is not a project-wide licensing decision.
4. Actual physical device values, company names, example connector UUIDs and diagrams were **not silently rewritten**. You decide which of these are intentionally public.

## Practical GitHub check

Before pushing, run a secrets scanner such as Gitleaks on the **entire Git history**, inspect staged changes (`git diff --cached`), and review JSON, YAML, documentation images, and `.env` files. Do not upload the raw original archives; the incoming archive includes backups and `__pycache__` files. If any key/token in prior versions was a live credential, **rotate it** rather than assuming removal from the latest commit is sufficient.

**Current text-only assessment:** No obvious live ThingsBoard access token, externally routable hard-coded server address or personal email was found in the repackaged **text sources**. This is not a guarantee of total anonymization. The remaining issues are mostly **identifiers, technical mappings, runtime logging, compatibility, and publication rights**.
