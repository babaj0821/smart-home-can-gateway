import json
import threading

import paho.mqtt.client as mqtt

from integrations.thingsboard.tb_config import (
    TB_HOST,
    TB_PORT,
    TB_TOKEN
)

from storage.json_storage import (
    get_scenario_names,
    get_scenario,
    create_scenario,
    delete_scenario,
    update_scenario
)


class ScenarioBridge:

    def __init__(self, scenario_engine):
        self.scenario_engine = scenario_engine

        self.client = mqtt.Client()

        self.client.username_pw_set(
            TB_TOKEN
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    # -------------------------------------------------
    # ThingsBoard connection
    # -------------------------------------------------

    def connect(self):
        self.client.connect(
            TB_HOST,
            TB_PORT,
            60
        )

        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    # -------------------------------------------------
    # MQTT connected
    # -------------------------------------------------

    def on_connect(
        self,
        client,
        userdata,
        flags,
        rc
    ):

        client.subscribe(
            "v1/devices/me/rpc/request/+"
        )

        self.publish_scenario_catalog()

    # -------------------------------------------------
    # Publish scenario catalog as client attribute
    # -------------------------------------------------

    def publish_scenario_catalog(self):
        try:
            names = get_scenario_names()

            payload = {
                "scenario_catalog": names,
                "scenario_count": len(names)
            }

            self.client.publish(
                "v1/devices/me/attributes",
                json.dumps(payload)
            )

        except Exception as error:
            print(
                "Scenario catalog publish error:",
                error
            )

    # -------------------------------------------------
    # RPC response
    # -------------------------------------------------

    def send_rpc_response(
        self,
        request_id,
        response
    ):
        topic = (
            "v1/devices/me/rpc/response/"
            + request_id
        )

        self.client.publish(
            topic,
            json.dumps(response)
        )

    # -------------------------------------------------
    # Run scenario in background
    # -------------------------------------------------

    def run_scenario(
        self,
        scenario_name
    ):
        try:
            scenario = get_scenario(
                scenario_name
            )

            if scenario is None:
                print(
                    "Scenario not found:",
                    scenario_name
                )
                return

            print(
                "Running scenario:",
                scenario_name
            )

            self.scenario_engine.run(
                scenario
            )

            print(
                "Scenario completed:",
                scenario_name
            )

        except Exception as error:
            print(
                "Scenario error:",
                error
            )

    # -------------------------------------------------
    # RPC handler
    # -------------------------------------------------

    def on_message(
        self,
        client,
        userdata,
        message
    ):
        try:
            payload = json.loads(
                message.payload.decode(
                    "utf-8"
                )
            )

            request_id = (
                message.topic.split("/")[-1]
            )

            method = payload.get(
                "method"
            )

            params = payload.get(
                "params",
                {}
            )

            if not isinstance(params, dict):
                params = {}

            print(
                "RPC:",
                method,
                params
            )

            # =========================================
            # GET SCENARIO LIST
            # =========================================

            if method == "getScenarios":

                names = get_scenario_names()

                self.send_rpc_response(
                    request_id,
                    {
                        "success": True,
                        "scenarios": names
                    }
                )

            # =========================================
            # GET ONE SCENARIO
            # =========================================

            elif method == "getScenario":

                name = params.get(
                    "name"
                )

                if not name:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario name missing"
                            )
                        }
                    )
                    return

                scenario = get_scenario(
                    name
                )

                if scenario is None:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario not found"
                            )
                        }
                    )
                    return

                self.send_rpc_response(
                    request_id,
                    {
                        "success": True,
                        "scenario": scenario
                    }
                )

            # =========================================
            # CREATE SCENARIO
            # =========================================

            elif method == "createScenario":

                name = params.get(
                    "name"
                )

                actions = params.get(
                    "actions",
                    []
                )

                if not name:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario name missing"
                            )
                        }
                    )
                    return

                if not isinstance(
                    actions,
                    list
                ):
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Actions must be a list"
                            )
                        }
                    )
                    return

                created = create_scenario(
                    name,
                    actions
                )

                if not created:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario already exists"
                            )
                        }
                    )
                    return

                self.send_rpc_response(
                    request_id,
                    {
                        "success": True,
                        "scenario": name
                    }
                )

                self.publish_scenario_catalog()

                print(
                    "Scenario created:",
                    name
                )

            # =========================================
            # UPDATE / RENAME SCENARIO
            # =========================================

            elif method == "updateScenario":

                old_name = params.get(
                    "oldName"
                )

                new_name = params.get(
                    "name"
                )

                actions = params.get(
                    "actions",
                    []
                )

                if not old_name:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Original scenario "
                                "name missing"
                            )
                        }
                    )
                    return

                if not new_name:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario name missing"
                            )
                        }
                    )
                    return

                if not isinstance(
                    actions,
                    list
                ):
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Actions must be a list"
                            )
                        }
                    )
                    return

                result = update_scenario(
                    old_name,
                    new_name,
                    actions
                )

                if result == "not_found":
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario not found"
                            )
                        }
                    )
                    return

                if result == "already_exists":
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario name "
                                "already exists"
                            )
                        }
                    )
                    return

                if result != "updated":
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario update failed"
                            )
                        }
                    )
                    return

                self.send_rpc_response(
                    request_id,
                    {
                        "success": True,
                        "scenario": new_name
                    }
                )

                self.publish_scenario_catalog()

                print(
                    "Scenario updated:",
                    old_name,
                    "->",
                    new_name
                )

            # =========================================
            # DELETE SCENARIO
            # =========================================

            elif method == "deleteScenario":

                name = params.get(
                    "name"
                )

                if not name:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario name missing"
                            )
                        }
                    )
                    return

                deleted = delete_scenario(
                    name
                )

                if not deleted:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario not found"
                            )
                        }
                    )
                    return

                self.send_rpc_response(
                    request_id,
                    {
                        "success": True,
                        "scenario": name
                    }
                )

                self.publish_scenario_catalog()

                print(
                    "Scenario deleted:",
                    name
                )

            # =========================================
            # RUN SCENARIO
            # =========================================

            elif method == "runScenario":

                scenario_name = params.get(
                    "name"
                )

                if not scenario_name:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario name missing"
                            )
                        }
                    )
                    return

                scenario = get_scenario(
                    scenario_name
                )

                if scenario is None:
                    self.send_rpc_response(
                        request_id,
                        {
                            "success": False,
                            "error": (
                                "Scenario not found"
                            )
                        }
                    )
                    return

                self.send_rpc_response(
                    request_id,
                    {
                        "success": True,
                        "scenario": scenario_name
                    }
                )

                threading.Thread(
                    target=self.run_scenario,
                    args=(
                        scenario_name,
                    ),
                    daemon=True
                ).start()

            # =========================================
            # REFRESH CATALOG ATTRIBUTE
            # =========================================

            elif method == "refreshScenarios":

                self.publish_scenario_catalog()

                self.send_rpc_response(
                    request_id,
                    {
                        "success": True
                    }
                )

            # =========================================
            # UNKNOWN RPC
            # =========================================

            else:

                self.send_rpc_response(
                    request_id,
                    {
                        "success": False,
                        "error": (
                            "Unknown RPC method"
                        )
                    }
                )

        except json.JSONDecodeError as error:
            print(
                "RPC JSON error:",
                error
            )

        except Exception as error:
            print(
                "RPC error:",
                error
            )
