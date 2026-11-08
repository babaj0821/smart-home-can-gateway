from thingsboard_gateway.connectors.can.can_connector import (
    CanConnector
)
from thingsboard_gateway.extensions.custom.smart_panel_core.event_bus import (
    get_event_bus
)

from thingsboard_gateway.extensions.custom.smart_panel_core.events import (
    CAN_RPC
)

import threading

class CustomCanConnector(
    CanConnector
):

    def __init__(
        self,
        gateway,
        config,
        connector_type
    ):

        super().__init__(
            gateway,
            config,
            connector_type
        )


        self._log.warning(
            "=== Custom CAN Connector started ==="
        )
        self.event_bus = get_event_bus()

        self.rpc_subscription = (
            self.event_bus.subscribe(
                topic=CAN_RPC,
                subscriber_id="custom_can_connector"
            )
        )


        threading.Thread(
            target=self._rpc_worker,
            daemon=True
        ).start()


        self._log.warning(
            "=== CUSTOM CAN RPC LISTENER STARTED ==="
        )

        converters = getattr(
            self,
            "_CanConnector__converters",
            {}
        )


        for device_name, device_converters in converters.items():

            uplink = device_converters.get(
                "uplink"
            )

            self._log.warning(
                "=== DEVICE CONVERTER | device=%s | uplink=%r | type=%s ===",
                device_name,
                uplink,
                type(uplink)
            )
    def _rpc_worker(
        self
    ):

        while True:

            try:

                event = self.rpc_subscription.get()

                self._log.warning(
                    "=== CAN RPC EVENT RECEIVED ==="
                )

                self._log.warning(
                    "%s",
                    event.payload
                )


                self.internal_rpc_handler(
                    event.payload
                )


            except Exception as e:

                self._log.exception(
                    "=== CAN RPC WORKER ERROR: %s ===",
                    e
                )
    def internal_rpc_handler(
        self,
        content
    ):
        """
        Handle RPC commands coming from
        Smart Panel Scenario Engine.

        This command has exactly the same
        structure as ThingsBoard RPC.

        Example:

        {
            "device": "Lamp Controller",
            "data": {
                "id": 1,
                "method": "setLedBit1",
                "params": {
                    "on": 1
                }
            }
        }

        """


        self._log.warning(
            "=== INTERNAL RPC RECEIVED ==="
        )


        self._log.warning(
            "%s",
            content
        )


        try:

            self.server_side_rpc_handler(
                content
            )


            self._log.warning(
                "=== INTERNAL RPC SENT TO CAN HANDLER ==="
            )


            return True


        except Exception as e:

            self._log.exception(
                "=== INTERNAL RPC ERROR: %s ===",
                e
            )

            return False
