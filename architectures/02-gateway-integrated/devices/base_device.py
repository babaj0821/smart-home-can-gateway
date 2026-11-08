class BaseDevice:
    def __init__(self, gateway, name):
        self.gateway = gateway
        self.name = name

    def send_rpc(self, method, params=None):
        return self.gateway.send_rpc(
            self.name,
            method,
            params or {}
        )

    def raw_state(self):
        return self.gateway.device_state(self.name)

    def attributes(self):
        data = self.raw_state()

        attributes = data.get("attributes", {})

        if attributes is None:
            return {}

        return attributes

    def telemetry(self):
        data = self.raw_state()

        telemetry = data.get("telemetry", [])

        if telemetry is None:
            return []

        return telemetry

    def latest_telemetry_values(self):
        values = {}

        for item in self.telemetry():
            if isinstance(item, dict):
                item_values = item.get("values")

                if isinstance(item_values, dict):
                    values.update(item_values)
                else:
                    values.update(item)

        return values

    def get_value(self, key, default=None):
        attrs = self.attributes()

        if key in attrs:
            return attrs.get(key)

        telemetry_values = self.latest_telemetry_values()

        if key in telemetry_values:
            return telemetry_values.get(key)

        return default

    def get_state(self):
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "attributes": self.attributes(),
            "telemetry": self.telemetry()
        }
