#!/bin/bash
# Build script for GLM-Image Docker image
# Pulls base image first to ensure latest version and faster builds

set -e

IMAGE_NAME="glm-image-sglang"
BASE_IMAGE="pytorch/pytorch:2.9.1-cuda12.8-cudnn9-runtime"

echo "=== Pulling base image ==="
docker pull $BASE_IMAGE

echo "=== Building $IMAGE_NAME ==="
docker build -t $IMAGE_NAME .

echo "=== Done ==="
echo "Run with: docker run --gpus all -p 30000:30000 $IMAGE_NAME"
