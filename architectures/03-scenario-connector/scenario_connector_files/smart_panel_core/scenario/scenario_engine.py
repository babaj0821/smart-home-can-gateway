from copy import deepcopy


class ScenarioEngine:

    def __init__(
        self,
        storage,
        gateway,
        devices
    ):

        self.storage = storage
        self.gateway = gateway
        self.devices = devices


    # ========================================================
    # Scenario CRUD
    # ========================================================

    def create_scenario(
        self,
        name,
        actions,
        description=""
    ):

        name = self._normalize_name(
            name
        )


        scenario = self._build_scenario(
            name,
            actions,
            description
        )


        self.storage.create(
            name,
            scenario
        )


        return self.get_scenario(
            name
        )


    def get_scenario(
        self,
        name
    ):

        scenario = self.storage.get(
            name
        )


        if scenario is None:

            return None


        return self._scenario_for_client(
            scenario
        )


    def get_all_scenarios(
        self
    ):

        result = {}


        scenarios = self.storage.get_all()


        for name, scenario in scenarios.items():

            result[name] = (
                self._scenario_for_client(
                    scenario
                )
            )


        return result


    def list_scenarios(
        self
    ):

        return sorted(
            self.storage
            .get_all()
            .keys()
        )


    def update_scenario(
        self,
        old_name,
        new_name,
        actions,
        description=""
    ):

        old_name = self._normalize_name(
            old_name
        )

        new_name = self._normalize_name(
            new_name
        )


        scenario = self._build_scenario(
            new_name,
            actions,
            description
        )


        self.storage.update(
            old_name,
            new_name,
            scenario
        )


        return self.get_scenario(
            new_name
        )


    def delete_scenario(
        self,
        name
    ):

        name = self._normalize_name(
            name
        )


        self.storage.delete(
            name
        )


        return {
            "success": True,
            "deleted": name
        }


    # ========================================================
    # Run Scenario
    # ========================================================

    def run_scenario(
        self,
        name
    ):

        name = self._normalize_name(
            name
        )


        scenario = self.storage.get(
            name
        )


        if scenario is None:

            raise ValueError(
                f"Scenario not found: {name}"
            )


        commands = []


        actions = scenario.get(
            "actions"
        )


        # ====================================================
        # New scenario format
        # ====================================================

        if (
            isinstance(
                actions,
                list
            )
            and
            len(actions) > 0
        ):

            normalized_actions = (
                self._normalize_actions(
                    actions
                )
            )


            for action in normalized_actions:

                commands.append(
                    self._action_to_command(
                        action
                    )
                )


        # ====================================================
        # Compatibility with old scenarios
        #
        # Example:
        #
        # {
        #   "commands": [
        #       {
        #           "device": "Lamp Controller",
        #           "method": "setLedBit1",
        #           "params": {"on": 1}
        #       }
        #   ]
        # }
        # ====================================================

        else:

            legacy_commands = scenario.get(
                "commands",
                []
            )


            if not isinstance(
                legacy_commands,
                list
            ):

                raise ValueError(
                    "Invalid scenario commands"
                )


            commands = deepcopy(
                legacy_commands
            )


        if not commands:

            raise ValueError(
                f"Scenario has no actions: {name}"
            )


        results = []


        for command in commands:

            result = self._execute_command(
                command
            )

            results.append(
                result
            )


        successful = sum(
            1
            for result in results
            if result.get(
                "success"
            )
        )


        all_success = (
            successful
            ==
            len(results)
        )


        return {

            "success":
                all_success,

            "scenario":
                name,

            "executed":
                all_success,

            "queued":
                successful,

            "total":
                len(results),

            "results":
                results

        }


    # ========================================================
    # Scenario builder
    # ========================================================

    def _build_scenario(
        self,
        name,
        actions,
        description
    ):

        if not isinstance(
            actions,
            list
        ):

            raise ValueError(
                "Scenario actions must be a list"
            )


        if not actions:

            raise ValueError(
                "Scenario must contain at least one action"
            )


        # ====================================================
        # Backward compatibility
        #
        # اگر مستقیماً canonical command وارد شد،
        # همان را به عنوان commands ذخیره می‌کنیم.
        # ====================================================

        if all(
            isinstance(
                item,
                dict
            )
            and
            "method" in item
            for item in actions
        ):

            return {

                "name":
                    name,

                "description":
                    str(
                        description
                        or
                        ""
                    ),

                "commands":
                    deepcopy(
                        actions
                    )

            }


        normalized_actions = (
            self._normalize_actions(
                actions
            )
        )


        return {

            "name":
                name,

            "description":
                str(
                    description
                    or
                    ""
                ),

            "actions":
                normalized_actions

        }


    # ========================================================
    # Validation
    # ========================================================

    def _normalize_name(
        self,
        name
    ):

        name = str(
            name
            or
            ""
        ).strip()


        if not name:

            raise ValueError(
                "Scenario name is required"
            )


        return name


    def _normalize_actions(
        self,
        actions
    ):

        if not isinstance(
            actions,
            list
        ):

            raise ValueError(
                "Actions must be a list"
            )


        if not actions:

            raise ValueError(
                "At least one action is required"
            )


        return [

            self._normalize_action(
                action
            )

            for action in actions

        ]


    def _normalize_action(
        self,
        action
    ):

        if not isinstance(
            action,
            dict
        ):

            raise ValueError(
                "Invalid scenario action"
            )


        device = str(
            action.get(
                "device",
                ""
            )
        ).strip().lower()


        action_name = str(
            action.get(
                "action",
                ""
            )
        ).strip()


        # ====================================================
        # Lamp
        # ====================================================

        if device == "lamp":

            number = int(
                action.get(
                    "number",
                    0
                )
            )


            try:

                max_lamps = (
                    self.devices
                    .lamps()
                    .lamp_count
                )

            except Exception:

                max_lamps = 6


            if (
                number < 1
                or
                number > max_lamps
            ):

                raise ValueError(
                    f"Lamp number must be between 1 and {max_lamps}"
                )


            if action_name not in (
                "turn_on",
                "turn_off"
            ):

                raise ValueError(
                    f"Unsupported lamp action: {action_name}"
                )


            return {

                "device":
                    "lamp",

                "number":
                    number,

                "action":
                    action_name

            }


        # ====================================================
        # Thermostat
        # ====================================================

        if device == "thermostat":

            supported = (

                "set_sp",

                "set_auto",

                "set_hand",

                "set_cool",

                "set_heat",

                "set_fan_speed"

            )


            if action_name not in supported:

                raise ValueError(
                    f"Unsupported thermostat action: {action_name}"
                )


            normalized = {

                "device":
                    "thermostat",

                "action":
                    action_name

            }


            if action_name == "set_sp":

                normalized[
                    "value"
                ] = float(
                    action.get(
                        "value"
                    )
                )


            if (
                action_name
                ==
                "set_fan_speed"
            ):

                speed = int(
                    action.get(
                        "value"
                    )
                )


                if speed not in (
                    0,
                    1,
                    2,
                    3
                ):

                    raise ValueError(
                        "Fan speed must be 0 to 3"
                    )


                normalized[
                    "value"
                ] = speed


            return normalized


        raise ValueError(
            f"Unsupported device type: {device}"
        )


    # ========================================================
    # Action -> canonical CAN RPC
    # ========================================================

    def _action_to_command(
        self,
        action
    ):

        # ====================================================
        # Lamp
        # ====================================================

        if (
            action[
                "device"
            ]
            ==
            "lamp"
        ):

            controller = (
                self.devices.lamps()
            )


            lamp = controller.lamp(
                action[
                    "number"
                ]
            )


            value = (

                1

                if
                action[
                    "action"
                ]
                ==
                "turn_on"

                else

                0

            )


            return {

                "device":
                    controller.name,

                "method":
                    lamp.rpc_method,

                "params": {
                    "on": value
                }

            }


        # ====================================================
        # Thermostat
        # ====================================================

        if (
            action[
                "device"
            ]
            ==
            "thermostat"
        ):

            thermostat = (
                self.devices.thermostat()
            )


            action_name = action[
                "action"
            ]


            # ------------------------------------------------
            # Set Point
            # ------------------------------------------------

            if action_name == "set_sp":

                return {

                    "device":
                        thermostat.name,

                    "method":
                        thermostat
                        .rpc_methods[
                            "setpoint"
                        ],

                    "params": {

                        "value":
                            thermostat
                            .encode_setpoint(
                                action[
                                    "value"
                                ]
                            )

                    }

                }


            # ------------------------------------------------
            # Fan
            # ------------------------------------------------

            if (
                action_name
                ==
                "set_fan_speed"
            ):

                return {

                    "device":
                        thermostat.name,

                    "method":
                        thermostat
                        .rpc_methods[
                            "fan_speed"
                        ],

                    "params": {

                        "speed":
                            int(
                                action[
                                    "value"
                                ]
                            )

                    }

                }


            # ------------------------------------------------
            # Cooling
            # ------------------------------------------------

            if action_name == "set_cool":

                return {

                    "device":
                        thermostat.name,

                    "method":
                        thermostat
                        .rpc_methods[
                            "cool_heat"
                        ],

                    "params": {
                        "cool": 1
                    }

                }


            # ------------------------------------------------
            # Heating
            # ------------------------------------------------

            if action_name == "set_heat":

                return {

                    "device":
                        thermostat.name,

                    "method":
                        thermostat
                        .rpc_methods[
                            "cool_heat"
                        ],

                    "params": {
                        "cool": 2
                    }

                }


            # ------------------------------------------------
            # Auto
            # ------------------------------------------------

            if action_name == "set_auto":

                return {

                    "device":
                        thermostat.name,

                    "method":
                        thermostat
                        .rpc_methods[
                            "auto"
                        ],

                    "params": {
                        "auto": 0
                    }

                }


            # ------------------------------------------------
            # Manual / Hand
            # ------------------------------------------------

            if action_name == "set_hand":

                return {

                    "device":
                        thermostat.name,

                    "method":
                        thermostat
                        .rpc_methods[
                            "auto"
                        ],

                    "params": {
                        "auto": 2
                    }

                }


        raise ValueError(
            f"Cannot convert action to command: {action}"
        )


    # ========================================================
    # Legacy command -> Widget action
    # ========================================================

    def _command_to_action(
        self,
        command
    ):

        if not isinstance(
            command,
            dict
        ):

            return None


        method = str(
            command.get(
                "method",
                ""
            )
        )


        params = command.get(
            "params",
            {}
        )


        if not isinstance(
            params,
            dict
        ):

            params = {}


        # ====================================================
        # Lamp
        # ====================================================

        if method.startswith(
            "setLedBit"
        ):

            suffix = method[
                len(
                    "setLedBit"
                ):
            ]


            try:

                number = int(
                    suffix
                )

                on = int(
                    params.get(
                        "on"
                    )
                )

            except Exception:

                return None


            return {

                "device":
                    "lamp",

                "number":
                    number,

                "action":
                    (
                        "turn_on"
                        if on == 1
                        else
                        "turn_off"
                    )

            }


        # ====================================================
        # Thermostat SetPoint
        # ====================================================

        if method == "setPoint":

            if "value" not in params:

                return None


            return {

                "device":
                    "thermostat",

                "action":
                    "set_sp",

                "value":
                    float(
                        params[
                            "value"
                        ]
                    )
                    /
                    2.0

            }


        # ====================================================
        # Thermostat Fan
        # ====================================================

        if method == "setFanSpeed":

            return {

                "device":
                    "thermostat",

                "action":
                    "set_fan_speed",

                "value":
                    int(
                        params.get(
                            "speed",
                            0
                        )
                    )

            }


        # ====================================================
        # Thermostat Cool / Heat
        # ====================================================

        if method == "setCoolHeat":

            value = int(
                params.get(
                    "cool",
                    -1
                )
            )


            if value == 1:

                action_name = (
                    "set_cool"
                )

            elif value == 2:

                action_name = (
                    "set_heat"
                )

            else:

                return None


            return {

                "device":
                    "thermostat",

                "action":
                    action_name

            }


        # ====================================================
        # Thermostat Auto / Hand
        # ====================================================

        if method == "setAuto":

            value = int(
                params.get(
                    "auto",
                    -1
                )
            )


            if value == 0:

                action_name = (
                    "set_auto"
                )

            elif value == 2:

                action_name = (
                    "set_hand"
                )

            else:

                return None


            return {

                "device":
                    "thermostat",

                "action":
                    action_name

            }


        return None


    # ========================================================
    # Scenario -> Widget format
    # ========================================================

    def _scenario_for_client(
        self,
        scenario
    ):

        result = deepcopy(
            scenario
        )


        actions = result.get(
            "actions"
        )


        # New scenario format
        if isinstance(
            actions,
            list
        ):

            result[
                "editable"
            ] = True

            return result


        # Legacy scenario format
        commands = result.get(
            "commands",
            []
        )


        converted_actions = []

        editable = True


        for command in commands:

            action = self._command_to_action(
                command
            )


            if action is None:

                editable = False

                continue


            converted_actions.append(
                action
            )


        result[
            "actions"
        ] = converted_actions


        result[
            "editable"
        ] = editable


        return result


    # ========================================================
    # Send command to LocalGateway
    # ========================================================

    def _execute_command(
        self,
        command
    ):

        device = command.get(
            "device"
        )


        method = command.get(
            "method"
        )


        params = command.get(
            "params",
            {}
        )


        if not device:

            return {
                "success": False,
                "error": "Device missing"
            }


        if not method:

            return {
                "success": False,
                "device": device,
                "error": "Method missing"
            }


        try:

            result = self.gateway.send_rpc(
                device,
                method,
                params
            )


            return {

                "device":
                    device,

                "method":
                    method,

                "params":
                    params,

                "success":
                    True,

                "result":
                    result

            }


        except Exception as e:

            return {

                "device":
                    device,

                "method":
                    method,

                "params":
                    params,

                "success":
                    False,

                "error":
                    str(e)

            }
