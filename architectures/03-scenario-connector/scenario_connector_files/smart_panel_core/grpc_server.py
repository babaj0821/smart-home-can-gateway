import json
from concurrent import futures

import grpc

from google.protobuf.wrappers_pb2 import (
    StringValue
)

from .local_processor import (
    LocalProcessor
)


ADDRESS = "127.0.0.1:50051"

SERVICE_NAME = (
    "smartpanel.LocalProcessorService"
)


class LocalProcessorGrpcService:

    def __init__(self):
        self.local_processor = LocalProcessor()

        print(
            "=== LOCAL PROCESSOR GRPC READY ===",
            flush=True
        )

    # ========================================================
    # Common helpers
    # ========================================================

    def _decode(
        self,
        request
    ):
        if not request.value:
            return {}

        payload = json.loads(
            request.value
        )

        if not isinstance(
            payload,
            dict
        ):
            raise ValueError(
                "gRPC payload must be a JSON object"
            )

        return payload

    def _response(
        self,
        payload
    ):
        return StringValue(
            value=json.dumps(
                payload,
                ensure_ascii=False
            )
        )

    def _error(
        self,
        error
    ):
        print(
            f"=== GRPC ERROR: {error} ===",
            flush=True
        )

        return self._response(
            {
                "success": False,
                "error": str(error)
            }
        )

    # ========================================================
    # Telemetry
    # ========================================================

    def push_telemetry(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            state = (
                self.local_processor
                .handle_can_telemetry(
                    payload
                )
            )

            return self._response(
                {
                    "success": True,
                    "accepted":
                        state is not None,
                    "deviceName":
                        (
                            state.get(
                                "deviceName"
                            )
                            if state
                            else None
                        )
                }
            )

        except Exception as e:
            return self._error(e)

    # ========================================================
    # Devices
    # ========================================================

    def get_devices(
        self,
        request,
        context
    ):
        try:
            return self._response(
                {
                    "success": True,
                    "devices":
                        self.local_processor
                        .device_names()
                }
            )

        except Exception as e:
            return self._error(e)

    def get_state(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            name = payload.get(
                "name"
            )

            if not name:
                raise ValueError(
                    "Device name is required"
                )

            return self._response(
                {
                    "success": True,
                    "state":
                        self.local_processor
                        .get_state(
                            name
                        )
                }
            )

        except Exception as e:
            return self._error(e)

    def get_all_states(
        self,
        request,
        context
    ):
        try:
            return self._response(
                {
                    "success": True,
                    "states":
                        self.local_processor
                        .get_all_states()
                }
            )

        except Exception as e:
            return self._error(e)

    def send_device_command(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            device = payload.get(
                "device"
            )

            method = payload.get(
                "method"
            )

            params = payload.get(
                "params",
                {}
            )

            if not device:
                raise ValueError(
                    "device is required"
                )

            if not method:
                raise ValueError(
                    "method is required"
                )

            if not isinstance(
                params,
                dict
            ):
                raise ValueError(
                    "params must be an object"
                )

            result = (
                self.local_processor
                .send_device_command(
                    device,
                    method,
                    params
                )
            )

            return self._response(
                {
                    "success": True,
                    "result": result
                }
            )

        except Exception as e:
            return self._error(e)

    def execute_device_action(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            device = payload.get(
                "device"
            )

            action = payload.get(
                "action"
            )

            params = payload.get(
                "params",
                {}
            )

            if not isinstance(
                params,
                dict
            ):
                raise ValueError(
                    "params must be an object"
                )

            print(
                "=== DEVICE ACTION RECEIVED"
                f" | device={device}"
                f" | action={action}"
                f" | params={params} ===",
                flush=True
            )

            result = (
                self.local_processor
                .execute_device_action(
                    device,
                    action,
                    params
                )
            )

            print(
                "=== DEVICE ACTION QUEUED"
                f" | device={device}"
                f" | action={action} ===",
                flush=True
            )

            return self._response(
                result
            )

        except Exception as e:
            return self._error(e)

    # ========================================================
    # Scenarios
    # ========================================================

    def get_scenarios(
        self,
        request,
        context
    ):
        try:
            return self._response(
                {
                    "success": True,
                    "scenarios":
                        self.local_processor
                        .get_scenarios()
                }
            )

        except Exception as e:
            return self._error(e)

    def get_scenario(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            name = payload.get(
                "name"
            )

            if not name:
                raise ValueError(
                    "Scenario name is required"
                )

            scenario = (
                self.local_processor
                .get_scenario(
                    name
                )
            )

            if scenario is None:
                raise ValueError(
                    f"Scenario not found: {name}"
                )

            return self._response(
                {
                    "success": True,
                    "scenario": scenario
                }
            )

        except Exception as e:
            return self._error(e)

    def create_scenario(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            scenario = (
                self.local_processor
                .create_scenario(
                    payload.get(
                        "name"
                    ),
                    payload.get(
                        "actions"
                    ),
                    payload.get(
                        "description",
                        ""
                    )
                )
            )

            return self._response(
                {
                    "success": True,
                    "scenario": scenario
                }
            )

        except Exception as e:
            return self._error(e)

    def update_scenario(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            scenario = (
                self.local_processor
                .update_scenario(
                    payload.get(
                        "oldName"
                    ),
                    payload.get(
                        "name"
                    ),
                    payload.get(
                        "actions"
                    ),
                    payload.get(
                        "description",
                        ""
                    )
                )
            )

            return self._response(
                {
                    "success": True,
                    "scenario": scenario
                }
            )

        except Exception as e:
            return self._error(e)

    def delete_scenario(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            name = payload.get(
                "name"
            )

            if not name:
                raise ValueError(
                    "Scenario name is required"
                )

            result = (
                self.local_processor
                .delete_scenario(
                    name
                )
            )

            return self._response(
                result
            )

        except Exception as e:
            return self._error(e)

    def run_scenario(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            name = payload.get(
                "name"
            )

            if not name:
                raise ValueError(
                    "Scenario name is required"
                )

            result = (
                self.local_processor
                .run_scenario(
                    name
                )
            )

            print(
                "=== SCENARIO EXECUTED / QUEUED ===",
                flush=True
            )

            print(
                result,
                flush=True
            )

            return self._response(
                result
            )

        except Exception as e:
            return self._error(e)

    # ========================================================
    # Command outbox
    # ========================================================

    def pull_commands(
        self,
        request,
        context
    ):
        try:
            payload = self._decode(
                request
            )

            commands = (
                self.local_processor
                .pull_commands(
                    payload.get(
                        "limit",
                        100
                    )
                )
            )

            return self._response(
                {
                    "success": True,
                    "commands": commands,
                    "remaining":
                        self.local_processor
                        .command_queue_size()
                }
            )

        except Exception as e:
            return self._error(e)


def _handler(
    function
):
    return grpc.unary_unary_rpc_method_handler(
        function,
        request_deserializer=
            StringValue.FromString,
        response_serializer=
            StringValue.SerializeToString
    )


def serve():
    service = LocalProcessorGrpcService()

    print(
        "=== CREATING GRPC SERVER ===",
        flush=True
    )

    server = grpc.server(
        futures.ThreadPoolExecutor(
            max_workers=8
        ),
        options=[
            (
                "grpc.so_reuseport",
                0
            )
        ]
    )

    # IMPORTANT:
    # All handler variables are created directly inside this
    # dictionary. This avoids the paste/order bug that caused:
    #
    #   UnboundLocalError:
    #   get_all_states_handler referenced before assignment
    #
    handlers = {
        "PushTelemetry":
            _handler(
                service.push_telemetry
            ),

        "GetDevices":
            _handler(
                service.get_devices
            ),

        "GetState":
            _handler(
                service.get_state
            ),

        # Compatibility alias for clients that use this name.
        "GetDeviceState":
            _handler(
                service.get_state
            ),

        "GetAllStates":
            _handler(
                service.get_all_states
            ),

        "SendDeviceCommand":
            _handler(
                service.send_device_command
            ),

        "ExecuteDeviceAction":
            _handler(
                service.execute_device_action
            ),

        "GetScenarios":
            _handler(
                service.get_scenarios
            ),

        "GetScenario":
            _handler(
                service.get_scenario
            ),

        "CreateScenario":
            _handler(
                service.create_scenario
            ),

        "UpdateScenario":
            _handler(
                service.update_scenario
            ),

        "DeleteScenario":
            _handler(
                service.delete_scenario
            ),

        "RunScenario":
            _handler(
                service.run_scenario
            ),

        "PullCommands":
            _handler(
                service.pull_commands
            )
    }

    generic_handler = (
        grpc.method_handlers_generic_handler(
            SERVICE_NAME,
            handlers
        )
    )

    server.add_generic_rpc_handlers(
        (
            generic_handler,
        )
    )

    print(
        f"=== BINDING GRPC SERVER TO {ADDRESS} ===",
        flush=True
    )

    bind_result = server.add_insecure_port(
        ADDRESS
    )

    print(
        f"=== GRPC BIND RESULT: {bind_result} ===",
        flush=True
    )

    if bind_result == 0:
        raise RuntimeError(
            f"Could not bind gRPC server to {ADDRESS}"
        )

    server.start()

    print(
        f"=== GRPC SERVER LISTENING ON {ADDRESS} ===",
        flush=True
    )

    try:
        server.wait_for_termination()

    except KeyboardInterrupt:
        server.stop(
            grace=2
        )


if __name__ == "__main__":
    serve()
