# Centralized configuration

I group **deployment-specific configuration templates** in this directory, while implementation code remains under [`../architectures/`](../architectures/). Subdirectories keep the four alternative architectures logically distinct. Do **not** mix settings from unrelated approaches into one running Gateway instance.

```text
config/
├── README.md
├── 01-parallel-socketcan/
│   ├── .env.example                  # Optional MQTT bridge variables
│   ├── tb_gateway.json              # Gateway reference settings
│   └── padnaCanGateway.json         # CAN mapping examples
├── 02-gateway-integrated/
│   ├── .env.example                  # Unix-domain socket paths/authentication
│   ├── tb_gateway.json              # Customized Gateway reference settings
│   └── padnaCanGateway.json         # CAN mapping examples
├── 03-scenario-connector/
│   ├── .env.example                  # ThingsBoard endpoint/token, CAN interface
│   ├── docker-compose.yml           # Reference deployment (paths updated)
│   └── gateway/
│       ├── tb_gateway.json          # ThingsBoard Gateway settings/connector registry
│       ├── padnaCanGateway.json     # CAN devices, telemetry and RPC mapping
│       ├── scenarioConnector.json   # gRPC target and connector settings
│       └── statistics/              # Platform-specific Gateway statistics samples
└── hardware/
    └── mcp2515.dts                   # Board-dependent Linux Device Tree overlay
```

## Using a configuration template

**Architecture 01** (from `architectures/01-parallel-socketcan/`):

```bash
cp ../../config/01-parallel-socketcan/.env.example .env
# Edit .env with your own non-public values.
set -a; . ./.env; set +a
```

**Architecture 02** (from `architectures/02-gateway-integrated/`):

```bash
cp ../../config/02-gateway-integrated/.env.example .env
# Set private authentication keys consistently on both IPC endpoints.
set -a; . ./.env; set +a
```

**Architecture 03** (from repository root):

```bash
cd config/03-scenario-connector
cp .env.example .env
# Edit .env and inspect gateway/*.json (intentionally anonymized examples).
docker compose --env-file .env config
docker compose --env-file .env up -d
```

The Compose file lives **beside** its `.env.example`; bind-mounted source paths are relative to this directory:

- `./gateway` → `/thingsboard_gateway/config`
- `../../architectures/03-scenario-connector/can` → Gateway CAN extensions
- `../../architectures/03-scenario-connector/scenario_connector_files` → custom connector extensions
- `../../architectures/03-scenario-connector/smart_panel_shared` → shared converter/connector helper
- `../../architectures/03-scenario-connector/runtime/logs` → runtime logs (untracked)

For the full setup, including the host-side gRPC server, see the [architecture 03 README](../architectures/03-scenario-connector/README.md).

**Architecture 04:** my ThingsBoard Edge experiments are documented, but Edge Rule Chain exports and deployment configuration are **not included** here; I do not substitute invented settings.

**Hardware:** [`hardware/mcp2515.dts`](hardware/mcp2515.dts) is a *board-dependent overlay source*, not a universal drop-in configuration. Read the [bring-up guide](../hardware/README.md) and verify SPI/IRQ/clock wiring before compiling or deploying it.

## What intentionally stays outside `config/`

- `architectures/01-parallel-socketcan/integrations/thingsboard/tb_config.py` is an **imported Python adapter that reads environment variables**, not a site-specific settings file. Keeping it next to its importing application preserves module paths; its actual values come from the root config environment template.
- `examples/scenarios.json` and `examples/devices_registry.json` are **sample runtime data**, not deployment settings.
- `requirements.txt` and `requirements-host.txt` are dependency manifests, not host configuration.
- The Gateway-integrated `gateway_patch/tb_gateway_service.py` is code derived from an upstream file, not a configuration template.

## Configuration safety

I intentionally anonymized the private CAN protocol values and connection details. The connector UUIDs in this directory are newly generated **sample identifiers**, not secrets or identifiers from my original deployment. These JSON files are reference templates, **not production configuration**. Deployed tokens belong in local environment variables or a secrets manager, not tracked JSON. The example `.env` templates contain only placeholders; `.env` files are ignored by Git. See [engineering notes](../docs/engineering-notes.md) for remaining technical limitations.
