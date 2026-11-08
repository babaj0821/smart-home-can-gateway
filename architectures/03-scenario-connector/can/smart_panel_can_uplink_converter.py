import logging
import sys

from thingsboard_gateway.connectors.can.bytes_can_uplink_converter import (
    BytesCanUplinkConverter
)


EXTENSIONS_PATH = "/thingsboard_gateway/extensions"

if EXTENSIONS_PATH not in sys.path:
    sys.path.insert(
        0,
        EXTENSIONS_PATH
    )


from smart_panel_shared.can_scenario_bridge import (
    get_can_scenario_bridge
)


class SmartPanelCanUplinkConverter(
    BytesCanUplinkConverter
):

    _logger = logging.getLogger(
        "SmartPanelCanUplinkConverter"
    )

    _base_converter = None

    @classmethod
    def _get_base_converter(
        cls
    ):
        if cls._base_converter is None:
            cls._base_converter = BytesCanUplinkConverter(
                cls._logger
            )

        return cls._base_converter

    @classmethod
    def convert(
        cls,
        configs,
        can_data
    ):
        print(
            "### SMART PANEL CONVERT ENTERED"
            " | device=%s ###"
            % configs.get("deviceName"),
            flush=True
        )

        base_converter = cls._get_base_converter()

        converted_data = base_converter.convert(
            configs,
            can_data
        )

        print(
            "### SMART PANEL BASE CONVERT DONE"
            " | device=%s ###"
            % configs.get("deviceName"),
            flush=True
        )

        if converted_data is None:
            return None

        try:
            payload = converted_data.to_dict()

            bridge = get_can_scenario_bridge()

            queued = bridge.push_telemetry(
                payload
            )

            print(
                "### BRIDGE PUSH TELEMETRY"
                " | device=%s"
                " | queued=%s"
                " | qsize=%s ###"
                % (
                    configs.get("deviceName"),
                    queued,
                    bridge.telemetry_qsize()
                ),
                flush=True
            )

        except Exception as e:
            print(
                "### BRIDGE PUSH TELEMETRY ERROR"
                " | error=%r ###"
                % e,
                flush=True
            )

        return converted_data
