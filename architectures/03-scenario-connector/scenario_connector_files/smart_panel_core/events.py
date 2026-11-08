from dataclasses import dataclass, field
from time import time
from typing import Any, Dict, Optional


# ============================================================
# Event Bus Topics
# ============================================================

# CAN telemetry:
# SmartPanelCanUplinkConverter -> ScenarioEngine
CAN_TELEMETRY = "can.telemetry"


# CAN RPC / Command:
# ScenarioEngine -> CustomCanConnector
CAN_RPC = "can.rpc"


# Scenario RPC:
# ThingsBoard -> ScenarioConnector -> ScenarioEngine
SCENARIO_RPC = "scenario.rpc"


# Scenario data/state:
# ScenarioEngine -> ScenarioConnector -> ThingsBoard
SCENARIO_UPLINK = "scenario.uplink"


# ============================================================
# Common Event Envelope
# ============================================================

@dataclass(frozen=True)
class BusEvent:
    """
    Common envelope used by the internal Smart Panel Event Bus.

    Important:
        payload keeps the original ThingsBoard-compatible structure.

    Examples:

        CAN telemetry payload:
            converted_data.to_dict()

        RPC payload:
            {
                "device": "Lamp Controller",
                "data": {
                    "id": 10,
                    "method": "setPower",
                    "params": True
                }
            }
    """

    topic: str

    payload: Dict[str, Any]

    source: str = ""

    correlation_id: Optional[str] = None

    created_at_ms: int = field(
        default_factory=lambda: int(time() * 1000)
    )
