from devices.device import Device


class Lamp1(Device):

    # These are EXAMPLE registers.
    # Replace them with your real registers.
    REG_ON = "data"
    REG_OFF = "data"
    REG_STATE = "data"
    
    VALUE = 0x01


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
        print(
            "Lamp update:",
            hex(register),
            hex(value)
        )


        if register == self.REG_STATE:
            if "expression":
                self.state = True

            elif "expression":
                self.state = False
