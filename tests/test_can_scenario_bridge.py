"""Dependency-free tests of the reconstructed in-process telemetry queue."""

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "architectures" / "03-scenario-connector" / "smart_panel_shared" / "can_scenario_bridge.py"
SPEC = importlib.util.spec_from_file_location("can_scenario_bridge", MODULE)
bridge_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge_module)


class TestCanScenarioBridge(unittest.TestCase):
    def test_fifo_and_copy(self):
        q = bridge_module.CanScenarioBridge(maxsize=2)
        msg = {"deviceName": "Lamp Controller", "telemetry": {"x": 1}}
        self.assertTrue(q.push_telemetry(msg))
        msg["telemetry"]["x"] = 999
        self.assertEqual(q.get_telemetry(timeout=0), {"deviceName": "Lamp Controller", "telemetry": {"x": 1}})

    def test_full_and_empty(self):
        q = bridge_module.CanScenarioBridge(maxsize=1)
        self.assertTrue(q.push_telemetry({"x": 1}))
        self.assertFalse(q.push_telemetry({"x": 2}))
        self.assertEqual(q.telemetry_qsize(), 1)
        self.assertEqual(q.get_telemetry(timeout=0), {"x": 1})
        self.assertIsNone(q.get_telemetry(timeout=0))


if __name__ == "__main__":
    unittest.main()
