# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository

https://github.com/khalidnass/sglang

## Project Overview

Docker container serving diffusion models (GLM-Image, Wan 2.2) via SGLang with OpenAI-compatible API. Designed for offline/OpenShift deployment.

**Supported models:** GLM-Image (image), Wan 2.2 T2V/I2V/TI2V (video)

## Commands

```bash
# Build (tags with git tag, e.g., glm-image-sglang:v0.6.0)
./build.sh

# Run with GLM-Image
docker run --gpus all -p 30000:30000 -e MODEL_PATH=/app/models/GLM-Image -v ./models:/app/models glm-image-sglang:v0.6.0

# Run with Wan 2.2 T2V
docker run --gpus all -p 30000:30000 -e MODEL_PATH=/app/models/Wan2.2-T2V-A14B-Diffusers -v ./models:/app/models glm-image-sglang:v0.6.0

# Test API
curl http://localhost:30000/health
curl http://localhost:30000/v1/models

# Offline deployment
docker save glm-image-sglang:v0.6.0 -o glm-image-sglang-v0.6.0.tar
docker load -i glm-image-sglang-v0.6.0.tar
```

## Architecture

| File | Purpose |
|------|---------|
| `Dockerfile` | Based on `lmsysorg/sglang:latest`, adds transformers/diffusers from git main, Wan 2.2 deps (ffmpeg, opencv), runs as UID 1001 |
| `build.sh` | Pulls base image, builds with git tag |
| `download-packages.sh` | Downloads pip packages to `pip-cache/` for reference |

**API endpoints:** `/v1/images/generations`, `/v1/images/edits`, `/v1/video/generations` on port 30000

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | (required) | Path to model directory |
| `HF_HOME` | /app/models | Model cache directory |
| `HF_HUB_OFFLINE` | 1 | Air-gapped mode (set in image) |

## Critical Constraints

- **Do NOT pin diffusers/transformers** - GLM-Image/Wan 2.2 require git main
- **Do NOT use `latest` tag** - always use git tag version (e.g., `glm-image-sglang:v0.6.0`)
- **Image editing (`/v1/images/edits`) may fail** - SGLang bug, use text-to-image instead

## OpenShift/Kubernetes Notes

- Model loading takes ~2 minutes - add startupProbe (failureThreshold: 30, periodSeconds: 10)
- Requires ~40-50GB RAM for model loading - set memory limit to 64Gi
