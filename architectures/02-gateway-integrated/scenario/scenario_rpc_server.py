import os
from multiprocessing.connection import Listener

from gateway.gateway_client import GatewayClient
from devices.device_manager import DeviceManager
from scenario.scenario_engine import ScenarioEngine


ADDRESS = os.environ.get("SMART_PANEL_SOCKET_PATH", "/tmp/smart_panel")


def load_authkey():
    key = os.environ.get("SMART_PANEL_AUTHKEY")
    if not key:
        raise RuntimeError("Set SMART_PANEL_AUTHKEY before starting the scenario RPC server")
    return key.encode("utf-8")


class SmartPanelScenarioService:
    def __init__(self):
        self.connect()

    def connect(self):
        self.gateway = GatewayClient()
        self.devices = DeviceManager(self.gateway)
        self.engine = ScenarioEngine(self.devices)

    def handle(self, request):
        try:
            method = request.get("method")
            params = request.get("params") or {}

            # Avoid logging RPC parameters: scenarios may contain private device data.

            if method == "refresh":
                self.connect()
                return {
                    "success": True
                }

            if method == "getScenarios":
                return self.engine.getScenarios(params)

            if method == "getScenario":
                return self.engine.getScenario(params)

            if method == "createScenario":
                return self.engine.createScenario(params)

            if method == "updateScenario":
                return self.engine.updateScenario(params)

            if method == "deleteScenario":
                return self.engine.deleteScenario(params)

            if method == "runScenario":
                return self.engine.runScenario(params)

            return {
                "success": False,
                "error": f"Unknown method: {method}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def main():
    if os.path.exists(ADDRESS):
        os.remove(ADDRESS)

    service = SmartPanelScenarioService()

    listener = Listener(
        ADDRESS,
        authkey=load_authkey()
    )

    print("Smart Panel Scenario RPC Server")
    print("Listening on:", ADDRESS)
    print("Ready.", flush=True)

    while True:
        conn = listener.accept()

        try:
            request = conn.recv()
            response = service.handle(request)
            conn.send(response)

        except Exception as e:
            conn.send(
                {
                    "success": False,
                    "error": str(e)
                }
            )

        finally:
            conn.close()


if __name__ == "__main__":
    main()
