from .command_outbox import CommandOutbox
from .state_store import StateStore
from .local_gateway import LocalGateway
from .devices.device_manager import DeviceManager
from .scenario.scenario_storage import ScenarioStorage
from .scenario.scenario_engine import ScenarioEngine


class LocalProcessor:

    def __init__(
        self,
        logger=None
    ):
        self._log = logger

        self.state_store = StateStore()

        self.command_outbox = CommandOutbox(
            maxsize=1000
        )

        self.gateway = LocalGateway(
            self.state_store,
            self.command_outbox
        )

        self.devices = DeviceManager(
            self.gateway
        )

        self.scenario_storage = ScenarioStorage()

        self.scenario_engine = ScenarioEngine(
            self.scenario_storage,
            self.gateway,
            self.devices
        )

        self._log_message(
            "=== LOCAL PROCESSOR INITIALIZED ==="
        )

    # ========================================================
    # Telemetry
    # ========================================================

    def handle_can_telemetry(
        self,
        payload
    ):
        state = self.state_store.update(
            payload
        )

        if state is None:
            self._log_message(
                "=== LOCAL PROCESSOR IGNORED INVALID TELEMETRY ==="
            )
            return None

        self.devices.refresh()

        device_name = state.get(
            "deviceName"
        )

        device = self.devices.get(
            device_name
        )

        self._log_message(
            "=== LOCAL PROCESSOR TELEMETRY | device=%s ===",
            device_name
        )

        if device is not None:
            self._log_message(
                "LOCAL DEVICE STATE: %s",
                device.get_state()
            )

        return state

    # ========================================================
    # Devices
    # ========================================================

    def device_names(self):
        return self.devices.names()

    def get_device(
        self,
        name
    ):
        return self.devices.get(
            name
        )

    def get_state(
        self,
        name
    ):
        device = self.devices.get(
            name
        )

        if device is None:
            return {}

        return device.get_state()

    def get_all_states(self):
        return self.devices.state_all()

    def send_device_command(
        self,
        device,
        method,
        params=None
    ):
        return self.gateway.send_rpc(
            device,
            method,
            params or {}
        )

    def execute_device_action(
        self,
        device_name,
        action,
        params=None
    ):
        """
        Execute a semantic Smart Panel action.

        The UI talks in semantic actions such as:
            Lamp Controller / turn_on / {"number": 1}
            Thermostat / set_sp / {"value": 23}

        The actual device class converts that semantic action
        into the configured CAN RPC method and pushes it into
        LocalGateway -> CommandOutbox.
        """

        params = params or {}

        if not isinstance(
            params,
            dict
        ):
            raise ValueError(
                "params must be an object"
            )

        device_name = str(
            device_name or ""
        ).strip()

        action = str(
            action or ""
        ).strip()

        if not device_name:
            raise ValueError(
                "device is required"
            )

        if not action:
            raise ValueError(
                "action is required"
            )

        device = self.devices.get(
            device_name
        )

        if device is None:
            raise ValueError(
                f"Device not found: {device_name}"
            )

        device_type = device.__class__.__name__

        # ====================================================
        # Lamp Controller
        # ====================================================

        if device_type == "LampController":

            if "number" not in params:
                raise ValueError(
                    "Lamp action requires params.number"
                )

            number = int(
                params["number"]
            )

            if action == "turn_on":
                result = device.turn_on(
                    number
                )

            elif action == "turn_off":
                result = device.turn_off(
                    number
                )

            elif action == "set":

                if "value" not in params:
                    raise ValueError(
                        "Lamp set action requires params.value"
                    )

                result = device.set(
                    number,
                    bool(
                        params["value"]
                    )
                )

            else:
                raise ValueError(
                    f"Unsupported Lamp action: {action}"
                )

        # ====================================================
        # Thermostat
        # ====================================================

        elif device_type == "Thermostat":

            if action in (
                "set_sp",
                "set_setpoint"
            ):

                if "value" not in params:
                    raise ValueError(
                        "Set point action requires params.value"
                    )

                result = device.set_setpoint(
                    params["value"]
                )

            elif action == "set_fan_speed":

                if "value" not in params:
                    raise ValueError(
                        "set_fan_speed requires params.value"
                    )

                result = device.set_fan_speed(
                    params["value"]
                )

            elif action in (
                "set_cool",
                "cool"
            ):
                result = device.cool()

            elif action in (
                "set_heat",
                "heat"
            ):
                result = device.heat()

            elif action in (
                "set_auto",
                "auto"
            ):
                result = device.auto()

            elif action in (
                "set_hand",
                "hand",
                "manual"
            ):
                result = device.hand()

            elif action == "fan_low":
                result = device.fan_low()

            elif action == "fan_medium":
                result = device.fan_medium()

            elif action == "fan_high":
                result = device.fan_high()

            elif action == "fan_off":
                result = device.fan_off()

            elif action == "set_scenario":

                if "value" not in params:
                    raise ValueError(
                        "set_scenario requires params.value"
                    )

                result = device.set_scenario(
                    params["value"]
                )

            else:
                raise ValueError(
                    f"Unsupported Thermostat action: {action}"
                )

        # ====================================================
        # Generic / unsupported device
        # ====================================================

        else:
            raise ValueError(
                "Device does not support local semantic actions: "
                f"{device_name}"
            )

        return {
            "success": True,
            "accepted": True,
            "device": device_name,
            "action": action,
            "result": result
        }

    # ========================================================
    # Scenario management
    # ========================================================

    def create_scenario(
        self,
        name,
        actions,
        description=""
    ):
        return self.scenario_engine.create_scenario(
            name,
            actions,
            description
        )

    def get_scenarios(self):
        return self.scenario_engine.list_scenarios()

    def get_scenario(
        self,
        name
    ):
        return self.scenario_engine.get_scenario(
            name
        )

    def update_scenario(
        self,
        old_name,
        new_name,
        actions,
        description=""
    ):
        return self.scenario_engine.update_scenario(
            old_name,
            new_name,
            actions,
            description
        )

    def run_scenario(
        self,
        name
    ):
        return self.scenario_engine.run_scenario(
            name
        )

    def delete_scenario(
        self,
        name
    ):
        return self.scenario_engine.delete_scenario(
            name
        )

    # ========================================================
    # Command outbox
    # ========================================================

    def pull_commands(
        self,
        limit=100
    ):
        return self.command_outbox.pull(
            limit
        )

    def command_queue_size(self):
        return self.command_outbox.qsize()

    # ========================================================
    # Logging
    # ========================================================

    def _log_message(
        self,
        message,
        *args
    ):
        if self._log is not None:
            self._log.warning(
                message,
                *args
            )
            return

        if args:
            message = message % args

        print(
            message,
            flush=True
        )

