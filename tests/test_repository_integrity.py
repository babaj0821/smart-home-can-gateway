"""Non-hardware checks for public example configs and documentation links."""

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"


class RepositoryIntegrityTests(unittest.TestCase):
    def test_json_examples_are_parseable(self):
        for path in sorted(ROOT.rglob("*.json")):
            with self.subTest(path=path.relative_to(ROOT)):
                json.loads(path.read_text(encoding="utf-8"))

    def test_gateway_examples_use_nonfunctional_tokens(self):
        for name in ("01-parallel-socketcan", "02-gateway-integrated", "03-scenario-connector"):
            base = CONFIG / name
            config_path = base / "gateway" / "tb_gateway.json" if name.startswith("03") else base / "tb_gateway.json"
            gateway = json.loads(config_path.read_text(encoding="utf-8"))
            with self.subTest(architecture=name):
                self.assertEqual(gateway["thingsboard"]["host"], "thingsboard.example.invalid")
                self.assertEqual(gateway["thingsboard"]["security"]["accessToken"], "replace-with-gateway-token")
                self.assertEqual(gateway["thingsboard"]["managerEnabled"], name.startswith("02"))
                for connector in gateway["connectors"]:
                    self.assertTrue((config_path.parent / connector["configuration"]).exists())

    def test_example_connector_ids_are_consistent(self):
        configs = [CONFIG / "01-parallel-socketcan" / "padnaCanGateway.json",
                   CONFIG / "02-gateway-integrated" / "padnaCanGateway.json",
                   CONFIG / "03-scenario-connector" / "gateway" / "padnaCanGateway.json"]
        ids = {json.loads(path.read_text(encoding="utf-8"))["id"] for path in configs}
        self.assertEqual(len(ids), 1)

    def test_upstream_license_and_modification_notice(self):
        folder = ROOT / "architectures" / "02-gateway-integrated" / "gateway_patch"
        source = (folder / "tb_gateway_service.py").read_text(encoding="utf-8")
        license_text = (folder / "LICENSE-APACHE-2.0.txt").read_text(encoding="utf-8")
        notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
        self.assertIn("Copyright 2026. ThingsBoard", source)
        self.assertIn("Modified by Iman Babajani in 2026", source)
        self.assertIn("Apache License", license_text)
        self.assertIn("tb_gateway_service.py", notice)
        self.assertNotIn("LOCAL CACHE UPDATED:", source)

    def test_local_markdown_links(self):
        # Only file targets are checked here; hosted docs and section anchors
        # are outside the scope of this simple source-level test.
        pattern = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
        for path in ROOT.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            for link in pattern.findall(content):
                target = unquote(link.split("#", 1)[0]).strip()
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                with self.subTest(document=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / target).exists(), f"Missing target {target} in {path}")


if __name__ == "__main__":
    unittest.main()
