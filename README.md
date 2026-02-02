# SGLang Examples

Python examples for using SGLang with Wan 2.2 video generation models.

## Prerequisites

1. Install dependencies:
```bash
pip install requests
```

2. Run SGLang server with Wan 2.2 model:
```bash
docker run --gpus all -p 30000:30000 \
  -e MODEL_PATH=/app/models/Wan2.2-T2V-A14B-Diffusers \
  -v ./models:/app/models \
  khalidnass/sglang:v0.5.0
```

## Usage

### Test Wan 2.2 Text-to-Video

```bash
python test_wan22.py
```

### Custom server URL

```bash
SGLANG_URL=http://your-server:30000 python test_wan22.py
```

## Supported Models

| Model | Description | Use Case |
|-------|-------------|----------|
| Wan 2.2 T2V | Text-to-Video | Generate video from text prompt |
| Wan 2.2 I2V | Image-to-Video | Animate a static image |
| Wan 2.2 TI2V | Text+Image-to-Video | Animate image with text guidance |

## API Examples

### Text-to-Video

```python
import requests
import base64

response = requests.post(
    "http://localhost:30000/v1/video/generations",
    json={
        "model": "Wan2.2-T2V",
        "prompt": "A cat walking in a garden",
        "size": "832x480",
        "extra_body": {
            "num_frames": 81,
            "num_inference_steps": 50,
            "guidance_scale": 5.0,
        },
    },
    timeout=600,
)

# Save video
video_b64 = response.json()["data"][0]["video"]
video_bytes = base64.b64decode(video_b64.split(",")[1])
with open("output.mp4", "wb") as f:
    f.write(video_bytes)
```

## Docker Image

Pull from Docker Hub:
```bash
docker pull khalidnass/sglang:v0.5.0
```

## Links

- [SGLang GitHub](https://github.com/sgl-project/sglang)
- [Wan 2.2 Models](https://huggingface.co/Wan-AI)
