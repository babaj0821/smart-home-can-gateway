import logging

from thingsboard_gateway.connectors.can.bytes_can_downlink_converter import (
    BytesCanDownlinkConverter
)


class SmartPanelCanDownlinkConverter(BytesCanDownlinkConverter):

    _logger = logging.getLogger(
        "SmartPanelCanDownlinkConverter"
    )

    _base_converter = None

    @classmethod
    def _get_base_converter(cls):

        if cls._base_converter is None:
            cls._base_converter = BytesCanDownlinkConverter(
                cls._logger
            )

        return cls._base_converter

    @classmethod
    def convert(cls, config, data):

        base_converter = cls._get_base_converter()

        can_data = base_converter.convert(
            config,
            data
        )

        return can_data
