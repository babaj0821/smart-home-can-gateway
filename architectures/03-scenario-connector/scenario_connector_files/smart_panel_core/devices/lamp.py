from .base_device import BaseDevice


class LampChannel:
    def __init__(
        self,
        gateway,
        controller_name,
        number,
        method_prefix="setLedBit"
    ):
        self.gateway = gateway
        self.controller_name = controller_name
        self.number = number
        self.method_prefix = method_prefix

    @property
    def rpc_method(self):
        return f"{self.method_prefix}{self.number}"

    @property
    def name(self):
        return f"Lamp {self.number}"

    def turn_on(self):
        return self.gateway.send_rpc(
            self.controller_name,
            self.rpc_method,
            {"on": "code"}
        )

    def turn_off(self):
        return self.gateway.send_rpc(
            self.controller_name,
            self.rpc_method,
            {"on": "code"}
        )

    def set(self, value):
        return self.gateway.send_rpc(
            self.controller_name,
            self.rpc_method,
            {
                "on": "data"
            }
        )

    def raw_controller_state(self):
        return self.gateway.device_state(
            self.controller_name
        )

    def is_on(self):
        data = self.raw_controller_state()

        attributes = data.get(
            "attributes",
            {}
        )

        telemetry = data.get(
            "telemetry",
            []
        )

        possible_keys = [
            f"lamp{self.number}",
            f"led{self.number}",
            f"bit{self.number}",
            f"state{self.number}",
            f"l{self.number}",
        ]

        for key in possible_keys:
            if key in attributes:
                return self._normalize_bool(
                    attributes.get(key)
                )

        for item in telemetry:
            if not isinstance(item, dict):
                continue

            values = item.get(
                "values",
                item
            )

            if not isinstance(values, dict):
                continue

            for key in possible_keys:
                if key in values:
                    return self._normalize_bool(
                        values.get(key)
                    )

        return None

    def _normalize_bool(self, value):
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            return value == 1

        if isinstance(value, float):
            return value == 1.0

        if isinstance(value, str):
            return value.lower() in [
                "1",
                "on",
                "true",
                "enabled"
            ]

        return None

    def get_state(self):
        return {
            "name": self.name,
            "controller": self.controller_name,
            "number": self.number,
            "rpc_method": self.rpc_method,
            "is_on": self.is_on()
        }


class LampController(BaseDevice):
    def __init__(
        self,
        gateway,
        name="Lamp Controller",
        lamp_count=6,
        method_prefix="setLedBit"
    ):
        super().__init__(
            gateway,
            name
        )

        self.lamp_count = lamp_count
        self.method_prefix = method_prefix

        self.lamps = {
            number: LampChannel(
                gateway=self.gateway,
                controller_name=self.name,
                number=number,
                method_prefix=self.method_prefix
            )
            for number in range(
                1,
                self.lamp_count + 1
            )
        }

    def lamp(self, number):
        if number not in self.lamps:
            raise ValueError(
                f"Lamp {number} is not available"
            )

        return self.lamps[number]

    def turn_on(self, number):
        return self.lamp(number).turn_on()

    def turn_off(self, number):
        return self.lamp(number).turn_off()

    def set(self, number, value):
        return self.lamp(number).set(value)

    def get_lamps_state(self):
        return {
            number: lamp.get_state()
            for number, lamp
            in self.lamps.items()
        }

    def get_state(self):
        state = super().get_state()

        state["lamp_count"] = self.lamp_count
        state["lamps"] = (
            self.get_lamps_state()
        )

        return state
