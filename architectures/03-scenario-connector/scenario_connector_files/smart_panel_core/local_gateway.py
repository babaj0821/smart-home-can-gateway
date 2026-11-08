from threading import Lock


class LocalGateway:

    def __init__(
        self,
        state_store,
        command_outbox
    ):

        self.state_store = state_store

        self.command_outbox = (
            command_outbox
        )

        self._rpc_id_lock = Lock()

        self._next_rpc_id = 1


    def devices(
        self
    ):

        return self.state_store.device_names()


    def device_state(
        self,
        device_name
    ):

        return self.state_store.get(
            device_name
        )


    def _allocate_rpc_id(
        self
    ):

        with self._rpc_id_lock:

            rpc_id = self._next_rpc_id

            self._next_rpc_id += 1


            if (
                self._next_rpc_id
                >
                2147483647
            ):

                self._next_rpc_id = 1


            return rpc_id


    def send_rpc(
        self,
        device_name,
        method,
        params=None
    ):

        if params is None:

            params = {}


        if not device_name:

            raise ValueError(
                "Device name is required"
            )


        if not method:

            raise ValueError(
                "RPC method is required"
            )


        payload = {

            "device": device_name,

            "data": {

                "id":
                    self._allocate_rpc_id(),

                "method":
                    method,

                "params":
                    params

            }

        }


        accepted = (
            self.command_outbox.put(
                payload
            )
        )


        if not accepted:

            raise RuntimeError(
                "Local command outbox is full"
            )


        return {

            "accepted": True,

            "queued": True,

            "payload": payload

        }
