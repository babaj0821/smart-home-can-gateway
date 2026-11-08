class DeviceManager:

    def __init__(self):
        self.devices = {}
        self.lamps = {}

    def add_device(self, device):
        self.devices[
            device.device_id
        ] = device

    def add_lamp(self, device, number):
        self.devices[
            (device.device_id, number)
        ] = device

        self.lamps[
            number
        ] = device

    def get_device(self, device_id):
        return self.devices.get(
            device_id
        )

    def get_device_lamp(
        self,
        device_id,
        number
    ):
        return self.devices.get(
            (device_id, number)
        )

    def get_lamp(self, number):
        return self.lamps.get(
            number
        )
    def handle_message(self, message, number):

        device_id = message["device_id"]

        if device_id == "len":
            device = self.get_device_lamp(
                device_id,
                number
            )
        else:
            device = self.get_device(
                device_id
            )

        if device is None:
            print(
                "Unknown device:",
                hex(device_id),
                "number:",
                number
            )
            return

        device.update_state(
            message["register"],
            message["value"]
        )
