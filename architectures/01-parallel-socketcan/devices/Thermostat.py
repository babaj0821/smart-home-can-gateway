from devices.device import Device


class Thermostate(Device):

    # These are EXAMPLE registers.
    # Replace them with your real registers.
    REG_TEMP = "data"
    REG_SP = "data"
    REG_STATE = "data"
    REG_FS = "data"
    REG_CH = "data"
    REG_HA = "data"

    MODE_COOL = "data"
    MODE_HEAT = "data"


    # ==========================================
    # Fan speed values
    # ==========================================

    FS_0 = "data"
    FS_1 = "data"
    FS_2 = "data"
    FS_3 = "data"
    AUTO = "data"
    HAND = "data"


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
        self.state = {
            "auto/hand": None,
            "mode": None,
            "room_temp": None,
            "setpoint": None,
            "fan": None
        }

    def set_fs0(self):
        self.write_register(
            self.REG_FS,
            self.FS_0
        )
    def set_fs1(self):
        self.write_register(
            self.REG_FS,
            self.FS_1
        )
    def set_fs2(self):
        self.write_register(
            self.REG_FS,
            self.FS_2
        )
    def set_fs3(self):
        self.write_register(
            self.REG_FS,
            self.FS_3
        )
    

    def set_ch_cool(self):
        self.write_register(
            self.REG_CH,
            self.MODE_COOL
        )
    def set_ch_heat(self):
        self.write_register(
            self.REG_CH,
            self.MODE_HEAT
        )

    def set_auto(self):
        self.write_register(
            self.REG_HA,
            self.AUTO
        )
    def set_hand(self):
        self.write_register(
            self.REG_HA,
            self.HAND
        )
    def set_sp(self , data):
        encoded_value = round(data * 2)
        self.write_register(
            self.REG_SP,
            encoded_value
        )

    def request_state(self):

        self.read_register(
            self.REG_STATE
        )
    def request_sp(self):

        self.read_register(
            self.REG_SP
        )
    def request_temp(self):

        self.read_register(
            self.REG_TEMP
	)

    def update_state(self, register, value):        
        if register != self.REG_STATE:
            if register == self.REG_TEMP:
                self.state["room_temp"] = value
            elif register == self.REG_SP:
                self.state["setpoint"] = value / 2
            else:
                return
        else:
            fan_s = "expressoin"
            if fan_s == 0:
                self.state["fan"] = "off"
            elif fan_s == 1:
                self.state["fan"] = "speed1"
            elif fan_s == 2:
                self.state["fan"] = "speed2"
            elif fan_s == 3:
                self.state["fan"]  = "speed3"

            if "expressoin":
                self.state["mode"] = "Cooling"
            elif "expressoin":
                self.state["mode"] = "Heating"
            

            if "expressoin":
                self.state["auto/hand"] = "Full hand"
            elif "expressoin":
                self.state["auto/hand"] = "Full auto"
