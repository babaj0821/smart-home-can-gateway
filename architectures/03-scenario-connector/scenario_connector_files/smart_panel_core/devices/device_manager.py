from .base_device import BaseDevice
from .lamp import LampController
from .thermostat import Thermostat
from .device_registry import DeviceRegistry


class DeviceManager:

    def __init__(
        self,
        gateway,
        registry=None
    ):

        self.gateway = gateway

        self.registry = (
            registry
            if registry is not None
            else DeviceRegistry()
        )

        self.devices = {}

        self.load_registry()

        self.refresh()


    def load_registry(
        self
    ):

        registered_devices = (
            self.registry.get_devices()
        )


        for name in registered_devices:

            if name not in self.devices:

                self.devices[name] = (
                    self._create_device(name)
                )


    def refresh(
        self
    ):

        current_names = (
            self.gateway.devices()
        )


        for name in current_names:

            if not self.registry.exists(
                name
            ):

                self.registry.register_device(
                    name,
                    self.detect_type(name)
                )


            if name not in self.devices:

                self.devices[name] = (
                    self._create_device(name)
                )


        return self.devices


    def detect_type(
        self,
        name
    ):

        normalized = name.lower()


        if (
            "lamp" in normalized
            or "light" in normalized
            or "led" in normalized
        ):

            return "lamp"


        if "thermostat" in normalized:

            return "thermostat"


        return "generic"



    def _create_device(
        self,
        name
    ):

        normalized = name.lower()


        if (
            "lamp" in normalized
            or "light" in normalized
            or "led" in normalized
        ):

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


    def all(
        self
    ):

        return list(
            self.devices.values()
        )


    def names(
        self
    ):

        return list(
            self.devices.keys()
        )


    def get(
        self,
        name
    ):

        return self.devices.get(
            name
        )


    def get_required(
        self,
        name
    ):

        device = self.get(
            name
        )


        if device is None:

            raise ValueError(
                f"Device not found: {name}"
            )


        return device



    def find_by_class(
        self,
        class_name
    ):

        for device in self.devices.values():

            if (
                device.__class__.__name__
                ==
                class_name
            ):

                return device


        return None



    def lamps(
        self
    ):

        device = self.find_by_class(
            "LampController"
        )


        if device is None:

            raise ValueError(
                "Lamp Controller not found"
            )


        return device



    def thermostat(
        self
    ):

        device = self.find_by_class(
            "Thermostat"
        )


        if device is None:

            raise ValueError(
                "Thermostat not found"
            )


        return device



    def state_all(
        self
    ):

        result = {}


        for name, device in self.devices.items():

            result[name] = (
                device.get_state()
            )


        return result
