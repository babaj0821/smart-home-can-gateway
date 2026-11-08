from copy import deepcopy
from threading import RLock


class StateStore:
    def __init__(self):
        self._devices = {}
        self._lock = RLock()

    def update(self, converted_data):
        if not isinstance(converted_data, dict):
            return None

        device_name = (
            converted_data.get("deviceName")
            or converted_data.get("device")
        )

        if not device_name:
            return None

        with self._lock:
            current = self._devices.get(
                device_name,
                {
                    "deviceName": device_name,
                    "deviceType": converted_data.get(
                        "deviceType",
                        "default"
                    ),
                    "attributes": {},
                    "telemetry": []
                }
            )

            device_type = converted_data.get("deviceType")

            if device_type is not None:
                current["deviceType"] = device_type

            attributes = converted_data.get("attributes")

            if isinstance(attributes, dict):
                current["attributes"].update(attributes)

            telemetry = converted_data.get("telemetry")

            if isinstance(telemetry, list):
                current["telemetry"] = deepcopy(telemetry)

            elif isinstance(telemetry, dict):
                current["telemetry"] = [
                    deepcopy(telemetry)
                ]

            self._devices[device_name] = current

            return deepcopy(current)

    def get(self, device_name):
        with self._lock:
            data = self._devices.get(device_name)

            if data is None:
                return {}

            return deepcopy(data)

    def device_names(self):
        with self._lock:
            return list(self._devices.keys())

    def all(self):
        with self._lock:
            return deepcopy(self._devices)
