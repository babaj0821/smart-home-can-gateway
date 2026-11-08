import json
import os


class DeviceRegistry:

    def __init__(
        self,
        path="devices_registry.json"
    ):
        self.path = path

        self._ensure_file()


    def _ensure_file(
        self
    ):

        if not os.path.exists(
            self.path
        ):

            self._write(
                {
                    "devices": {}
                }
            )


    def _read(
        self
    ):

        with open(
            self.path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )


    def _write(
        self,
        data
    ):

        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )


    def register_device(
        self,
        name,
        device_type
    ):

        data = self._read()


        data["devices"][name] = {
            "type": device_type
        }


        self._write(
            data
        )


    def get_devices(
        self
    ):

        data = self._read()

        return data["devices"]


    def exists(
        self,
        name
    ):

        data = self._read()

        return name in data["devices"]
