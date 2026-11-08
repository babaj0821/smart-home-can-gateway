import json

import grpc

from google.protobuf.wrappers_pb2 import (
    StringValue
)


class LocalProcessorGrpcClient:

    SERVICE = (
        "smartpanel.LocalProcessorService"
    )

    def __init__(
        self,
        target="127.0.0.1:50051",
        timeout=3.0
    ):
        self.target = target
        self.timeout = timeout

        self.channel = grpc.insecure_channel(
            target
        )

        self._methods = {}

    def _rpc(
        self,
        method
    ):
        rpc = self._methods.get(
            method
        )

        if rpc is None:
            rpc = self.channel.unary_unary(
                f"/{self.SERVICE}/{method}",
                request_serializer=
                    StringValue.SerializeToString,
                response_deserializer=
                    StringValue.FromString
            )

            self._methods[
                method
            ] = rpc

        return rpc

    def _call(
        self,
        method,
        payload=None,
        timeout=None
    ):
        if payload is None:
            payload = {}

        request = StringValue(
            value=json.dumps(
                payload,
                ensure_ascii=False
            )
        )

        response = self._rpc(
            method
        )(
            request,
            timeout=(
                self.timeout
                if timeout is None
                else timeout
            )
        )

        return json.loads(
            response.value
        )

    # ========================================================
    # Telemetry
    # ========================================================

    def send_telemetry(
        self,
        payload
    ):
        return self._call(
            "PushTelemetry",
            payload
        )

    # ========================================================
    # Devices
    # ========================================================

    def get_devices(self):
        return self._call(
            "GetDevices"
        )

    def get_state(
        self,
        name
    ):
        return self._call(
            "GetState",
            {
                "name": name
            }
        )

    def get_device_state(
        self,
        name
    ):
        return self.get_state(
            name
        )

    def get_all_states(self):
        return self._call(
            "GetAllStates"
        )

    def send_device_command(
        self,
        device,
        method,
        params=None
    ):
        return self._call(
            "SendDeviceCommand",
            {
                "device": device,
                "method": method,
                "params":
                    params or {}
            }
        )

    def execute_device_action(
        self,
        device,
        action,
        params=None
    ):
        return self._call(
            "ExecuteDeviceAction",
            {
                "device": device,
                "action": action,
                "params":
                    params or {}
            }
        )

    # ========================================================
    # Scenarios
    # ========================================================

    def get_scenarios(self):
        return self._call(
            "GetScenarios"
        )

    def get_scenario(
        self,
        name
    ):
        return self._call(
            "GetScenario",
            {
                "name": name
            }
        )

    def create_scenario(
        self,
        name,
        actions,
        description=""
    ):
        return self._call(
            "CreateScenario",
            {
                "name": name,
                "actions": actions,
                "description":
                    description
            }
        )

    def update_scenario(
        self,
        old_name,
        name,
        actions,
        description=""
    ):
        return self._call(
            "UpdateScenario",
            {
                "oldName": old_name,
                "name": name,
                "actions": actions,
                "description":
                    description
            }
        )

    def delete_scenario(
        self,
        name
    ):
        return self._call(
            "DeleteScenario",
            {
                "name": name
            }
        )

    def run_scenario(
        self,
        name
    ):
        return self._call(
            "RunScenario",
            {
                "name": name
            }
        )

    # ========================================================
    # ScenarioConnector command pull
    # ========================================================

    def pull_commands(
        self,
        limit=100
    ):
        return self._call(
            "PullCommands",
            {
                "limit": limit
            }
        )

    def close(self):
        self.channel.close()
