import time

from storage.json_storage import (
    get_scenario_names,
    get_scenario,
    create_scenario,
    delete_scenario,
    add_action,
    remove_action
)


def clear_screen():
    print(
        "\033[2J\033[H",
        end=""
    )


def show_message(
    message,
    delay=2
):
    print(
        f"\n{message}"
    )

    time.sleep(
        delay
    )


def select_scenario():
    names = get_scenario_names()

    if not names:
        show_message(
            "No scenarios found"
        )
        return None

    clear_screen()

    print(
        "========== SCENARIOS =========="
    )

    for index, name in enumerate(
        names,
        start=1
    ):
        print(
            f"{index} = {name}"
        )

    print(
        "b = Back"
    )

    command = input(
        "\n> "
    ).strip().lower()

    if command == "b":
        return None

    try:
        index = int(command) - 1

    except ValueError:
        show_message(
            "Invalid selection"
        )
        return None

    if not 0 <= index < len(names):
        show_message(
            "Invalid selection"
        )
        return None

    return names[index]


def build_action():
    clear_screen()

    print(
        "========== ADD ACTION ==========\n"
        "1 = Lamp\n"
        "2 = Thermostat\n"
        "b = Back\n"
        "================================"
    )

    device = input(
        "\n> "
    ).strip().lower()

    if device == "b":
        return None

    if device == "1":
        return build_lamp_action()

    if device == "2":
        return build_thermostat_action()

    show_message(
        "Unknown device"
    )

    return None


def build_lamp_action():
    clear_screen()

    try:
        number = int(
            input(
                "Lamp number: "
            )
        )

    except ValueError:
        show_message(
            "Invalid lamp number"
        )
        return None

    print(
        "\n"
        "1 = Turn ON\n"
        "2 = Turn OFF\n"
        "3 = Request State\n"
    )

    command = input(
        "> "
    ).strip()

    actions = {
        "1": "turn_on",
        "2": "turn_off",
        "3": "request_state"
    }

    action_name = actions.get(
        command
    )

    if action_name is None:
        show_message(
            "Invalid action"
        )
        return None

    return {
        "device": "lamp",
        "number": number,
        "action": action_name
    }


def build_thermostat_action():
    clear_screen()

    print(
        "======= THERMOSTAT ACTION =======\n"
        "1 = Set SP\n"
        "2 = Auto\n"
        "3 = Hand\n"
        "4 = Cool\n"
        "5 = Heat\n"
        "6 = Fan Speed\n"
        "7 = Request State\n"
        "================================="
    )

    command = input(
        "\n> "
    ).strip()

    if command == "1":
        try:
            value = float(
                input(
                    "Setpoint: "
                )
            )

        except ValueError:
            show_message(
                "Invalid setpoint"
            )
            return None

        return {
            "device": "thermostat",
            "action": "set_sp",
            "value": value
        }

    if command == "2":
        return {
            "device": "thermostat",
            "action": "set_auto"
        }

    if command == "3":
        return {
            "device": "thermostat",
            "action": "set_hand"
        }

    if command == "4":
        return {
            "device": "thermostat",
            "action": "set_cool"
        }

    if command == "5":
        return {
            "device": "thermostat",
            "action": "set_heat"
        }

    if command == "6":
        try:
            value = int(
                input(
                    "Fan speed [0-3]: "
                )
            )

        except ValueError:
            show_message(
                "Invalid fan speed"
            )
            return None

        if value not in (
            0,
            1,
            2,
            3
        ):
            show_message(
                "Fan speed must be 0-3"
            )
            return None

        return {
            "device": "thermostat",
            "action": "set_fan_speed",
            "value": value
        }

    if command == "7":
        return {
            "device": "thermostat",
            "action": "request_state"
        }

    show_message(
        "Invalid action"
    )

    return None


def create_scenario_menu():
    clear_screen()

    name = input(
        "Scenario name: "
    ).strip()

    if not name:
        show_message(
            "Invalid scenario name"
        )
        return

    created = create_scenario(
        name
    )

    if not created:
        show_message(
            "Scenario already exists"
        )
        return

    while True:
        clear_screen()

        scenario = get_scenario(
            name
        )

        print(
            f"Scenario: {name}\n"
        )

        actions = scenario[
            "actions"
        ]

        if not actions:
            print(
                "No actions"
            )

        else:
            for index, action in enumerate(
                actions,
                start=1
            ):
                print(
                    index,
                    action
                )

        print(
            "\n"
            "a = Add Action\n"
            "d = Done\n"
        )

        command = input(
            "> "
        ).strip().lower()

        if command == "d":
            break

        if command == "a":
            action = build_action()

            if action is not None:
                add_action(
                    name,
                    action
                )


def edit_scenario_menu():
    name = select_scenario()

    if name is None:
        return

    while True:
        clear_screen()

        scenario = get_scenario(
            name
        )

        print(
            f"========== {name} ==========\n"
        )

        actions = scenario[
            "actions"
        ]

        if not actions:
            print(
                "No actions"
            )

        else:
            for index, action in enumerate(
                actions,
                start=1
            ):
                print(
                    f"{index}: {action}"
                )

        print(
            "\n"
            "a = Add Action\n"
            "r = Remove Action\n"
            "b = Back\n"
        )

        command = input(
            "> "
        ).strip().lower()

        if command == "b":
            break

        elif command == "a":
            action = build_action()

            if action is not None:
                add_action(
                    name,
                    action
                )

        elif command == "r":
            try:
                index = int(
                    input(
                        "Action number: "
                    )
                ) - 1

            except ValueError:
                show_message(
                    "Invalid action number"
                )
                continue

            if remove_action(
                name,
                index
            ):
                show_message(
                    "Action removed",
                    1
                )

            else:
                show_message(
                    "Action not found"
                )


def delete_scenario_menu():
    name = select_scenario()

    if name is None:
        return

    answer = input(
        f"Delete '{name}'? [y/n]: "
    ).strip().lower()

    if answer != "y":
        return

    if delete_scenario(
        name
    ):
        show_message(
            "Scenario deleted"
        )


def run_scenario_menu(
    scenario_engine
):
    name = select_scenario()

    if name is None:
        return

    scenario = get_scenario(
        name
    )

    try:
        scenario_engine.run(
            scenario
        )

        show_message(
            f"Scenario '{name}' executed"
        )

    except Exception as error:
        show_message(
            f"Scenario error: {error}",
            3
        )


def scenario_menu(
    scenario_engine
):
    while True:
        clear_screen()

        names = get_scenario_names()

        print(
            "========== SCENARIO MENU ==========\n"
        )

        if names:
            print(
                "Available scenarios:"
            )

            for name in names:
                print(
                    f"  - {name}"
                )

        else:
            print(
                "No scenarios defined"
            )

        print(
            "\n"
            "1 = Run Scenario\n"
            "2 = Create Scenario\n"
            "3 = Edit Scenario\n"
            "4 = Delete Scenario\n"
            "b = Back\n"
            "==================================="
        )

        command = input(
            "\n> "
        ).strip().lower()

        if command == "b":
            break

        elif command == "1":
            run_scenario_menu(
                scenario_engine
            )

        elif command == "2":
            create_scenario_menu()

        elif command == "3":
            edit_scenario_menu()

        elif command == "4":
            delete_scenario_menu()

        else:
            show_message(
                "Unknown command"
            )
