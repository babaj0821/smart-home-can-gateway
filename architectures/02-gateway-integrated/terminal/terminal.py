import os
import time
import json

from gateway.gateway_client import GatewayClient
from devices.device_manager import DeviceManager
from scenario.scenario_engine import ScenarioEngine


class TerminalUI:
    def __init__(self):
        self.gateway = None
        self.devices = None
        self.lamps = None
        self.thermostat = None
        self.scenarios = None
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
                ensure_ascii=False,
                default=str
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
        self.scenarios = ScenarioEngine(self.devices)

        print("Connected successfully.")
        time.sleep(1)

    def header(self):
        self.clear()

        print("Smart Panel V2")
        print("==============================")
        print("Local Terminal Control Panel")
        print("==============================")
        print()

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

    def main_menu(self):
        while self.running:
            self.header()

            print("Main Menu")
            print("------------------------------")
            print("1) Show all device states")
            print("2) Lamp control")
            print("3) Thermostat control")
            print("4) Scenario control")
            print("5) Refresh devices")
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
                self.scenario_menu()

            elif choice == "5":
                self.refresh_devices()

            elif choice == "0":
                self.running = False

            else:
                print("Invalid command.")
                self.pause()

    def refresh_devices(self):
        self.header()

        print("Refreshing devices...")
        print()

        self.devices.refresh()
        self.lamps = self.devices.lamps()
        self.thermostat = self.devices.thermostat()
        self.scenarios = ScenarioEngine(self.devices)

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

    # =========================================================
    # Lamp Menu
    # =========================================================

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
                self.control_single_lamp(turn_on=True)

            elif choice == "3":
                self.control_single_lamp(turn_on=False)

            elif choice == "4":
                self.turn_all_lamps(turn_on=True)

            elif choice == "5":
                self.turn_all_lamps(turn_on=False)

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
            print()
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
            print()
            print("Error:")
            print(e)

        self.pause()

    # =========================================================
    # Thermostat Menu
    # =========================================================

    def thermostat_menu(self):
        while True:
            self.header()

            print("Thermostat Control")
            print("------------------------------")
            print("1) Show thermostat state")
            print("2) Set point")
            print()
            print("Mode")
            print("3) Cool")
            print("4) Heat")
            print("5) Auto")
            print("6) Hand")
            print()
            print("Fan Speed")
            print("7) Fan low")
            print("8) Fan medium")
            print("9) Fan high")
            print("10) Fan off")
            print()
            print("0) Back")
            print()

            choice = input("Select: ").strip()

            if choice == "1":
                self.show_thermostat_state()

            elif choice == "2":
                self.set_thermostat_setpoint()

            elif choice == "3":
                self.run_thermostat_action(
                    "Thermostat mode -> COOL",
                    self.thermostat.cool
                )

            elif choice == "4":
                self.run_thermostat_action(
                    "Thermostat mode -> HEAT",
                    self.thermostat.heat
                )

            elif choice == "5":
                self.run_thermostat_action(
                    "Thermostat mode -> AUTO",
                    self.thermostat.auto
                )

            elif choice == "6":
                self.run_thermostat_action(
                    "Thermostat mode -> HAND",
                    self.thermostat.hand
                )

            elif choice == "7":
                self.run_thermostat_action(
                    "Fan speed -> LOW",
                    self.thermostat.fan_low
                )

            elif choice == "8":
                self.run_thermostat_action(
                    "Fan speed -> MEDIUM",
                    self.thermostat.fan_medium
                )

            elif choice == "9":
                self.run_thermostat_action(
                    "Fan speed -> HIGH",
                    self.thermostat.fan_high
                )

            elif choice == "10":
                self.run_thermostat_action(
                    "Fan speed -> OFF",
                    self.thermostat.fan_off
                )

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
            print()
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print()
            print("Error:")
            print(e)

        self.pause()

    def run_thermostat_action(self, title, action):
        self.header()

        print(title)
        print("------------------------------")
        print()

        try:
            result = action()

            print("Command sent successfully.")
            print()
            print("RPC Result:")
            self.print_json(result)

        except Exception as e:
            print("Error:")
            print(e)

        self.pause()

    # =========================================================
    # Scenario Menu
    # =========================================================

    def scenario_menu(self):
        while True:
            self.header()

            print("Scenario Control")
            print("------------------------------")
            print("1) List scenarios")
            print("2) Show scenario")
            print("3) Run scenario")
            print("4) Create scenario")
            print("5) Edit scenario")
            print("6) Delete scenario")
            print("0) Back")
            print()

            choice = input("Select: ").strip()

            if choice == "1":
                self.list_scenarios()

            elif choice == "2":
                self.show_scenario()

            elif choice == "3":
                self.run_scenario()

            elif choice == "4":
                self.create_scenario()

            elif choice == "5":
                self.edit_scenario()

            elif choice == "6":
                self.delete_scenario()

            elif choice == "0":
                break

            else:
                print("Invalid command.")
                self.pause()

    def list_scenarios(self):
        self.header()

        print("Scenarios")
        print("------------------------------")
        print()

        response = self.scenarios.getScenarios()

        self.print_json(response)

        self.pause()

    def show_scenario(self):
        self.header()

        print("Show Scenario")
        print("------------------------------")
        print()

        name = input("Scenario name: ").strip()

        response = self.scenarios.getScenario(
            {
                "name": name
            }
        )

        self.print_json(response)

        self.pause()

    def run_scenario(self):
        self.header()

        print("Run Scenario")
        print("------------------------------")
        print()

        name = input("Scenario name: ").strip()

        response = self.scenarios.runScenario(
            {
                "name": name
            }
        )

        self.print_json(response)

        self.pause()

    def create_scenario(self):
        self.header()

        print("Create Scenario")
        print("------------------------------")
        print()

        name = input("Scenario name: ").strip()

        actions = self.build_actions_interactive()

        response = self.scenarios.createScenario(
            {
                "name": name,
                "actions": actions
            }
        )

        self.print_json(response)

        self.pause()

    def edit_scenario(self):
        self.header()

        print("Edit Scenario")
        print("------------------------------")
        print()

        old_name = input("Old scenario name: ").strip()

        existing = self.scenarios.getScenario(
            {
                "name": old_name
            }
        )

        if not existing.get("success"):
            self.print_json(existing)
            self.pause()
            return

        print()
        print("Current scenario:")
        self.print_json(existing.get("scenario"))

        print()
        new_name = input("New name empty = keep old: ").strip()

        if not new_name:
            new_name = old_name

        print()
        print("Now define new action list.")
        print("The old action list will be replaced.")
        print()

        actions = self.build_actions_interactive()

        response = self.scenarios.updateScenario(
            {
                "oldName": old_name,
                "name": new_name,
                "actions": actions
            }
        )

        self.print_json(response)

        self.pause()

    def delete_scenario(self):
        self.header()

        print("Delete Scenario")
        print("------------------------------")
        print()

        name = input("Scenario name: ").strip()
        confirm = input(f'Delete "{name}"? yes/no: ').strip().lower()

        if confirm != "yes":
            print("Cancelled.")
            self.pause()
            return

        response = self.scenarios.deleteScenario(
            {
                "name": name
            }
        )

        self.print_json(response)

        self.pause()

    def build_actions_interactive(self):
        actions = []

        while True:
            print()
            print("Add Action")
            print("------------------------------")
            print("1) Lamp")
            print("2) Thermostat")
            print("0) Finish")
            print()

            choice = input("Select device: ").strip()

            if choice == "1":
                action = self.build_lamp_action()
                actions.append(action)

            elif choice == "2":
                action = self.build_thermostat_action()
                actions.append(action)

            elif choice == "0":
                break

            else:
                print("Invalid command.")
                continue

            print()
            print("Current actions:")
            self.print_json(actions)

        return actions

    def build_lamp_action(self):
        print()
        print("Lamp Action")
        print("------------------------------")
        print("1) Turn ON")
        print("2) Turn OFF")
        print("3) Request state")
        print()

        choice = input("Select: ").strip()
        number = int(input("Lamp number 1-6: ").strip())

        if choice == "1":
            action_name = "turn_on"

        elif choice == "2":
            action_name = "turn_off"

        elif choice == "3":
            action_name = "request_state"

        else:
            raise ValueError("Invalid lamp action")

        return {
            "device": "lamp",
            "number": number,
            "action": action_name
        }

    def build_thermostat_action(self):
        print()
        print("Thermostat Action")
        print("------------------------------")
        print("1) Set temperature")
        print("2) Auto mode")
        print("3) Manual mode")
        print("4) Cooling")
        print("5) Heating")
        print("6) Fan speed")
        print("7) Request state")
        print()

        choice = input("Select: ").strip()

        if choice == "1":
            value = float(input("Temperature °C: ").strip())

            return {
                "device": "thermostat",
                "action": "set_sp",
                "value": value
            }

        if choice == "2":
            return {
                "device": "thermostat",
                "action": "set_auto"
            }

        if choice == "3":
            return {
                "device": "thermostat",
                "action": "set_hand"
            }

        if choice == "4":
            return {
                "device": "thermostat",
                "action": "set_cool"
            }

        if choice == "5":
            return {
                "device": "thermostat",
                "action": "set_heat"
            }

        if choice == "6":
            speed = int(input("Fan speed 0-3: ").strip())

            return {
                "device": "thermostat",
                "action": "set_fan_speed",
                "value": speed
            }

        if choice == "7":
            return {
                "device": "thermostat",
                "action": "request_state"
            }

        raise ValueError("Invalid thermostat action")
