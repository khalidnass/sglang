#!/bin/bash
# Download packages to pip-cache for offline/faster Docker builds
# Run this once before build.sh
#
# Note: torch/cuda/python are in base image, no need to cache

set -e

CACHE_DIR="$(dirname "$0")/pip-cache"
mkdir -p "$CACHE_DIR"

echo "=== Downloading packages to $CACHE_DIR ==="

# transformers 5.0.0 (official release with GLM-Image)
echo ">>> Downloading transformers==5.0.0"
pip download -d "$CACHE_DIR" transformers==5.0.0

# diffusers from git main (official GLM-Image recommendation)
echo ">>> Downloading diffusers (git main)"
pip download -d "$CACHE_DIR" "git+https://github.com/huggingface/diffusers.git"

# Other ML dependencies
echo ">>> Downloading other dependencies"
pip download -d "$CACHE_DIR" \
    accelerate \
    sentencepiece \
    protobuf \
    pillow

# sglang v0.5.8 with diffusion support
echo ">>> Downloading sglang v0.5.8"
pip download -d "$CACHE_DIR" \
    "sglang[diffusion] @ git+https://github.com/sgl-project/sglang.git@v0.5.8#subdirectory=python"

echo ""
echo "=== Done. Cache contents ==="
ls -lh "$CACHE_DIR"
echo ""
echo "=== Total cache size ==="
du -sh "$CACHE_DIR"
