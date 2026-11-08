import threading
import time

from canbus.can_interface import CANInterface
from canbus.can_protocol import CANProtocol
from devices.lamp1 import Lamp1
from devices.lamp2 import Lamp2
from devices.lamp3 import Lamp3
from devices.lamp4 import Lamp4
from devices.lamp5 import Lamp5
from devices.lamp6 import Lamp6
from core.device_manager import DeviceManager
from devices.Thermostat import Thermostate
from core.scenario_engine import ScenarioEngine
from ui.scenario_menu import scenario_menu
from integrations.thingsboard.scenario_bridge import (
    ScenarioBridge
)
can = CANInterface("can0")
protocol = CANProtocol()

thermostat = Thermostate(
	device_id=0x34,
	name = "living room thermostate",
	can_interface = can,
	protocol=protocol
)
lamp1 = Lamp1(
    device_id=0x02,
    name="Living Room Lamp",
    can_interface=can,
    protocol=protocol
)
lamp2 = Lamp2(
    device_id=0x02,
    name="Living Room Lamp",
    can_interface=can,
    protocol=protocol
)
lamp3 = Lamp3(
    device_id=0x02,
    name="Living Room Lamp",
    can_interface=can,
    protocol=protocol
)
lamp4 = Lamp4(
    device_id=0x02,
    name="Living Room Lamp",
    can_interface=can,
    protocol=protocol
)
lamp5 = Lamp5(
    device_id=0x02,
    name="Living Room Lamp",
    can_interface=can,
    protocol=protocol
)
lamp6 = Lamp6(
    device_id=0x02,
    name="Living Room Lamp",
    can_interface=can,
    protocol=protocol
)
device_manager = DeviceManager()
device_manager.add_lamp(lamp1 , 1)
device_manager.add_lamp(lamp2 , 2)
device_manager.add_lamp(lamp3 , 3)
device_manager.add_lamp(lamp4 , 4)
device_manager.add_lamp(lamp5 , 5)
device_manager.add_lamp(lamp6 , 6)
device_manager.add_device(thermostat)
scenario_engine = ScenarioEngine(
    device_manager,
    thermostat
)
tb_bridge = ScenarioBridge(
    scenario_engine
)

tb_bridge.connect()
def receive_loop():
    while True:
        can_id, data = can.receive()

        message = protocol.decode_frame(
            can_id,
            data
        )

        print(
            "RX:",
            hex(message["can_id"]),
            "OP:", message["operation"],
            "DEVICE:", hex(message["device_id"]),
            "REG:", hex(message["register"]),
            "VALUE:", hex(message["value"])
        )
        if message["device_id"] == 0x02:
            for i in range (1 , 7):
                print("sent")
                device_manager.handle_message(message , i)
        else:
            device_manager.handle_message(message , -1)

def clear_screen():
    print("\033[2J\033[H", end="")

try:
    can.connect()

    print("CAN connected")


    receiver_thread = threading.Thread(
        target=receive_loop,
        daemon=True
    )

    receiver_thread.start()


    while True:
        clear_screen()
        print(
            "\n"
            "========== MAIN MENU ==========\n"
            "1 = Lamps\n"
            "2 = Thermostat\n"
            "3 = Scenarios\n"
            "s = Show all states\n"
            "q = Quit\n"
            "===============================\n"
        )

        command = input("> ").strip().lower()

        if command == "q":
            break

        elif command == "1":
            while True:
                clear_screen()
                print(
                    "\n"
                    "========== LAMP MENU ==========\n"
                    "1 = Lamp 1 ON\n"
                    "2 = Lamp 1 OFF\n"
                    "3 = Lamp 2 ON\n"
                    "4 = Lamp 2 OFF\n"
                    "5 = Lamp 3 ON\n"
                    "6 = Lamp 3 OFF\n"
                    "7 = Lamp 4 ON\n"
                    "8 = Lamp 4 OFF\n"
                    "9 = Lamp 5 ON\n"
                    "10 = Lamp 5 OFF\n"
                    "11 = Lamp 6 ON\n"
                    "12 = Lamp 6 OFF\n"
                    "b = Back\n"
                    "===============================\n"
                )

                lamp_command = input("> ").strip().lower()

                if lamp_command == "b":
                    break

                elif lamp_command == "1":
                    lamp1.turn_on()
                    print("Lamp 1 ON command sent")

                elif lamp_command == "2":
                    lamp1.turn_off()
                    print("Lamp 1 OFF command sent")
                
                elif lamp_command == "3":
                    lamp2.turn_on()
                    print("Lamp 2 ON command sent")

                elif lamp_command == "4":
                    lamp2.turn_off()
                    print("Lamp 2 OFF command sent")

                elif lamp_command == "5":
                    lamp3.turn_on()
                    print("Lamp 3 ON command sent")

                elif lamp_command == "6":
                    lamp3.turn_off()
                    print("Lamp 3 OFF command sent")

                elif lamp_command == "7":
                    lamp4.turn_on()
                    print("Lamp 4 ON command sent")

                elif lamp_command == "8":
                    lamp4.turn_off()
                    print("Lamp 4 OFF command sent")

                elif lamp_command == "9":
                    lamp5.turn_on()
                    print("Lamp 5 ON command sent")

                elif lamp_command == "10":
                    lamp5.turn_off()
                    print("Lamp 5 OFF command sent")

                elif lamp_command == "11":
                    lamp6.turn_on()
                    print("Lamp 6 ON command sent")

                elif lamp_command == "12":
                    lamp6.turn_off()
                    print("Lamp 6 OFF command sent")

                else:
                    print("Unknown lamp command")

        elif command == "2":
            while True:
                clear_screen()
                print(
                    "\n"
                    "======= THERMOSTAT MENU =======\n"
                    "1 = Set SP\n"
                    "2 = Cooling Mode\n"
                    "3 = Heating Mode\n"
                    "4 = Auto Mode\n"
                    "5 = Hand Mode\n"
                    "6 = Fan Speed\n"
                    "7 = Request Thermostat State\n"
                    "8 = Request SP\n"
                    "s = Show Thermostat State\n"
                    "b = Back\n"
                    "===============================\n"
                )

                thermo_command = input("> ").strip().lower()

                if thermo_command == "b":
                    break

                elif thermo_command == "1":
                    try:
                        temperature = float(
                            input("Set temperature: ")
                        )

                        thermostat.set_sp(
                            temperature
                        )

                        print(
                            f"Setpoint sent: {temperature}"
                        )

                    except ValueError:
                        print("Invalid temperature")

                elif thermo_command == "2":
                    thermostat.set_ch_cool()
                    print("Cooling mode command sent")

                elif thermo_command == "3":
                    thermostat.set_ch_heat()
                    print("Heating mode command sent")

                elif thermo_command == "4":
                    thermostat.set_auto()
                    print("Auto mode command sent")

                elif thermo_command == "5":
                    thermostat.set_hand()
                    print("Hand mode command sent")

                elif thermo_command == "6":
                    try:
                        fan_speed = int(
                            input("Fan speed [0-3]: ")
                        )

                        if fan_speed == 0:
                            thermostat.set_fs0()

                        elif fan_speed == 1:
                            thermostat.set_fs1()

                        elif fan_speed == 2:
                            thermostat.set_fs2()

                        elif fan_speed == 3:
                            thermostat.set_fs3()

                        else:
                            print("Fan speed must be 0 to 3")
                            continue

                        print(
                            f"Fan speed sent: {fan_speed}"
                        )

                    except ValueError:
                        print("Invalid fan speed")

                elif thermo_command == "7":
                    thermostat.request_state()
                    print("Thermostat state requested")

                elif thermo_command == "8":
                    thermostat.request_sp()
                    print("SP requested")

                elif thermo_command == "s":
                    print(
                        "\n--- THERMOSTAT STATE ---"
                    )

                    print(
                        thermostat.state
                    )
                    time.sleep(5)

                else:
                    print("Unknown thermostat command")

        elif command == "s":
            print(
                "\n--- CURRENT STATES ---"
            )

            print(
                "Lamp 1:",
                lamp1.state
            )
            print(
                "Lamp 2:",
                lamp2.state
            )
            print(
                "Lamp 3:",
                lamp3.state
            )
            print(
                "Lamp 4:",
                lamp4.state
            )
            print(
                "Lamp 5:",
                lamp5.state
            )
            print(
                "Lamp 6:",
                lamp6.state
            )

            print(
                "Thermostat:",
                thermostat.state
            )
            time.sleep(10)
        elif command == "3":
            scenario_menu(
                scenario_engine
            )
        else:
            print("Unknown command")



except KeyboardInterrupt:

    print("\nStopped by user")


finally:

    can.close()

    print("CAN closed")
