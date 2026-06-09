import argparse
import importlib
import platform
import sys
from typing import Iterable, List, Tuple


REQUIRED_PYTHON_VERSION = "3.8.10"

MODE_PACKAGES = {
    "dev": [
        "numpy",
        "pandas",
        "yaml",
        "dotenv",
        "pydantic",
        "tqdm",
        "joblib",
        "pytest",
        "black",
        "ruff",
        "mypy",
        "matplotlib",
    ],
    "train": [
        "numpy",
        "pandas",
        "yaml",
        "dotenv",
        "pydantic",
        "tqdm",
        "joblib",
        "scipy",
        "sklearn",
        "lightgbm",
        "xgboost",
        "mlflow",
        "onnx",
        "onnxruntime",
        "matplotlib",
    ],
    "edge": [
        "numpy",
        "pandas",
        "yaml",
        "dotenv",
        "pydantic",
        "tqdm",
        "joblib",
        "fastapi",
        "uvicorn",
        "paho.mqtt.client",
        "requests",
        "serial",
    ],
}


def check_python_version(strict_patch: bool = True) -> None:
    current_version = platform.python_version()
    major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"

    if major_minor != "3.8":
        raise RuntimeError(
            f"Invalid Python version. Required Python 3.8.x, "
            f"but current version is {current_version}"
        )

    if strict_patch and current_version != REQUIRED_PYTHON_VERSION:
        raise RuntimeError(
            f"Invalid Python patch version. Required {REQUIRED_PYTHON_VERSION}, "
            f"but current version is {current_version}"
        )

    print(f"Python version OK: {current_version}")


def check_imports(packages: Iterable[str]) -> None:
    failed: List[Tuple[str, str]] = []

    for package in packages:
        try:
            importlib.import_module(package)
            print(f"Package OK: {package}")
        except Exception as exc:
            failed.append((package, str(exc)))

    if failed:
        details = "\n".join(f"- {package}: {error}" for package, error in failed)
        raise RuntimeError(f"Some packages cannot be imported:\n{details}")


def check_torch() -> None:
    try:
        import torch
    except Exception as exc:
        raise RuntimeError(f"PyTorch cannot be imported: {exc}") from exc

    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"CUDA device name: {torch.cuda.get_device_name(0)}")


def check_tensorrt() -> None:
    try:
        import tensorrt as trt
    except Exception as exc:
        raise RuntimeError(f"TensorRT cannot be imported: {exc}") from exc

    print(f"TensorRT version: {trt.__version__}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["dev", "train", "edge"],
        default="dev",
        help="Environment mode to validate",
    )
    parser.add_argument(
        "--check-torch",
        action="store_true",
        help="Check PyTorch and CUDA availability",
    )
    parser.add_argument(
        "--check-tensorrt",
        action="store_true",
        help="Check TensorRT Python binding",
    )
    parser.add_argument(
        "--allow-python-patch-diff",
        action="store_true",
        help="Allow Python 3.8.x even if patch version is not exactly 3.8.10",
    )
    args = parser.parse_args()

    check_python_version(strict_patch=not args.allow_python_patch_diff)
    check_imports(MODE_PACKAGES[args.mode])

    if args.check_torch:
        check_torch()

    if args.check_tensorrt:
        check_tensorrt()

    print(f"Environment check passed for mode='{args.mode}'.")


if __name__ == "__main__":
    main()