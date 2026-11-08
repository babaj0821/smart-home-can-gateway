"""Bounded in-process queue carrying converted CAN telemetry.

Reconstructed for this organized repository from the API calls in the
provided CAN uplink converter and ScenarioConnector. Both must import
this module in the *same Gateway Python process* to share this queue.
"""

from copy import deepcopy
from queue import Empty, Full, Queue
from threading import Lock


class CanScenarioBridge:
    def __init__(self, maxsize=1000):
        self._telemetry = Queue(maxsize=maxsize)

    def push_telemetry(self, payload):
        """Enqueue a defensive copy; return False when the queue is full."""
        if not isinstance(payload, dict):
            return False
        try:
            self._telemetry.put_nowait(deepcopy(payload))
        except Full:
            return False
        return True

    def get_telemetry(self, timeout=0.25):
        """Get the next telemetry message, or None on timeout."""
        try:
            return self._telemetry.get(timeout=timeout)
        except Empty:
            return None

    def telemetry_qsize(self):
        return self._telemetry.qsize()


_bridge = None
_lock = Lock()


def get_can_scenario_bridge():
    """One bridge per interpreter/process."""
    global _bridge
    with _lock:
        if _bridge is None:
            _bridge = CanScenarioBridge()
        return _bridge
