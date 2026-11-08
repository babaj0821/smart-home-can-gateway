import time


class ScenarioEngine:

    def __init__(
        self,
        device_manager,
        thermostat
    ):
        self.device_manager = device_manager
        self.thermostat = thermostat

    def run(self, scenario):
        if scenario is None:
            raise ValueError(
                "Scenario not found"
            )

        actions = scenario.get(
            "actions",
            []
        )

        for action in actions:
            self.execute_action(
                action
            )

            delay = action.get(
                "delay",
                0
            )

            if delay > 0:
                time.sleep(
                    delay
                )

    def execute_action(
        self,
        action
    ):
        device_type = action.get(
            "device"
        )

        if device_type == "lamp":
            self.execute_lamp(
                action
            )

        elif device_type == "thermostat":
            self.execute_thermostat(
                action
            )

        else:
            raise ValueError(
                f"Unknown device type: {device_type}"
            )

    def execute_lamp(
        self,
        action
    ):
        number = action.get(
            "number"
        )

        lamp = self.device_manager.get_lamp(
            number
        )

        if lamp is None:
            raise ValueError(
                f"Lamp {number} not found"
            )

        command = action.get(
            "action"
        )

        if command == "turn_on":
            lamp.turn_on()

        elif command == "turn_off":
            lamp.turn_off()

        elif command == "request_state":
            lamp.request_state()

        else:
            raise ValueError(
                f"Unknown lamp action: {command}"
            )

    def execute_thermostat(
        self,
        action
    ):
        command = action.get(
            "action"
        )

        if command == "set_sp":
            self.thermostat.set_sp(
                action["value"]
            )

        elif command == "set_auto":
            self.thermostat.set_auto()

        elif command == "set_hand":
            self.thermostat.set_hand()

        elif command == "set_cool":
            self.thermostat.set_ch_cool()

        elif command == "set_heat":
            self.thermostat.set_ch_heat()

        elif command == "set_fan_speed":
            speed = int(
                action["value"]
            )

            fan_methods = {
                "code": self.thermostat.set_fs0,
                "code": self.thermostat.set_fs1,
                "code": self.thermostat.set_fs2,
                "code": self.thermostat.set_fs3
            }

            method = fan_methods.get(
                speed
            )

            if method is None:
                raise ValueError(
                    f"Invalid fan speed: {speed}"
                )

            method()

        elif command == "request_state":
            self.thermostat.request_state()

        else:
            raise ValueError(
                f"Unknown thermostat action: {command}"
            )
