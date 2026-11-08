import time

from scenario.scenario_storage import ScenarioStorage


class ScenarioEngine:
    def __init__(self, devices, storage_path="scenario/data.json"):
        self.devices = devices
        self.storage = ScenarioStorage(storage_path)

    # =========================================================
    # Widget-compatible methods
    # =========================================================

    def getScenarios(self, params=None):
        return {
            "success": True,
            "scenarios": self.storage.list_names()
        }

    def getScenario(self, params):
        name = self._required_param(params, "name")

        scenario = self.storage.get(name)

        if scenario is None:
            return {
                "success": False,
                "error": f"Scenario not found: {name}"
            }

        return {
            "success": True,
            "scenario": scenario
        }

    def createScenario(self, params):
        try:
            name = self._validate_name(
                params.get("name")
            )

            actions = self._validate_actions(
                params.get("actions")
            )

            scenario = self.storage.create(
                name,
                actions
            )

            return {
                "success": True,
                "scenario": scenario
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def updateScenario(self, params):
        try:
            old_name = self._validate_name(
                params.get("oldName")
            )

            new_name = self._validate_name(
                params.get("name")
            )

            actions = self._validate_actions(
                params.get("actions")
            )

            scenario = self.storage.update(
                old_name,
                new_name,
                actions
            )

            return {
                "success": True,
                "scenario": scenario
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def deleteScenario(self, params):
        try:
            name = self._validate_name(
                params.get("name")
            )

            self.storage.delete(name)

            return {
                "success": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def runScenario(self, params):
        try:
            name = self._validate_name(
                params.get("name")
            )

            return self.run_by_name(name)

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # =========================================================
    # Local methods
    # =========================================================

    def list_names(self):
        return self.storage.list_names()

    def get(self, name):
        return self.storage.get(name)

    def create(self, name, actions):
        return self.createScenario(
            {
                "name": name,
                "actions": actions
            }
        )

    def update(self, old_name, new_name, actions):
        return self.updateScenario(
            {
                "oldName": old_name,
                "name": new_name,
                "actions": actions
            }
        )

    def delete(self, name):
        return self.deleteScenario(
            {
                "name": name
            }
        )

    def run_by_name(self, name):
        scenario = self.storage.get(name)

        if scenario is None:
            return {
                "success": False,
                "error": f"Scenario not found: {name}"
            }

        results = []

        for index, action in enumerate(
            scenario.get("actions", []),
            start=1
        ):
            result = self.run_action(action)

            results.append(
                {
                    "index": index,
                    "action": action,
                    "result": result
                }
            )

            delay = action.get("delay")

            if delay is not None:
                time.sleep(float(delay))

        return {
            "success": True,
            "name": name,
            "results": results
        }

    def run_action(self, action):
        device = action.get("device")
        action_name = action.get("action")

        if device == "lamp":
            return self._run_lamp_action(action_name, action)

        if device == "thermostat":
            return self._run_thermostat_action(action_name, action)

        raise ValueError(f"Unknown device: {device}")

    # =========================================================
    # Device actions
    # =========================================================

    def _run_lamp_action(self, action_name, action):
        lamps = self.devices.lamps()

        number = int(action.get("number", 1))

        if action_name == "turn_on":
            return lamps.turn_on(number)

        if action_name == "turn_off":
            return lamps.turn_off(number)

        if action_name == "request_state":
            return lamps.lamp(number).get_state()

        raise ValueError(f"Unknown lamp action: {action_name}")

    def _run_thermostat_action(self, action_name, action):
        thermostat = self.devices.thermostat()

        if action_name == "set_sp":
            return thermostat.set_setpoint(
                action.get("value")
            )

        if action_name == "set_auto":
            return thermostat.auto()

        if action_name == "set_hand":
            return thermostat.hand()

        if action_name == "set_cool":
            return thermostat.cool()

        if action_name == "set_heat":
            return thermostat.heat()

        if action_name == "set_fan_speed":
            speed = int(action.get("value"))

            if speed == 0:
                return thermostat.fan_off()

            if speed == 1:
                return thermostat.fan_low()

            if speed == 2:
                return thermostat.fan_medium()

            if speed == 3:
                return thermostat.fan_high()

            raise ValueError("Fan speed must be 0 to 3")

        if action_name == "request_state":
            return thermostat.get_state()

        raise ValueError(f"Unknown thermostat action: {action_name}")

    # =========================================================
    # Validation
    # =========================================================

    def _required_param(self, params, key):
        if not isinstance(params, dict):
            raise ValueError("Params must be object")

        value = params.get(key)

        if value is None:
            raise ValueError(f"Missing param: {key}")

        return value

    def _validate_name(self, value):
        name = str(value or "").strip()

        if not name:
            raise ValueError("Scenario name is required")

        return name

    def _validate_actions(self, actions):
        if not isinstance(actions, list):
            raise ValueError("Actions must be list")

        if len(actions) == 0:
            raise ValueError("Add at least one action")

        cleaned = []

        for action in actions:
            cleaned.append(
                self._validate_action(action)
            )

        return cleaned

    def _validate_action(self, action):
        if not isinstance(action, dict):
            raise ValueError("Action must be object")

        device = action.get("device")
        action_name = action.get("action")

        if device not in ["lamp", "thermostat"]:
            raise ValueError(f"Invalid device: {device}")

        if not action_name:
            raise ValueError("Action name is required")

        cleaned = {
            "device": device,
            "action": action_name
        }

        if device == "lamp":
            number = int(action.get("number", 1))

            if number < 1:
                raise ValueError("Invalid lamp number")

            cleaned["number"] = number

            if action_name not in [
                "turn_on",
                "turn_off",
                "request_state"
            ]:
                raise ValueError(f"Invalid lamp action: {action_name}")

        if device == "thermostat":
            if action_name not in [
                "set_sp",
                "set_auto",
                "set_hand",
                "set_cool",
                "set_heat",
                "set_fan_speed",
                "request_state"
            ]:
                raise ValueError(
                    f"Invalid thermostat action: {action_name}"
                )

            if action_name == "set_sp":
                cleaned["value"] = float(action.get("value"))

            if action_name == "set_fan_speed":
                speed = int(action.get("value"))

                if speed not in [0, 1, 2, 3]:
                    raise ValueError("Fan speed must be 0 to 3")

                cleaned["value"] = speed

        if "delay" in action and action.get("delay") is not None:
            cleaned["delay"] = float(action.get("delay"))

        return cleaned
