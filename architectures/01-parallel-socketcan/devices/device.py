class Device:

    def __init__(
        self,
        device_id,
        name,
        can_interface,
        protocol
    ):
        self.device_id = device_id
        self.name = name

        self.can = can_interface
        self.protocol = protocol

        self.state = None


    def write_register(self, register, value):
        """
        Write a value to one register.
        """

        can_id, data = self.protocol.encode_frame(
            self.protocol.OP_WRITE,
            self.device_id,
            register,
            value
        )

        self.can.send(
            can_id,
            data
        )


    def read_register(self, register):
        """
        Request/read one register.

        For now we send value = 0.
        This may change depending on your real protocol.
        """

        can_id, data = self.protocol.encode_frame(
            self.protocol.OP_READ,
            self.device_id,
            register,
            0
        )

        self.can.send(
            can_id,
            data
        )


    def update_state(self, register, value):
        """
        Called when new information about
        this device is received.

        Child classes will implement this.
        """

        pass

