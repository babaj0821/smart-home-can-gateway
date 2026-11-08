import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent / "data.json"


def empty_data():
    return {
        "scenarios": {}
    }


def save_data(data):
    temp_path = DATA_PATH.with_suffix(".tmp")

    with open(
        temp_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    temp_path.replace(DATA_PATH)


def load_data():
    if not DATA_PATH.exists():
        data = empty_data()
        save_data(data)
        return data

    if DATA_PATH.stat().st_size == 0:
        data = empty_data()
        save_data(data)
        return data

    try:
        with open(
            DATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON file: {error}"
        )

    if not isinstance(data, dict):
        raise ValueError(
            "Root JSON must be an object"
        )

    if "scenarios" not in data:
        data["scenarios"] = {}

    if not isinstance(
        data["scenarios"],
        dict
    ):
        raise ValueError(
            "scenarios must be an object"
        )

    return data


def get_scenario_names():
    data = load_data()

    return list(
        data["scenarios"].keys()
    )


def get_scenario(name):
    data = load_data()

    scenario = data[
        "scenarios"
    ].get(name)

    if scenario is None:
        return None

    return {
        "name": name,
        "actions": scenario.get(
            "actions",
            []
        )
    }


def create_scenario(
    name,
    actions=None
):
    name = name.strip()

    if not name:
        raise ValueError(
            "Scenario name cannot be empty"
        )

    data = load_data()

    if name in data["scenarios"]:
        return False

    if actions is None:
        actions = []

    data["scenarios"][name] = {
        "actions": actions
    }

    save_data(data)

    return True


def delete_scenario(name):
    data = load_data()

    if name not in data["scenarios"]:
        return False

    del data[
        "scenarios"
    ][name]

    save_data(data)

    return True


def rename_scenario(
    old_name,
    new_name
):
    new_name = new_name.strip()

    if not new_name:
        return False

    data = load_data()

    if old_name not in data["scenarios"]:
        return False

    if new_name in data["scenarios"]:
        return False

    data["scenarios"][new_name] = (
        data["scenarios"].pop(
            old_name
        )
    )

    save_data(data)

    return True


def add_action(
    scenario_name,
    action
):
    data = load_data()

    scenario = data[
        "scenarios"
    ].get(
        scenario_name
    )

    if scenario is None:
        return False

    scenario.setdefault(
        "actions",
        []
    )

    scenario[
        "actions"
    ].append(
        action
    )

    save_data(data)

    return True


def remove_action(
    scenario_name,
    action_index
):
    data = load_data()

    scenario = data[
        "scenarios"
    ].get(
        scenario_name
    )

    if scenario is None:
        return False

    actions = scenario.get(
        "actions",
        []
    )

    if not 0 <= action_index < len(actions):
        return False

    actions.pop(
        action_index
    )

    save_data(data)

    return True


def replace_actions(
    scenario_name,
    actions
):
    data = load_data()

    scenario = data[
        "scenarios"
    ].get(
        scenario_name
    )

    if scenario is None:
        return False

    scenario[
        "actions"
    ] = actions

    save_data(data)

    return True
def update_scenario(old_name, new_name, actions):

    old_name = old_name.strip()
    new_name = new_name.strip()

    if not old_name:
        raise ValueError(
            "Old scenario name cannot be empty"
        )

    if not new_name:
        raise ValueError(
            "New scenario name cannot be empty"
        )

    if not isinstance(actions, list):
        raise ValueError(
            "Actions must be a list"
        )

    data = load_data()

    scenarios = data["scenarios"]

    if old_name not in scenarios:
        return "not_found"

    if (
        new_name != old_name
        and new_name in scenarios
    ):
        return "already_exists"

    new_scenarios = {}

    for name, scenario in scenarios.items():

        if name == old_name:

            new_scenarios[new_name] = {
                "actions": actions
            }

        else:

            new_scenarios[name] = scenario

    data["scenarios"] = new_scenarios

    save_data(data)

    return "updated"
