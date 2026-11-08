import json

from smart_panel_core.grpc_client import (
    LocalProcessorGrpcClient
)


class SmartPanelTerminal:

    def __init__(
        self
    ):

        self.client = (
            LocalProcessorGrpcClient(
                target="127.0.0.1:50051",
                timeout=5.0
            )
        )


    # ========================================================
    # Start terminal
    # ========================================================

    def start(
        self
    ):

        print(
            "=== SMART PANEL TERMINAL ==="
        )


        self.print_help()


        try:

            while True:

                try:

                    command = input(
                        "\n> "
                    )


                    self.handle(
                        command
                    )


                except KeyboardInterrupt:

                    print(
                        "\nEXIT"
                    )

                    break


                except Exception as e:

                    print(
                        {
                            "success": False,
                            "error": str(e)
                        }
                    )


        finally:

            self.client.close()


    # ========================================================
    # Help
    # ========================================================

    def print_help(
        self
    ):

        print(
            """
Commands:

  help

  devices

  state <device name>

  states


  scenarios

  show <scenario name>

  run <scenario name>

  delete <scenario name>


  create {"name":"night","actions":[{"device":"lamp","number":1,"action":"turn_off"}]}


  update {"oldName":"night","name":"night","actions":[{"device":"lamp","number":1,"action":"turn_on"}]}


  rpc {"device":"Lamp Controller","method":"setLedBit1","params":{"on":1}}


  exit
            """.strip()
        )


    # ========================================================
    # Command handler
    # ========================================================

    def handle(
        self,
        command
    ):

        command = str(
            command
            or
            ""
        ).strip()


        if not command:

            return


        parts = command.split(
            " ",
            1
        )


        action = parts[
            0
        ].lower()


        argument = (
            parts[
                1
            ].strip()

            if len(parts) > 1

            else
            ""
        )


        # ====================================================
        # Help
        # ====================================================

        if action == "help":

            self.print_help()

            return


        # ====================================================
        # Devices
        # ====================================================

        if action == "devices":

            result = (
                self.client.get_devices()
            )


            print(
                result
            )

            return


        # ====================================================
        # One device state
        # ====================================================

        if action == "state":

            if not argument:

                print(
                    "Usage: state <device name>"
                )

                return


            result = (
                self.client.get_state(
                    argument
                )
            )


            print(
                result
            )

            return


        # ====================================================
        # All states
        # ====================================================

        if action == "states":

            result = (
                self.client.get_all_states()
            )


            print(
                result
            )

            return


        # ====================================================
        # Scenario list
        # ====================================================

        if action == "scenarios":

            result = (
                self.client.get_scenarios()
            )


            print(
                result
            )

            return


        # ====================================================
        # Get one scenario
        # ====================================================

        if action == "show":

            if not argument:

                print(
                    "Usage: show <scenario name>"
                )

                return


            result = (
                self.client.get_scenario(
                    argument
                )
            )


            print(
                result
            )

            return


        # ====================================================
        # Run scenario
        # ====================================================

        if action == "run":

            if not argument:

                print(
                    "Usage: run <scenario name>"
                )

                return


            result = (
                self.client.run_scenario(
                    argument
                )
            )


            print(
                result
            )

            return


        # ====================================================
        # Delete scenario
        # ====================================================

        if action == "delete":

            if not argument:

                print(
                    "Usage: delete <scenario name>"
                )

                return


            result = (
                self.client.delete_scenario(
                    argument
                )
            )


            print(
                result
            )

            return


        # ====================================================
        # Create scenario
        #
        # Example:
        #
        # create {
        #   "name":"night",
        #   "actions":[
        #       {
        #           "device":"lamp",
        #           "number":1,
        #           "action":"turn_off"
        #       }
        #   ]
        # }
        # ====================================================

        if action == "create":

            if not argument:

                print(
                    "Usage: create <JSON>"
                )

                return


            payload = json.loads(
                argument
            )


            result = (
                self.client.create_scenario(
                    payload.get(
                        "name"
                    ),
                    payload.get(
                        "actions"
                    ),
                    payload.get(
                        "description",
                        ""
                    )
                )
            )


            print(
                result
            )

            return


        # ====================================================
        # Update / Rename scenario
        # ====================================================

        if action == "update":

            if not argument:

                print(
                    "Usage: update <JSON>"
                )

                return


            payload = json.loads(
                argument
            )


            result = (
                self.client.update_scenario(
                    payload.get(
                        "oldName"
                    ),
                    payload.get(
                        "name"
                    ),
                    payload.get(
                        "actions"
                    ),
                    payload.get(
                        "description",
                        ""
                    )
                )
            )


            print(
                result
            )

            return


        # ====================================================
        # Direct device RPC
        #
        # This does NOT encode CAN here.
        #
        # It goes:
        #
        # Terminal
        #   -> gRPC
        #   -> LocalProcessor
        #   -> CommandOutbox
        #   -> ScenarioConnector
        #   -> CAN_RPC
        #   -> CustomCanConnector
        #   -> official CAN downlink converter
        # ====================================================

        if action == "rpc":

            if not argument:

                print(
                    "Usage: rpc <JSON>"
                )

                return


            payload = json.loads(
                argument
            )


            result = (
                self.client.send_device_command(
                    payload.get(
                        "device"
                    ),
                    payload.get(
                        "method"
                    ),
                    payload.get(
                        "params",
                        {}
                    )
                )
            )


            print(
                result
            )

            return


        # ====================================================
        # Exit
        # ====================================================

        if action in (
            "exit",
            "quit"
        ):

            raise KeyboardInterrupt


        print(
            "Unknown command. Type: help"
        )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    SmartPanelTerminal().start()
