import os
import platform
from datetime import datetime, timezone

from dotenv import load_dotenv


def get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def main() -> None:
    load_dotenv()

    edge_id = get_env("EDGE_ID", "local-dev")
    machine_id = get_env("MACHINE_ID", "unknown-machine")
    model_name = get_env("MODEL_NAME", "not-configured")
    model_path = get_env("MODEL_PATH", "not-configured")
    inference_interval_sec = get_env("INFERENCE_INTERVAL_SEC", "1")

    print("Predictive Maintenance Service")
    print("=" * 40)
    print(f"Started at UTC: {datetime.now(timezone.utc).isoformat()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Machine arch: {platform.machine()}")
    print(f"EDGE_ID: {edge_id}")
    print(f"MACHINE_ID: {machine_id}")
    print(f"MODEL_NAME: {model_name}")
    print(f"MODEL_PATH: {model_path}")
    print(f"INFERENCE_INTERVAL_SEC: {inference_interval_sec}")
    print("=" * 40)

    # TODO:
    # 1. Load sensor / PLC / CNC data
    # 2. Apply time-series preprocessing
    # 3. Load model
    # 4. Run inference
    # 5. Send result to MQTT / REST API / database


if __name__ == "__main__":
    main()