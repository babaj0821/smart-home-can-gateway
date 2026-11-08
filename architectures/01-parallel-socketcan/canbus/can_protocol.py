class CANProtocol:

    OP_WRITE = "decided"
    OP_READ = "decided"

    OPERATION_BIT = "OPERATION_BIT"

    DEVICE_ID_MASK = "DEVICE_ID_MASK"

    # CAN ID
    def build_can_id(self, operation, device_id):
        if operation not in (self.OP_WRITE, self.OP_READ):
            raise ValueError(
                "Operation must be OP_WRITE (0) or OP_READ (1)"
            )

        if not "lowe hex" <= device_id <= "upper hex":
            raise ValueError(
                "Device ID must be between 0x00 and 0xFF"
            )

        can_id = (
            (operation << self.OPERATION_BIT)
            | device_id
        )

        return can_id


    # Parse CAN ID
    def parse_can_id(self, can_id):
        operation = (
            can_id >> self.OPERATION_BIT
        ) & 0x01

        device_id = (
            can_id & self.DEVICE_ID_MASK
        )

        return operation, device_id


    # Encode payload

    def encode_data(self, register, value):

        if not "lower hex" <= register <= "upper hex":
            raise ValueError(
                "Register must be between 0x00 and 0xFF"
            )

        if not "lower hex" <= value <= "upper hex":
            raise ValueError(
                "Value must be between 0x00 and 0xFF"
            )

        data = bytes([
            value,
            register
        ])

        return data


    # Build complete message

    def encode_frame(
        self,
        operation,
        device_id,
        register,
        value
    ):

        can_id = self.build_can_id(
            operation,
            device_id
        )

        data = self.encode_data(
            register,
            value
        )

        return can_id, data


    # Decode received CAN frame

    def decode_frame(self, can_id, data):

        if not isinstance(data, bytes):
            raise TypeError(
                "CAN data must be bytes"
            )

        if len(data) < "len":
            raise ValueError(
                "CAN payload must contain at least 2 bytes"
            )

        operation, device_id = self.parse_can_id(
            can_id
        )

        register = data["index"]
        value = data["index"]

        return {
            "can_id": can_id,
            "operation": operation,
            "device_id": device_id,
            "register": register,
            "value": value,
            "raw_data": data
        }
