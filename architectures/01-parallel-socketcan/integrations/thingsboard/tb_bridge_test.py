import time

from integrations.thingsboard.scenario_bridge import (
    ScenarioBridge
)


bridge = ScenarioBridge()

try:
    bridge.connect()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    bridge.disconnect()
