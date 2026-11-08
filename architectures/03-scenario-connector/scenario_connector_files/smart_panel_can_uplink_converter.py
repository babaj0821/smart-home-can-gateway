import logging

from thingsboard_gateway.connectors.can.bytes_can_uplink_converter import (
    BytesCanUplinkConverter
)

from thingsboard_gateway.extensions.custom.smart_panel_core.event_bus import (
    get_event_bus
)

from thingsboard_gateway.extensions.custom.smart_panel_core.events import (
    CAN_TELEMETRY
)

class SmartPanelCanUplinkConverter(BytesCanUplinkConverter):

    _logger = logging.getLogger(
        "SmartPanelCanUplinkConverter"
    )

    _base_converter = None

    def __init__(self, logger=None):
        if logger is None:
            logger = self.__class__._logger

        super().__init__(logger)

        self.__class__._logger = logger

        self.__class__._base_converter = (
            BytesCanUplinkConverter(logger)
        )

    @classmethod
    def _get_base_converter(cls):
        if cls._base_converter is None:
            cls._base_converter = BytesCanUplinkConverter(
                cls._logger
            )

        return cls._base_converter

    @classmethod
    def convert(cls, configs, can_data):
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

        try:
            payload = converted_data.to_dict()

            delivered = get_event_bus().publish(
                topic=CAN_TELEMETRY,
                payload=payload,
                source="SmartPanelCanUplinkConverter"
            )

            print(
                "### EVENT BUS PUBLISH"
                " | device=%s"
                " | delivered=%s ###"
                % (
                    configs.get("deviceName"),
                    delivered
                ),
                flush=True
            )

        except Exception as e:
            print(
                "### EVENT BUS PUBLISH ERROR: %r ###"
                % e,
                flush=True
            )

        return converted_data
