import os

from multiprocessing.managers import BaseManager, AutoProxy


class GatewayManager(BaseManager):
    pass


class GatewayClient:
    def __init__(self, address=None, authkey=None):
        if address is None:
            address = os.environ.get("GATEWAY_SOCKET_PATH", "/tmp/gateway")
        if authkey is None:
            key = os.environ.get("GATEWAY_AUTHKEY")
            if not key:
                raise RuntimeError("Set GATEWAY_AUTHKEY to match the Gateway-side manager")
            authkey = key.encode("utf-8")
        GatewayManager.register(
            "get_gateway",
            proxytype=AutoProxy
        )

        self.manager = GatewayManager(
            address=address,
            authkey=authkey
        )

        self.manager.connect()
        self.gateway = self.manager.get_gateway()

    def send_rpc(self, device_name, method, params=None):
        if params is None:
            params = {}

        content = {
            "device": device_name,
            "data": {
                "method": method,
                "params": params
            }
        }

        return self.gateway.send_local_rpc(content)

    def get_local_devices(self):
        return list(self.gateway.get_local_devices())

    def get_device_data(self, device_name):
        data = self.gateway.get_device_data(device_name)

        if data is None:
            return {}

        return dict(data)

    def get_available_connectors(self):
        return self.gateway.get_available_connectors()

    def devices(self):
        return self.get_local_devices()

    def device_state(self, device_name):
        return self.get_device_data(device_name)
