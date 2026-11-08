import json
import os
import tempfile


class ScenarioStorage:
    def __init__(self, path="scenario/data.json"):
        self.path = path
        self.ensure_file()

    def ensure_file(self):
        directory = os.path.dirname(self.path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.path):
            self.save_data(
                {
                    "scenarios": {}
                }
            )

    def load_data(self):
        self.ensure_file()

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)

        except Exception:
            data = {
                "scenarios": {}
            }

        if not isinstance(data, dict):
            data = {
                "scenarios": {}
            }

        if "scenarios" not in data or not isinstance(data["scenarios"], dict):
            data["scenarios"] = {}

        return data

    def save_data(self, data):
        directory = os.path.dirname(self.path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(
            dir=directory or ".",
            prefix=".scenario_",
            suffix=".json"
        )

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(temp_path, self.path)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def list_names(self):
        data = self.load_data()

        return sorted(
            list(data["scenarios"].keys())
        )

    def get(self, name):
        data = self.load_data()

        scenario = data["scenarios"].get(name)

        if scenario is None:
            return None

        return scenario

    def create(self, name, actions):
        data = self.load_data()

        if name in data["scenarios"]:
            raise ValueError(f"Scenario already exists: {name}")

        data["scenarios"][name] = {
            "name": name,
            "actions": actions
        }

        self.save_data(data)

        return data["scenarios"][name]

    def update(self, old_name, new_name, actions):
        data = self.load_data()

        if old_name not in data["scenarios"]:
            raise ValueError(f"Scenario not found: {old_name}")

        if new_name != old_name and new_name in data["scenarios"]:
            raise ValueError(f"Scenario already exists: {new_name}")

        if new_name != old_name:
            del data["scenarios"][old_name]

        data["scenarios"][new_name] = {
            "name": new_name,
            "actions": actions
        }

        self.save_data(data)

        return data["scenarios"][new_name]

    def delete(self, name):
        data = self.load_data()

        if name not in data["scenarios"]:
            raise ValueError(f"Scenario not found: {name}")

        del data["scenarios"][name]

        self.save_data(data)

        return True
