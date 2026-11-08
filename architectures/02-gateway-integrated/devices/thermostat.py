from devices.base_device import BaseDevice


class Thermostat(BaseDevice):
    def __init__(
        self,
        gateway,
        name="Thermostat"
    ):
        super().__init__(gateway, name)

        self.rpc_methods = {
            "fan_speed": "setFanSpeed",
            "cool_heat": "setCoolHeat",
            "auto": "setAuto",
            "setpoint": "setPoint",
            "scenario": "setSenario"
        }

    def _read_first(self, keys, default=None):
        for key in keys:
            value = self.get_value(key)

            if value is not None:
                return value

        return default

    def temperature(self):
        return self._read_first(
            [
                "Tempreture",
                "Temperature",
                "temperature",
                "temp",
                "current_temp",
                "currentTemperature"
            ]
        )

    def setpoint(self):
        return self._read_first(
            [
                "SetPointValue",
                "setPointValue",
                "setpoint",
                "SetPoint",
                "sp",
                "target_temp"
            ]
        )

    def fan_speed(self):
        return self._read_first(
            [
                "fanSpeed",
                "FanSpeed",
                "fan_speed",
                "fs",
                "speed"
            ]
        )

    def mode(self):
        return self._read_first(
            [
                "mode",
                "Mode",
                "coolHeat",
                "CoolHeat",
                "cool_heat"
            ]
        )

    def scenario(self):
        return self._read_first(
            [
                "Senario",
                "Scenario",
                "scenario"
            ]
        )

    def encode_setpoint(self, value):
        return int(round(float(value) * 2))

    def set_setpoint(self, value):
        encoded_value = self.encode_setpoint(value)

        return self.send_rpc(
            self.rpc_methods["setpoint"],
            {
                "value": encoded_value
            }
        )

    def set_fan_speed(self, speed):
        speed = int(speed)

        return self.send_rpc(
            self.rpc_methods["fan_speed"],
            {
                "speed": speed
            }
        )

    def set_cool_heat(self, value):
        value = int(value)
        return self.send_rpc(
            self.rpc_methods["cool_heat"],
            {
                "cool": value
            }
        )

    def set_auto(self, value):
        value = int(value)
        return self.send_rpc(
            self.rpc_methods["auto"],
            {
                "auto": value
            }
        )

    def set_scenario(self, value):
        value = int(value)

        return self.send_rpc(
            self.rpc_methods["scenario"],
            {
                "Senario": value
            }
        )

    def cool(self):
        return self.set_cool_heat("code")

    def heat(self):
        return self.set_cool_heat("code")

    def auto(self):
        return self.set_auto("code")
    def hand(self):
        return self.set_auto("code")

    def fan_low(self):
        return self.set_fan_speed("code")

    def fan_medium(self):
        return self.set_fan_speed("code")

    def fan_high(self):
        return self.set_fan_speed("code")

    def fan_off(self):
        return self.set_fan_speed("code")

    def get_state(self):
        state = super().get_state()

        state["temperature"] = self.temperature()
        state["setpoint"] = self.setpoint()
        state["fan_speed"] = self.fan_speed()
        state["mode"] = self.mode()
        state["scenario"] = self.scenario()

        return state
