"""Local configuration, loaded from environment variables (no secrets in source)."""

import os

TB_HOST = os.environ.get("TB_HOST", "127.0.0.1")
TB_PORT = int(os.environ.get("TB_PORT", "1883"))
TB_TOKEN = os.environ.get("TB_TOKEN", "")
