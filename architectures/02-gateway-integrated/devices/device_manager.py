from devices.base_device import BaseDevice
from devices.lamp import LampController
from devices.thermostat import Thermostat


class DeviceManager:
    def __init__(self, gateway):
        self.gateway = gateway
        self.devices = {}

        self.refresh()

    def refresh(self):
        self.devices = {}

        device_names = self.gateway.devices()

        for name in device_names:
            self.devices[name] = self._create_device(name)

        return self.devices

    def _create_device(self, name):
        normalized = name.lower()

        if "lamp" in normalized or "light" in normalized:
            return LampController(
                self.gateway,
                name=name,
                lamp_count=6,
                method_prefix="setLedBit"
            )

        if "thermostat" in normalized:
            return Thermostat(
                self.gateway,
                name=name
            )

        return BaseDevice(
            self.gateway,
            name=name
        )

    def all(self):
        return list(self.devices.values())

    def names(self):
        return list(self.devices.keys())

    def get(self, name):
        return self.devices.get(name)

    def get_required(self, name):
        device = self.get(name)

        if device is None:
            raise ValueError(f"Device not found: {name}")

        return device

    def find_by_class(self, class_name):
        for device in self.devices.values():
            if device.__class__.__name__ == class_name:
                return device

        return None

    def lamps(self):
        device = self.find_by_class("LampController")

        if device is None:
            raise ValueError("Lamp Controller not found")

        return device

    def thermostat(self):
        device = self.find_by_class("Thermostat")

        if device is None:
            raise ValueError("Thermostat not found")

        return device

    def state_all(self):
        result = {}

        for name, device in self.devices.items():
            result[name] = device.get_state()

        return result

    def print_summary(self):
        print("Devices:")

        for name, device in self.devices.items():
            print()
            print("Name:", name)
            print("Type:", device.__class__.__name__)
            print("State:")
            print(device.get_state())
