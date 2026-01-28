# GLM-Image Test - Single Cell for Colab A100
# Following OFFICIAL installation from https://huggingface.co/zai-org/GLM-Image
#
# Usage: Copy this entire file content into a single Colab cell and run
# Runtime: A100 GPU (Colab Pro) - needs ~40GB VRAM

import subprocess
import sys
import os
import threading

# Install PyTorch 2.9.1 with CUDA 12.8
print("=== Installing PyTorch 2.9.1 + CUDA 12.8 ===")
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "torch==2.9.1",
    "torchvision",
    "--index-url", "https://download.pytorch.org/whl/cu128"
], check=True)

# Official GLM-Image installation (from https://huggingface.co/zai-org/GLM-Image):
# pip install "sglang[diffusion] @ git+https://github.com/sgl-project/sglang.git#subdirectory=python"
# pip install git+https://github.com/huggingface/transformers.git
# pip install git+https://github.com/huggingface/diffusers.git

print("=== Installing sglang (official guide) ===")
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "sglang[diffusion] @ git+https://github.com/sgl-project/sglang.git#subdirectory=python"
], check=True)

print("=== Installing transformers from git (official guide) ===")
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "git+https://github.com/huggingface/transformers.git"
], check=True)

print("=== Installing diffusers from git (official guide) ===")
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "git+https://github.com/huggingface/diffusers.git"
], check=True)

# Verify transformers has GlmImageForConditionalGeneration
print("=== Verifying transformers installation ===")
result = subprocess.run([sys.executable, "-c",
    "from transformers import GlmImageForConditionalGeneration; print('GlmImageForConditionalGeneration OK')"
], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(f"ERROR: {result.stderr}")
    subprocess.run([sys.executable, "-c", "import transformers; print(f'transformers version: {transformers.__version__}')"])
    sys.exit(1)

print("=== Starting sglang serve ===")
import time
import requests
import base64
from PIL import Image
from io import BytesIO

os.environ["PYTHONUNBUFFERED"] = "1"
MODEL_PATH = "zai-org/GLM-Image"

def stream_output(proc):
    for line in iter(proc.stdout.readline, ''):
        if line:
            print(f"[SERVER] {line}", end='')

server_proc = subprocess.Popen(
    ["sglang", "serve", "--model-path", MODEL_PATH, "--port", "30000", "--host", "0.0.0.0"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

output_thread = threading.Thread(target=stream_output, args=(server_proc,), daemon=True)
output_thread.start()

print("=== Waiting for server to start ===")
max_wait = 600
ready = False
for i in range(max_wait):
    try:
        resp = requests.get("http://localhost:30000/health", timeout=5)
        if resp.status_code == 200:
            print(f"\n=== Server ready after {i} seconds! ===")
            ready = True
            break
    except:
        pass
    time.sleep(1)

if not ready:
    print("Server failed to start!")
    server_proc.terminate()
    sys.exit(1)

print("\n=== Testing /v1/images/generations ===")
response = requests.post(
    "http://localhost:30000/v1/images/generations",
    json={
        "model": "zai-org/GLM-Image",
        "prompt": 'A sunset with text "Hello" in the sky',
        "size": "1024x1024",
        "n": 1,
        "response_format": "b64_json"
    }
)

if response.status_code == 200:
    print("SUCCESS! Image generated.")
    data = response.json()
    img_b64 = data["data"][0]["b64_json"]
    img_bytes = base64.b64decode(img_b64)
    img = Image.open(BytesIO(img_bytes))
    img.save("test_output.png")
    display(img)
    print("Image saved to test_output.png")
else:
    print(f"FAILED: {response.status_code}")
    print(response.text)

print("\n=== Stopping server ===")
server_proc.terminate()
server_proc.wait()
print("=== Test complete ===")
