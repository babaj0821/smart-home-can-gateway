from devices.device import Device


class Lamp3(Device):

    # These are EXAMPLE registers.
    # Replace them with your real registers.
    REG_ON = 0x01
    REG_OFF = 0x02
    REG_STATE = 0x00
    
    VALUE = 0x04


    def __init__(
        self,
        device_id,
        name,
        can_interface,
        protocol
    ):

        super().__init__(
            device_id,
            name,
            can_interface,
            protocol
        )


    def turn_on(self):

        self.write_register(
            self.REG_ON,
            self.VALUE
        )


    def turn_off(self):

        self.write_register(
            self.REG_OFF,
            self.VALUE
        )


    def request_state(self):

        self.read_register(
            self.REG_STATE
        )


    def update_state(self, register, value):

        if register != self.REG_STATE:
            return

        if ((value >> 2) & 1) == 1:
            self.state = True

        elif ((value >> 2) & 1) == 0:
            self.state = False
