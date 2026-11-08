import sys

from collections import deque
from copy import deepcopy
from threading import Event, Thread
from time import monotonic

from thingsboard_gateway.connectors.connector import Connector
from thingsboard_gateway.tb_utility.tb_logger import init_logger

from thingsboard_gateway.extensions.custom.smart_panel_core.grpc_client import (
    LocalProcessorGrpcClient
)


# ============================================================
# Shared extension path
# ============================================================

EXTENSIONS_PATH = "/thingsboard_gateway/extensions"

if EXTENSIONS_PATH not in sys.path:
    sys.path.insert(
        0,
        EXTENSIONS_PATH
    )


from smart_panel_shared.can_scenario_bridge import (
    get_can_scenario_bridge
)


class ScenarioConnector(Thread, Connector):

    def __init__(
        self,
        gateway,
        config,
        connector_type
    ):
        super().__init__()

        # ====================================================
        # Gateway / Connector configuration
        # ====================================================

        self.__gateway = gateway
        self.__config = config

        self._connector_type = connector_type

        self.__id = config.get(
            "id"
        )

        self.name = config.get(
            "name",
            "ScenarioConnector"
        )

        # ====================================================
        # Logger
        # ====================================================

        self._log = init_logger(
            self.__gateway,
            self.name,
            level=config.get(
                "logLevel",
                "DEBUG"
            ),
            enable_remote_logging=config.get(
                "enableRemoteLogging",
                False
            ),
            is_connector_logger=True
        )

        # ====================================================
        # Local Processor virtual ThingsBoard device
        # ====================================================

        device_config = self.__get_device_config(
            config
        )

        self.__device_name = device_config.get(
            "name",
            "Local Processor"
        )

        self.__device_type = device_config.get(
            "type",
            "default"
        )

        # ====================================================
        # Original CAN Connector
        #
        # This is NOT a CustomCanConnector.
        #
        # ScenarioConnector will find the already-running
        # original ThingsBoard CanConnector through Gateway's
        # connector registry.
        # ====================================================

        self.__can_connector_name = config.get(
            "canConnectorName",
            "PADNA-CAN-Gateway"
        )

        # ====================================================
        # Runtime state
        # ====================================================

        self.daemon = True

        self.stopped = Event()
        self.stopped.set()

        self.__connected = False

        # ====================================================
        # CAN telemetry Bridge
        #
        # Uplink:
        #
        # SmartPanelCanUplinkConverter
        #       ->
        # CanScenarioBridge
        #       ->
        # ScenarioConnector
        # ====================================================

        self.__can_bridge = (
            get_can_scenario_bridge()
        )

        # ====================================================
        # Local Processor gRPC client
        # ====================================================

        grpc_config = config.get(
            "localProcessorGrpc",
            {}
        )

        self.__grpc_target = grpc_config.get(
            "target",
            "127.0.0.1:50051"
        )

        self.__grpc_timeout = float(
            grpc_config.get(
                "timeoutSeconds",
                3.0
            )
        )

        self.__local_processor_client = (
            LocalProcessorGrpcClient(
                target=self.__grpc_target,
                timeout=self.__grpc_timeout
            )
        )

        # ====================================================
        # Local CAN command processing
        #
        # Commands are pulled from LocalProcessor over gRPC.
        #
        # Pending commands are kept here if the CAN connector
        # is temporarily unavailable.
        # ====================================================

        self.__pending_can_commands = deque()

        self.__command_pull_limit = int(
            config.get(
                "commandPullLimit",
                10
            )
        )

        if self.__command_pull_limit < 1:
            self.__command_pull_limit = 1

        if self.__command_pull_limit > 100:
            self.__command_pull_limit = 100

        self.__command_poll_interval = float(
            config.get(
                "commandPollIntervalSeconds",
                0.25
            )
        )

        self.__command_retry_interval = float(
            config.get(
                "commandRetryIntervalSeconds",
                1.0
            )
        )

        self.__next_command_poll_at = 0.0
        self.__next_command_retry_at = 0.0

        # ====================================================
        # Local RPC ID namespace
        #
        # ThingsBoard RPC IDs normally use positive values.
        #
        # Smart Panel local commands use negative IDs so they
        # cannot accidentally overlap with a real TB RPC ID.
        # ====================================================

        self.__next_local_rpc_id = -1

        # Avoid repeating compatibility error every loop.
        self.__pull_commands_api_error_logged = False

        # ====================================================
        # Diagnostic logs
        # ====================================================

        self._log.warning(
            "=== SCENARIO CONNECTOR INITIALIZED ==="
        )

        self._log.warning(
            "=== LOCAL PROCESSOR CONFIG"
            " | name=%s"
            " | type=%s ===",
            self.__device_name,
            self.__device_type
        )

        self._log.warning(
            "=== CAN SCENARIO BRIDGE READY"
            " | bridge_id=%s ===",
            id(
                self.__can_bridge
            )
        )

        self._log.warning(
            "=== LOCAL PROCESSOR GRPC CLIENT CREATED"
            " | target=%s"
            " | timeout=%s ===",
            self.__grpc_target,
            self.__grpc_timeout
        )

        self._log.warning(
            "=== LOCAL CAN DOWNLINK CONFIG"
            " | connector=%s"
            " | poll=%s"
            " | retry=%s ===",
            self.__can_connector_name,
            self.__command_poll_interval,
            self.__command_retry_interval
        )

    # ========================================================
    # Configuration helpers
    # ========================================================

    @staticmethod
    def __get_device_config(
        config
    ):

        device_config = config.get(
            "device"
        )

        if isinstance(
            device_config,
            dict
        ):
            return device_config

        inner_config = config.get(
            "config"
        )

        if isinstance(
            inner_config,
            dict
        ):

            device_config = inner_config.get(
                "device"
            )

            if isinstance(
                device_config,
                dict
            ):
                return device_config

            for value in inner_config.values():

                if not isinstance(
                    value,
                    dict
                ):
                    continue

                device_config = value.get(
                    "device"
                )

                if isinstance(
                    device_config,
                    dict
                ):
                    return device_config

        return {}

    # ========================================================
    # Connector lifecycle
    # ========================================================

    def open(
        self
    ):

        self._log.warning(
            "=== SCENARIO CONNECTOR OPEN CALLED ==="
        )

        self.stopped.clear()

        self.start()

    def run(
        self
    ):

        self._log.warning(
            "=== SCENARIO CONNECTOR RUNNING ==="
        )

        retry_count = 0

        registration_reset_done = False

        # ====================================================
        # Register Local Processor virtual device
        #
        # The Gateway may remember Local Processor from a
        # previous run while ThingsBoard no longer has an
        # active gateway-device connection.
        #
        # Therefore we clear the old Gateway registration
        # once and then register the device again.
        # ====================================================

        while (
            not self.stopped.is_set()
            and
            not self.__connected
        ):

            try:

                # ============================================
                # Wait until Gateway itself is connected to
                # ThingsBoard.
                # ============================================

                tb_client = getattr(
                    self.__gateway,
                    "tb_client",
                    None
                )

                if (
                    tb_client is None
                    or
                    not tb_client.is_connected()
                ):

                    retry_count += 1

                    if (
                        retry_count == 1
                        or
                        retry_count % 5 == 0
                    ):

                        self._log.info(
                            "Gateway is not connected to "
                            "ThingsBoard yet. "
                            "Waiting before registering "
                            "Local Processor..."
                        )

                    self.stopped.wait(
                        1
                    )

                    continue

                # ============================================
                # Clear stale registration exactly once.
                # ============================================

                if not registration_reset_done:

                    self._log.warning(
                        "=== LOCAL PROCESSOR GATEWAY"
                        " RECONNECT START"
                        " | device=%s ===",
                        self.__device_name
                    )

                    try:

                        self.__gateway.del_device(
                            self.__device_name,
                            remove_device=False
                        )

                        self._log.warning(
                            "=== OLD LOCAL PROCESSOR"
                            " GATEWAY REGISTRATION CLEARED"
                            " | device=%s ===",
                            self.__device_name
                        )

                    except Exception as e:

                        self._log.warning(
                            "=== LOCAL PROCESSOR"
                            " PRE-CONNECT CLEANUP"
                            " | device=%s"
                            " | error=%s ===",
                            self.__device_name,
                            e
                        )

                    registration_reset_done = True

                    self.stopped.wait(
                        0.25
                    )

                    if self.stopped.is_set():
                        break

                # ============================================
                # Fresh registration.
                # ============================================

                result = (
                    self.__gateway.add_device(
                        self.__device_name,
                        {
                            "connector": self
                        },
                        self.__device_type
                    )
                )

                if result:

                    self.__connected = True

                    self._log.warning(
                        "=== LOCAL PROCESSOR REGISTERED"
                        " SUCCESSFULLY"
                        " | device=%s ===",
                        self.__device_name
                    )

                    self._log.warning(
                        "=== LOCAL PROCESSOR GATEWAY"
                        " CONNECTION ACTIVE"
                        " | device=%s ===",
                        self.__device_name
                    )

                    break

                retry_count += 1

            except Exception as e:

                self._log.exception(
                    "Error while registering "
                    "Local Processor: %s",
                    e
                )

            self.stopped.wait(
                1
            )
        # ====================================================
        # Main worker loop
        #
        # Uplink:
        # Bridge -> ScenarioConnector -> gRPC
        #
        # Downlink:
        # gRPC -> ScenarioConnector -> Original CanConnector
        # ====================================================

        while not self.stopped.is_set():

            self.__process_one_telemetry()

            self.__process_can_command_outbox()

        self._log.info(
            "Scenario Connector thread stopped"
        )

    # ========================================================
    # UPLINK
    #
    # CanScenarioBridge
    #       ->
    # ScenarioConnector
    #       ->
    # LocalProcessor gRPC
    # ========================================================

    def __process_one_telemetry(
        self
    ):

        payload = (
            self.__can_bridge.get_telemetry(
                timeout=0.25
            )
        )

        if payload is None:
            return

        print(
            "### SCENARIO CONNECTOR BRIDGE TELEMETRY"
            " | device=%s ###"
            % payload.get(
                "deviceName",
                "unknown"
            ),
            flush=True
        )

        try:

            result = (
                self.__local_processor_client
                .send_telemetry(
                    payload
                )
            )

            self._log.warning(
                "=== TELEMETRY SENT TO LOCAL PROCESSOR"
                " VIA GRPC"
                " | device=%s"
                " | result=%s ===",
                payload.get(
                    "deviceName"
                ),
                result
            )

        except Exception as e:

            self._log.error(
                "=== FAILED TO SEND TELEMETRY"
                " TO LOCAL PROCESSOR"
                " VIA GRPC"
                " | device=%s"
                " | error=%s ===",
                payload.get(
                    "deviceName"
                ),
                e
            )

    # ========================================================
    # DOWNLINK
    #
    # LocalProcessor CommandOutbox
    #       ->
    # gRPC PullCommands
    #       ->
    # ScenarioConnector
    #       ->
    # Original CanConnector.server_side_rpc_handler()
    #       ->
    # Official BytesCanDownlinkConverter
    #       ->
    # Original CanConnector.send_data_to_bus()
    #       ->
    # CAN
    # ========================================================

    def __process_can_command_outbox(
        self
    ):

        now = monotonic()

        # ====================================================
        # If a command previously failed because CAN connector
        # was temporarily unavailable, wait before retrying.
        # ====================================================

        if (
            self.__pending_can_commands
            and
            now < self.__next_command_retry_at
        ):
            return

        # ====================================================
        # Pull new commands only when local pending queue
        # is empty.
        # ====================================================

        if not self.__pending_can_commands:

            if now < self.__next_command_poll_at:
                return

            self.__next_command_poll_at = (
                now
                +
                self.__command_poll_interval
            )

            try:

                commands = (
                    self.__pull_local_commands()
                )

            except Exception as e:

                self._log.error(
                    "=== FAILED TO PULL LOCAL COMMANDS"
                    " | error=%s ===",
                    e
                )

                self.__next_command_poll_at = (
                    monotonic()
                    +
                    self.__command_retry_interval
                )

                return

            for command in commands:

                self.__pending_can_commands.append(
                    command
                )

        # ====================================================
        # Nothing to send
        # ====================================================

        if not self.__pending_can_commands:
            return

        command = (
            self.__pending_can_commands[0]
        )

        # ====================================================
        # Dispatch first pending command
        # ====================================================

        try:

            self.__dispatch_local_can_command(
                command
            )

        except ValueError as e:

            # ------------------------------------------------
            # Permanent invalid/unsafe command.
            #
            # Do not retry forever and block later commands.
            # ------------------------------------------------

            self._log.error(
                "=== LOCAL CAN COMMAND REJECTED"
                " | command=%s"
                " | reason=%s ===",
                command,
                e
            )

            self.__pending_can_commands.popleft()

            return

        except Exception as e:

            # ------------------------------------------------
            # Usually temporary:
            #
            # CAN connector unavailable
            # connector reload
            # compatibility issue
            # runtime failure
            #
            # Keep command and retry later.
            # ------------------------------------------------

            self._log.error(
                "=== LOCAL CAN COMMAND DELIVERY FAILED"
                " | command=%s"
                " | error=%s"
                " | retry_in=%s ===",
                command,
                e,
                self.__command_retry_interval
            )

            self.__next_command_retry_at = (
                monotonic()
                +
                self.__command_retry_interval
            )

            return

        # ====================================================
        # Handler accepted the call without raising.
        #
        # Remove command from our pending queue.
        # ====================================================

        self.__pending_can_commands.popleft()

        self.__next_command_retry_at = 0.0

    # ========================================================
    # Pull commands from LocalProcessor over gRPC
    # ========================================================

    def __pull_local_commands(
        self
    ):

        pull_method = getattr(
            self.__local_processor_client,
            "pull_commands",
            None
        )

        if not callable(
            pull_method
        ):

            if not self.__pull_commands_api_error_logged:

                self.__pull_commands_api_error_logged = True

                self._log.error(
                    "=== LOCAL PROCESSOR GRPC API"
                    " DOES NOT PROVIDE pull_commands() ==="
                )

            raise RuntimeError(
                "LocalProcessorGrpcClient.pull_commands() "
                "is unavailable"
            )

        result = pull_method(
            self.__command_pull_limit
        )

        self.__pull_commands_api_error_logged = False

        # ====================================================
        # Supported response form:
        #
        # [
        #     {...},
        #     {...}
        # ]
        # ====================================================

        if isinstance(
            result,
            list
        ):
            return result

        # ====================================================
        # Also support wrapped gRPC responses such as:
        #
        # {
        #     "success": True,
        #     "commands": [...]
        # }
        # ====================================================

        if isinstance(
            result,
            dict
        ):

            commands = result.get(
                "commands"
            )

            if isinstance(
                commands,
                list
            ):
                return commands

            commands = result.get(
                "result"
            )

            if isinstance(
                commands,
                list
            ):
                return commands

            commands = result.get(
                "data"
            )

            if isinstance(
                commands,
                list
            ):
                return commands

            # A successful empty response may omit commands.
            if (
                result.get(
                    "success"
                )
                is True
            ):
                return []

        if result is None:
            return []

        raise RuntimeError(
            "Unexpected PullCommands response: "
            + repr(
                result
            )
        )

    # ========================================================
    # Direct local command -> Original CanConnector
    # ========================================================

    def __dispatch_local_can_command(
        self,
        command
    ):

        can_connector = (
            self.__get_can_connector()
        )

        safe_command = (
            self.__prepare_local_can_command(
                can_connector,
                command
            )
        )

        device = safe_command.get(
            "device"
        )

        data = safe_command.get(
            "data",
            {}
        )

        self._log.warning(
            "=== LOCAL CAN COMMAND DISPATCH"
            " | connector=%s"
            " | device=%s"
            " | method=%s"
            " | local_rpc_id=%s ===",
            self.__can_connector_name,
            device,
            data.get(
                "method"
            ),
            data.get(
                "id"
            )
        )

        handler = getattr(
            can_connector,
            "server_side_rpc_handler",
            None
        )

        if not callable(
            handler
        ):
            raise RuntimeError(
                "CAN connector does not provide "
                "server_side_rpc_handler()"
            )

        # ====================================================
        # This is the important call.
        #
        # We do NOT:
        # - encode CAN here
        # - call the downlink converter ourselves
        # - call send_data_to_bus ourselves
        #
        # Original CanConnector handles all of it.
        # ====================================================

        handler(
            safe_command
        )

        self._log.warning(
            "=== LOCAL CAN COMMAND HANDED TO"
            " ORIGINAL CAN CONNECTOR"
            " | device=%s"
            " | method=%s"
            " | local_rpc_id=%s ===",
            device,
            data.get(
                "method"
            ),
            data.get(
                "id"
            )
        )

    # ========================================================
    # Get the real, currently-running Original CanConnector
    #
    # Important:
    # We fetch it for every command.
    #
    # Therefore if ThingsBoard reloads/recreates the connector,
    # we do not keep a stale connector object.
    # ========================================================

    def __get_can_connector(
        self
    ):

        registry = getattr(
            self.__gateway,
            "available_connectors_by_name",
            None
        )

        if not isinstance(
            registry,
            dict
        ):
            raise RuntimeError(
                "Gateway connector registry "
                "is unavailable"
            )

        can_connector = registry.get(
            self.__can_connector_name
        )

        if can_connector is None:
            raise RuntimeError(
                "CAN connector is not running: "
                + str(
                    self.__can_connector_name
                )
            )

        handler = getattr(
            can_connector,
            "server_side_rpc_handler",
            None
        )

        if not callable(
            handler
        ):
            raise RuntimeError(
                "CAN connector API is incompatible: "
                "server_side_rpc_handler() missing"
            )

        get_config = getattr(
            can_connector,
            "get_config",
            None
        )

        if not callable(
            get_config
        ):
            raise RuntimeError(
                "CAN connector API is incompatible: "
                "get_config() missing"
            )

        return can_connector

    # ========================================================
    # Prepare and validate a LOCAL RPC-shaped command
    #
    # Safety goals:
    #
    # 1. Never use reserved RPC method "set".
    #
    # 2. Use negative local RPC IDs.
    #
    # 3. Ensure local command cannot intentionally request
    #    a ThingsBoard RPC response.
    #
    # 4. Fail closed if current CAN configuration cannot
    #    safely suppress the response.
    # ========================================================

    def __prepare_local_can_command(
        self,
        can_connector,
        command
    ):

        if not isinstance(
            command,
            dict
        ):
            raise ValueError(
                "Local CAN command must be a dictionary"
            )

        result = deepcopy(
            command
        )

        device = result.get(
            "device"
        )

        if not device:
            raise ValueError(
                "Local CAN command device is missing"
            )

        data = result.get(
            "data"
        )

        if not isinstance(
            data,
            dict
        ):
            raise ValueError(
                "Local CAN command data is missing"
            )

        method = data.get(
            "method"
        )

        if not method:
            raise ValueError(
                "Local CAN command method is missing"
            )

        # ====================================================
        # "set" is reserved by ThingsBoard CanConnector and
        # its reserved handler sends an RPC reply directly.
        #
        # Local Smart Panel commands must never use it.
        # ====================================================

        if method == "set":
            raise ValueError(
                'Reserved CAN RPC method "set" '
                "cannot be used by LocalProcessor"
            )

        params = data.get(
            "params",
            {}
        )

        if params is None:
            params = {}

        if not isinstance(
            params,
            dict
        ):
            raise ValueError(
                "Local CAN RPC params must be a dictionary"
            )

        params = deepcopy(
            params
        )

        data[
            "params"
        ] = params

        # ====================================================
        # Replace LocalProcessor positive/request ID with our
        # isolated negative local RPC ID.
        # ====================================================

        data[
            "id"
        ] = self.__allocate_local_rpc_id()

        # ====================================================
        # Read PUBLIC connector configuration.
        #
        # We deliberately do NOT touch:
        #
        # _CanConnector__devices
        # _CanConnector__rpc_calls
        # _CanConnector__converters
        #
        # or any other private ThingsBoard field.
        # ====================================================

        device_config = (
            self.__find_can_device_config(
                can_connector,
                device
            )
        )

        if device_config is None:
            raise ValueError(
                "CAN device configuration not found: "
                + str(
                    device
                )
            )

        rpc_config = (
            self.__find_rpc_config(
                device_config,
                method
            )
        )

        # ====================================================
        # Resolve enableUnknownRpc
        # ====================================================

        default_enable_unknown = getattr(
            can_connector,
            "DEFAULT_ENABLE_UNKNOWN_RPC",
            False
        )

        enable_unknown_rpc = (
            self.__to_bool(
                device_config.get(
                    "enableUnknownRpc",
                    default_enable_unknown
                )
            )
        )

        if (
            rpc_config is None
            and
            not enable_unknown_rpc
        ):
            raise ValueError(
                "No CAN serverSideRpc configuration "
                "for method: "
                + str(
                    method
                )
            )

        # ====================================================
        # Resolve overrideRpcConfig exactly as current
        # CanConnector does.
        #
        # If enableUnknownRpc=True, CanConnector forces
        # override behavior.
        # ====================================================

        if enable_unknown_rpc:

            override_rpc_config = True

        else:

            if (
                "overrideRpcConfig"
                in device_config
            ):

                override_rpc_config = (
                    self.__to_bool(
                        device_config.get(
                            "overrideRpcConfig"
                        )
                    )
                )

            else:

                if not hasattr(
                    can_connector,
                    "DEFAULT_OVERRIDE_RPC_PARAMS"
                ):
                    raise RuntimeError(
                        "Cannot determine safe "
                        "overrideRpcConfig behavior"
                    )

                override_rpc_config = (
                    self.__to_bool(
                        getattr(
                            can_connector,
                            "DEFAULT_OVERRIDE_RPC_PARAMS"
                        )
                    )
                )

        # ====================================================
        # RESPONSE SAFETY
        # ====================================================

        if override_rpc_config:

            # -----------------------------------------------
            # Current CanConnector merge logic gives RPC
            # params priority.
            #
            # Therefore this forces:
            #
            # conversion_config["response"] = False
            # -----------------------------------------------

            params[
                "response"
            ] = False

        else:

            # -----------------------------------------------
            # Params are ignored as conversion config when:
            #
            # overrideRpcConfig == False
            #
            # Therefore response safety must come from the
            # configured serverSideRpc itself.
            # -----------------------------------------------

            if rpc_config is None:
                raise ValueError(
                    "Cannot validate RPC response safety"
                )

            if "response" in rpc_config:

                response_enabled = (
                    self.__to_bool(
                        rpc_config.get(
                            "response"
                        )
                    )
                )

            else:

                if not hasattr(
                    can_connector,
                    "DEFAULT_RPC_RESPONSE_SEND_FLAG"
                ):
                    raise RuntimeError(
                        "Cannot determine default "
                        "RPC response behavior"
                    )

                response_enabled = (
                    self.__to_bool(
                        getattr(
                            can_connector,
                            "DEFAULT_RPC_RESPONSE_SEND_FLAG"
                        )
                    )
                )

            if response_enabled:

                raise ValueError(
                    "Local CAN RPC blocked because "
                    "its serverSideRpc configuration "
                    "has response=True while "
                    "overrideRpcConfig=False"
                )

        return result

    # ========================================================
    # Find CAN device in public CanConnector configuration
    # ========================================================

    def __find_can_device_config(
        self,
        can_connector,
        device_name
    ):

        get_config = getattr(
            can_connector,
            "get_config",
            None
        )

        if not callable(
            get_config
        ):
            return None

        config = get_config()

        if not isinstance(
            config,
            dict
        ):
            return None

        devices = config.get(
            "devices"
        )

        # Some wrapper configurations may contain a nested
        # "config" object. Support that form as well.
        if not isinstance(
            devices,
            list
        ):

            inner_config = config.get(
                "config"
            )

            if isinstance(
                inner_config,
                dict
            ):
                devices = inner_config.get(
                    "devices"
                )

        if not isinstance(
            devices,
            list
        ):
            return None

        for device_config in devices:

            if not isinstance(
                device_config,
                dict
            ):
                continue

            if (
                device_config.get(
                    "name"
                )
                ==
                device_name
            ):
                return device_config

        return None

    # ========================================================
    # Find server-side RPC configuration
    # ========================================================

    @staticmethod
    def __find_rpc_config(
        device_config,
        method
    ):

        rpc_configs = device_config.get(
            "serverSideRpc",
            []
        )

        if not isinstance(
            rpc_configs,
            list
        ):
            return None

        for rpc_config in rpc_configs:

            if not isinstance(
                rpc_config,
                dict
            ):
                continue

            if (
                rpc_config.get(
                    "method"
                )
                ==
                method
            ):
                return rpc_config

        return None

    # ========================================================
    # Local negative RPC ID allocator
    # ========================================================

    def __allocate_local_rpc_id(
        self
    ):

        rpc_id = self.__next_local_rpc_id

        self.__next_local_rpc_id -= 1

        # Reset before reaching unreasonable integer size.
        if self.__next_local_rpc_id < -2147483647:
            self.__next_local_rpc_id = -1

        return rpc_id

    # ========================================================
    # Safe bool parser for configuration values
    # ========================================================

    @staticmethod
    def __to_bool(
        value
    ):

        if isinstance(
            value,
            bool
        ):
            return value

        if isinstance(
            value,
            str
        ):

            normalized = (
                value.strip().lower()
            )

            if normalized in (
                "true",
                "1",
                "yes",
                "on"
            ):
                return True

            if normalized in (
                "false",
                "0",
                "no",
                "off",
                ""
            ):
                return False

        return bool(
            value
        )

    # ========================================================
    # Close
    # ========================================================

    def close(
        self
    ):

        self._log.warning(
            "=== SCENARIO CONNECTOR CLOSE CALLED ==="
        )

        self.stopped.set()

        # ====================================================
        # Close LocalProcessor gRPC client
        # ====================================================

        try:

            self.__local_processor_client.close()

            self._log.warning(
                "=== LOCAL PROCESSOR GRPC CLIENT CLOSED ==="
            )

        except Exception as e:

            self._log.error(
                "Failed to close Local Processor "
                "gRPC client: %s",
                e
            )

        # ====================================================
        # Remove Local Processor virtual device
        # ====================================================

        if self.__connected:

            try:

                self.__gateway.del_device(
                    self.__device_name
                )

            except Exception as e:

                self._log.exception(
                    "Failed to disconnect "
                    "Local Processor: %s",
                    e
                )

        self.__connected = False

        # ====================================================
        # Stop connector logger
        # ====================================================

        try:

            self._log.stop()

        except Exception:
            pass

    # ========================================================
    # Connector interface
    # ========================================================

    def get_name(
        self
    ):
        return self.name

    def get_type(
        self
    ):
        return self._connector_type

    def get_id(
        self
    ):
        return self.__id

    def get_config(
        self
    ):
        return self.__config

    def is_connected(
        self
    ):
        return self.__connected

    def is_stopped(
        self
    ):
        return self.stopped.is_set()

    # ========================================================
    # ThingsBoard -> LocalProcessor Scenario RPC
    # ========================================================

    def server_side_rpc_handler(
        self,
        content
    ):

        self._log.warning(
            "=== SCENARIO RPC RECEIVED ==="
        )

        self._log.warning(
            "RPC CONTENT: %s",
            content
        )

        data = content.get(
            "data",
            {}
        )

        method = data.get(
            "method"
        )

        params = data.get(
            "params"
        )

        if not isinstance(
            params,
            dict
        ):
            params = {}

        request_id = data.get(
            "id"
        )

        device_name = content.get(
            "device",
            self.__device_name
        )

        try:

            # ================================================
            # Get all scenarios
            # ================================================

            if method == "getScenarios":

                result = (
                    self.__local_processor_client
                    .get_scenarios()
                )

            # ================================================
            # Get one scenario
            # ================================================

            elif method == "getScenario":

                name = params.get(
                    "name"
                )

                if not name:
                    raise ValueError(
                        "Scenario name is required"
                    )

                result = (
                    self.__local_processor_client
                    .get_scenario(
                        name
                    )
                )

            # ================================================
            # Create scenario
            # ================================================

            elif method == "createScenario":

                name = params.get(
                    "name"
                )

                actions = params.get(
                    "actions",
                    []
                )

                description = params.get(
                    "description",
                    ""
                )

                if not name:
                    raise ValueError(
                        "Scenario name is required"
                    )

                result = (
                    self.__local_processor_client
                    .create_scenario(
                        name,
                        actions,
                        description
                    )
                )

            # ================================================
            # Update scenario
            # ================================================

            elif method == "updateScenario":

                old_name = (
                    params.get(
                        "oldName"
                    )
                    or
                    params.get(
                        "old_name"
                    )
                    or
                    params.get(
                        "name"
                    )
                )

                new_name = (
                    params.get(
                        "newName"
                    )
                    or
                    params.get(
                        "new_name"
                    )
                    or
                    params.get(
                        "name"
                    )
                )

                actions = params.get(
                    "actions",
                    []
                )

                description = params.get(
                    "description",
                    ""
                )

                if not old_name:
                    raise ValueError(
                        "Old scenario name is required"
                    )

                if not new_name:
                    raise ValueError(
                        "New scenario name is required"
                    )

                result = (
                    self.__local_processor_client
                    .update_scenario(
                        old_name,
                        new_name,
                        actions,
                        description
                    )
                )

            # ================================================
            # Delete scenario
            # ================================================

            elif method == "deleteScenario":

                name = params.get(
                    "name"
                )

                if not name:
                    raise ValueError(
                        "Scenario name is required"
                    )

                result = (
                    self.__local_processor_client
                    .delete_scenario(
                        name
                    )
                )

            # ================================================
            # Run scenario
            # ================================================

            elif method == "runScenario":

                name = params.get(
                    "name"
                )

                if not name:
                    raise ValueError(
                        "Scenario name is required"
                    )

                result = (
                    self.__local_processor_client
                    .run_scenario(
                        name
                    )
                )

            # ================================================
            # Unknown ScenarioConnector RPC
            # ================================================

            else:

                result = {
                    "success": False,
                    "error": (
                        "Unsupported RPC method: "
                        + str(
                            method
                        )
                    )
                }

            # ================================================
            # This reply belongs to REAL ThingsBoard RPC sent
            # to ScenarioConnector, so replying is correct.
            # ================================================

            if request_id is not None:

                self.__gateway.send_rpc_reply(
                    device_name,
                    request_id,
                    result
                )

            self._log.warning(
                "=== SCENARIO RPC RESPONSE"
                " | method=%s"
                " | result=%s ===",
                method,
                result
            )

            return result

        except Exception as e:

            self._log.exception(
                "=== SCENARIO RPC ERROR"
                " | method=%s"
                " | error=%s ===",
                method,
                e
            )

            result = {
                "success": False,
                "error": str(
                    e
                )
            }

            try:

                if request_id is not None:

                    self.__gateway.send_rpc_reply(
                        device_name,
                        request_id,
                        result
                    )

            except Exception as reply_error:

                self._log.error(
                    "Failed to send RPC error reply: %s",
                    reply_error
                )

            return result

    # ========================================================
    # ThingsBoard -> ScenarioConnector attributes
    # ========================================================

    def on_attributes_update(
        self,
        content
    ):

        self._log.warning(
            "=== SCENARIO ATTRIBUTE UPDATE"
            " | content=%s ===",
            content
        )
