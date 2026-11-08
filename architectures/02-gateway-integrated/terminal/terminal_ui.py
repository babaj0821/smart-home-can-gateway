import os
import time
import json

from gateway.gateway_client import GatewayClient
from devices.device_manager import DeviceManager


class TerminalUI:
    def __init__(self):
        self.gateway = None
        self.devices = None
        self.lamps = None
        self.thermostat = None
        self.running = True

    def clear(self):
        os.system("clear")

    def pause(self):
        input("\nPress Enter to continue...")

    def print_json(self, data):
        print(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            )
        )

    def connect(self):
        self.clear()

        print("Smart Panel V2")
        print("==============================")
        print("Connecting to ThingsBoard Gateway...")
        print()

        self.gateway = GatewayClient()
        self.devices = DeviceManager(self.gateway)

        self.lamps = self.devices.lamps()
        self.thermostat = self.devices.thermostat()

        print("Connected successfully.")
        time.sleep(1)

    def header(self):
        self.clear()

        print("Smart Panel V2")
        print("==============================")
        print("Local Terminal Control Panel")
        print("==============================")
        print()

    def main_menu(self):
        while self.running:
            self.header()

            print("Main Menu")
            print("------------------------------")
            print("1) Show all device states")
            print("2) Lamp control")
            print("3) Thermostat control")
            print("4) Refresh devices")
            print("0) Exit")
            print()

            choice = input("Select: ").strip()

            if choice == "1":
                self.show_all_states()

            elif choice == "2":
                self.lamp_menu()

            elif choice == "3":
                self.thermostat_menu()

            elif choice == "4":
                self.refresh_devices()

            elif choice == "0":
                self.running = False

            else:
                print("Invalid command.")
                self.pause()

    def refresh_devices(self):
        self.header()

        print("Refreshing devices...")
        self.devices.refresh()

        self.lamps = self.devices.lamps()
        self.thermostat = self.devices.thermostat()

        print("Refresh completed.")
        self.pause()

    def show_all_states(self):
        self.header()

        print("All Device States")
        print("------------------------------")
        print()

        self.print_json(
            self.devices.state_all()
        )

        self.pause()

    def lamp_menu(self):
        while True:
            self.header()

            print("Lamp Control")
            print("------------------------------")
            print("1) Show lamp states")
            print("2) Turn lamp ON")
            print("3) Turn lamp OFF")
            print("4) Turn all lamps ON")
            print("5) Turn all lamps OFF")
            print("0) Back")
            print()

            choice = input("Select: ").strip()

            if choice == "1":
                self.show_lamp_states()

            elif choice == "2":
                self.control_single_lamp(True)

            elif choice == "3":
                self.control_single_lamp(False)

            elif choice == "4":
                self.turn_all_lamps(True)

            elif choice == "5":
                self.turn_all_lamps(False)

            elif choice == "0":
                break

            else:
                print("Invalid command.")
                self.pause()

    def show_lamp_states(self):
        self.header()

        print("Lamp States")
        print("------------------------------")
        print()

        self.print_json(
            self.lamps.get_state()
        )

        self.pause()

    def control_single_lamp(self, turn_on):
        self.header()

        print("Single Lamp Control")
        print("------------------------------")
        print()

        try:
            number = int(input("Lamp number 1-6: ").strip())

            if turn_on:
                result = self.lamps.turn_on(number)
                action = "ON"
            else:
                result = self.lamps.turn_off(number)
                action = "OFF"

            print()
            print(f"Lamp {number} -> {action}")
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print()
            print("Error:")
            print(e)

        self.pause()

    def turn_all_lamps(self, turn_on):
        self.header()

        try:
            if turn_on:
                result = self.lamps.all_on()
                action = "ON"
            else:
                result = self.lamps.all_off()
                action = "OFF"

            print(f"All lamps -> {action}")
            print()
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print("Error:")
            print(e)

        self.pause()

    def thermostat_menu(self):
        while True:
            self.header()

            print("Thermostat Control")
            print("------------------------------")
            print("1) Show thermostat state")
            print("2) Set point")
            print("3) Set fan speed")
            print("4) Set cool / heat")
            print("5) Set auto")
            print("6) Set scenario")
            print("0) Back")
            print()

            choice = input("Select: ").strip()

            if choice == "1":
                self.show_thermostat_state()

            elif choice == "2":
                self.set_thermostat_setpoint()

            elif choice == "3":
                self.set_thermostat_fan_speed()

            elif choice == "4":
                self.set_thermostat_cool_heat()

            elif choice == "5":
                self.set_thermostat_auto()

            elif choice == "6":
                self.set_thermostat_scenario()

            elif choice == "0":
                break

            else:
                print("Invalid command.")
                self.pause()

    def show_thermostat_state(self):
        self.header()

        print("Thermostat State")
        print("------------------------------")
        print()

        self.print_json(
            self.thermostat.get_state()
        )

        self.pause()

    def set_thermostat_setpoint(self):
        self.header()

        print("Set Thermostat Setpoint")
        print("------------------------------")
        print()

        try:
            value = float(input("Setpoint, example 24.5: ").strip())

            result = self.thermostat.set_setpoint(value)

            print()
            print(f"Setpoint command sent: {value}")
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print()
            print("Error:")
            print(e)

        self.pause()

    def set_thermostat_fan_speed(self):
        self.header()

        print("Set Fan Speed")
        print("------------------------------")
        print()

        try:
            speed = int(input("Fan speed value: ").strip())

            result = self.thermostat.set_fan_speed(speed)

            print()
            print(f"Fan speed command sent: {speed}")
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print()
            print("Error:")
            print(e)

        self.pause()

    def set_thermostat_cool_heat(self):
        self.header()

        print("Set Cool / Heat")
        print("------------------------------")
        print()

        try:
            value = int(input("Cool/Heat value: ").strip())

            result = self.thermostat.set_cool_heat(value)

            print()
            print(f"Cool/Heat command sent: {value}")
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print()
            print("Error:")
            print(e)

        self.pause()

    def set_thermostat_auto(self):
        self.header()

        print("Set Auto")
        print("------------------------------")
        print()

        try:
            value = int(input("Auto value: ").strip())

            result = self.thermostat.set_auto(value)

            print()
            print(f"Auto command sent: {value}")
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print()
            print("Error:")
            print(e)

        self.pause()

    def set_thermostat_scenario(self):
        self.header()

        print("Set Thermostat Scenario")
        print("------------------------------")
        print()

        try:
            value = int(input("Scenario value: ").strip())

            result = self.thermostat.set_scenario(value)

            print()
            print(f"Scenario command sent: {value}")
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print()
            print("Error:")
            print(e)

        self.pause()

    def run(self):
        try:
            self.connect()
            self.main_menu()

        except KeyboardInterrupt:
            print()
            print("Closed by user.")

        except Exception as e:
            print()
            print("Fatal error:")
            print(e)

        finally:
            print()
            print("Smart Panel stopped.")
