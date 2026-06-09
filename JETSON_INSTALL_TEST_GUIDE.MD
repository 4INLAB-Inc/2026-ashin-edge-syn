# Jetson Edge 설치 및 테스트 가이드

Project: `2026-ashin-edge-syn`
Repository: `git@github.com:4INLAB-Inc/2026-ashin-edge-syn.git`

본 문서는 Jetson Edge PC에서 Docker 기반 실행 환경을 설치하고 테스트하는 절차를 정리한 문서입니다.

---

## 1. 테스트 완료 환경

```text
Jetson Host: L4T R35.4.1
Ubuntu: 20.04.6 LTS
Host Python: 3.8.10
Docker: 24.0.5
Docker Base Image: nvcr.io/nvidia/l4t-jetpack:r35.4.1
Docker Python: 3.8.10
Docker TensorRT: 8.5.2.2
Architecture: aarch64
```

---

## 2. Jetson Host 환경 확인

Jetson에서 Terminal을 열고 아래 명령어를 실행합니다.

```bash
cat /etc/nv_tegra_release
lsb_release -a
python3 --version
docker --version
```

정상 결과 예시:

```text
R35, REVISION: 4.1
Ubuntu 20.04.6 LTS
Python 3.8.10
Docker version 24.x
```

---

## 3. GitHub에서 Source Code Clone

### 3.1 Repository clone

```bash
cd ~
git clone git@github.com:4INLAB-Inc/2026-ashin-edge-syn.git
cd 2026-ashin-edge-syn
```

기존에 실패한 폴더가 있다면 삭제 후 다시 clone합니다.

```bash
cd ~
rm -rf 2026-ashin-edge-syn
git clone git@github.com:4INLAB-Inc/2026-ashin-edge-syn.git
cd 2026-ashin-edge-syn
```

---

## 4. Docker Base Image 확인

Jetson Host가 `L4T R35.4.1`이므로 Docker base image도 동일 계열의 JetPack image를 사용합니다.

사용 image:

```text
nvcr.io/nvidia/l4t-jetpack:r35.4.1
```

Docker base image의 Python을 확인합니다.

```bash
sudo docker run --rm --runtime nvidia nvcr.io/nvidia/l4t-jetpack:r35.4.1 python3 --version
```

정상 결과:

```text
Python 3.8.10
```

Docker base image의 TensorRT를 확인합니다.

```bash
sudo docker run --rm --runtime nvidia nvcr.io/nvidia/l4t-jetpack:r35.4.1 python3 -c "import tensorrt as trt; print(trt.__version__)"
```

정상 결과:

```text
8.5.2.2
```

이 단계가 통과하면 아래 항목이 정상입니다.

```text
Jetson Host L4T R35.4.1 OK
Docker Base Image R35.4.1 OK
Python 3.8.10 OK
TensorRT 8.5.2.2 OK
NVIDIA Docker Runtime OK
```

---

## 5. Dockerfile 설정

파일 위치:

```text
docker/Dockerfile.jetson
```

Base image는 아래처럼 설정합니다.

```dockerfile
ARG BASE_IMAGE=nvcr.io/nvidia/l4t-jetpack:r35.4.1
FROM ${BASE_IMAGE}
```

Docker build 단계에서는 기본 Python package만 확인합니다.

```dockerfile
RUN python3 scripts/check_env.py --mode edge
```

아래처럼 build 단계에서 TensorRT를 확인하지 않습니다.

```dockerfile
RUN python3 scripts/check_env.py --mode edge --check-tensorrt
```

이유:

```text
TensorRT는 NVIDIA runtime과 함께 container 실행 시 확인하는 것이 안전합니다.
build 단계에서는 일부 NVIDIA runtime library가 mount되지 않아
libnvdla_compiler.so 오류가 발생할 수 있습니다.
```

---

## 6. Project Docker Image Build

Repository 폴더로 이동합니다.

```bash
cd ~/2026-ashin-edge-syn
```

Docker image를 build합니다.

```bash
sudo docker build -f docker/Dockerfile.jetson -t 2026-ashin-edge-syn:edge .
```

정상 결과 예시:

```text
Successfully built ...
Successfully tagged 2026-ashin-edge-syn:edge
```

아래 경고는 무시해도 됩니다.

```text
DEPRECATED: The legacy builder is deprecated
```

---

## 7. Docker에서 App 실행 테스트

아래 명령어를 한 줄로 실행합니다.

```bash
sudo docker run --rm --runtime nvidia -e EDGE_ID=edge-01 -e MACHINE_ID=CNC-01 -e MODEL_NAME=test-model -e MODEL_PATH=/workspace/models/test-model.onnx -e INFERENCE_INTERVAL_SEC=1 2026-ashin-edge-syn:edge
```

정상 결과 예시:

```text
Predictive Maintenance Service
========================================
Started at UTC: ...
Python version: 3.8.10
Machine arch: aarch64
EDGE_ID: edge-01
MACHINE_ID: CNC-01
MODEL_NAME: test-model
MODEL_PATH: /workspace/models/test-model.onnx
INFERENCE_INTERVAL_SEC: 1
========================================
```

---

## 8. Docker Edge 환경 테스트

아래 명령어로 edge 환경과 TensorRT를 확인합니다.

```bash
sudo docker run --rm --runtime nvidia 2026-ashin-edge-syn:edge python3 scripts/check_env.py --mode edge --check-tensorrt
```

정상 결과 예시:

```text
Python version OK: 3.8.10
Package OK: numpy
Package OK: pandas
Package OK: yaml
Package OK: dotenv
Package OK: pydantic
Package OK: tqdm
Package OK: joblib
Package OK: fastapi
Package OK: uvicorn
Package OK: paho.mqtt.client
Package OK: requests
Package OK: serial
TensorRT version: 8.5.2.2
Environment check passed for mode='edge'.
```

이 단계까지 통과하면 Jetson Docker 환경은 정상입니다.

---

## 9. GitHub 코드 업데이트 후 재빌드

Windows 개발 PC에서 GitHub로 code를 push한 후, Jetson에서는 아래 명령어를 실행합니다.

```bash
cd ~/2026-ashin-edge-syn
git pull
sudo docker build -f docker/Dockerfile.jetson -t 2026-ashin-edge-syn:edge .
```

App 실행 테스트:

```bash
sudo docker run --rm --runtime nvidia -e EDGE_ID=edge-01 -e MACHINE_ID=CNC-01 -e MODEL_NAME=test-model -e MODEL_PATH=/workspace/models/test-model.onnx -e INFERENCE_INTERVAL_SEC=1 2026-ashin-edge-syn:edge
```

TensorRT 테스트:

```bash
sudo docker run --rm --runtime nvidia 2026-ashin-edge-syn:edge python3 scripts/check_env.py --mode edge --check-tensorrt
```

---

## 10. 빠른 테스트 명령어

설치가 완료된 이후에는 아래 명령어만 실행하면 됩니다.

```bash
cd ~/2026-ashin-edge-syn
git pull
sudo docker build -f docker/Dockerfile.jetson -t 2026-ashin-edge-syn:edge .
sudo docker run --rm --runtime nvidia -e EDGE_ID=edge-01 -e MACHINE_ID=CNC-01 -e MODEL_NAME=test-model -e MODEL_PATH=/workspace/models/test-model.onnx -e INFERENCE_INTERVAL_SEC=1 2026-ashin-edge-syn:edge
sudo docker run --rm --runtime nvidia 2026-ashin-edge-syn:edge python3 scripts/check_env.py --mode edge --check-tensorrt
```

모든 명령어가 정상 실행되면 아래 환경이 모두 준비된 것입니다.

```text
Windows 개발/학습 환경 OK
GitHub 동기화 OK
Jetson Docker 환경 OK
TensorRT Docker Runtime OK
```

## 11. 최종 확인 결과

Windows native 개발 PC:

```text
Python 3.8.10 OK
PyTorch 2.3.1+cu118 OK
CUDA 11.8 OK
RTX 4090 OK
ONNX 1.16.0 OK
Train environment OK
```

Jetson Docker:

```text
Docker build OK
App run OK
Python 3.8.10 OK
Architecture aarch64 OK
TensorRT 8.5.2.2 OK
Edge requirements OK
```

최종 결론:

```text
Windows 개발/학습 환경 준비 완료
GitHub 동기화 준비 완료
Jetson Docker Edge 환경 준비 완료
동일 절차로 나머지 Jetson Edge PC도 설정 가능
```
