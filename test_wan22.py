#!/usr/bin/env python3
"""
Wan 2.2 Video Generation Example using SGLang

This script demonstrates how to generate videos using Wan 2.2 models
served by SGLang with OpenAI-compatible API.

Supported models:
- Wan 2.2 T2V (Text-to-Video)
- Wan 2.2 I2V (Image-to-Video)
- Wan 2.2 TI2V (Text+Image-to-Video)

Requirements:
- pip install openai
- SGLang server running with Wan 2.2 model
"""

import base64
import json
import os
from pathlib import Path

import requests

# Server configuration
SERVER_URL = os.getenv("SGLANG_URL", "http://localhost:30000")


def check_health():
    """Check if the server is healthy."""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def list_models():
    """List available models on the server."""
    response = requests.get(f"{SERVER_URL}/v1/models", timeout=10)
    response.raise_for_status()
    return response.json()


def generate_video_t2v(
    prompt: str,
    num_frames: int = 81,
    height: int = 480,
    width: int = 832,
    num_inference_steps: int = 50,
    guidance_scale: float = 5.0,
    output_path: str = "output_t2v.mp4",
):
    """
    Generate video from text prompt (Text-to-Video).

    Args:
        prompt: Text description of the video to generate
        num_frames: Number of frames (default 81 = ~3 seconds at 24fps)
        height: Video height in pixels
        width: Video width in pixels
        num_inference_steps: Number of denoising steps
        guidance_scale: Classifier-free guidance scale
        output_path: Path to save the generated video

    Returns:
        Path to the saved video file
    """
    payload = {
        "model": "Wan2.2-T2V",
        "prompt": prompt,
        "size": f"{width}x{height}",
        "n": 1,
        "extra_body": {
            "num_frames": num_frames,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
        },
    }

    print(f"Generating video from prompt: '{prompt}'")
    print(f"Resolution: {width}x{height}, Frames: {num_frames}")

    response = requests.post(
        f"{SERVER_URL}/v1/video/generations",
        json=payload,
        timeout=600,  # Video generation can take a while
    )
    response.raise_for_status()

    result = response.json()

    # Decode and save the video
    video_data = result["data"][0]["video"]
    if video_data.startswith("data:"):
        # Remove data URL prefix
        video_data = video_data.split(",", 1)[1]

    video_bytes = base64.b64decode(video_data)
    Path(output_path).write_bytes(video_bytes)

    print(f"Video saved to: {output_path}")
    return output_path


def generate_video_i2v(
    image_path: str,
    prompt: str = "",
    num_frames: int = 81,
    num_inference_steps: int = 50,
    guidance_scale: float = 5.0,
    output_path: str = "output_i2v.mp4",
):
    """
    Generate video from an input image (Image-to-Video).

    Args:
        image_path: Path to the input image
        prompt: Optional text prompt to guide the video
        num_frames: Number of frames to generate
        num_inference_steps: Number of denoising steps
        guidance_scale: Classifier-free guidance scale
        output_path: Path to save the generated video

    Returns:
        Path to the saved video file
    """
    # Read and encode the input image
    image_bytes = Path(image_path).read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Determine image type
    if image_path.lower().endswith(".png"):
        image_data = f"data:image/png;base64,{image_b64}"
    else:
        image_data = f"data:image/jpeg;base64,{image_b64}"

    payload = {
        "model": "Wan2.2-I2V",
        "image": image_data,
        "prompt": prompt,
        "n": 1,
        "extra_body": {
            "num_frames": num_frames,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
        },
    }

    print(f"Generating video from image: '{image_path}'")
    if prompt:
        print(f"With prompt: '{prompt}'")

    response = requests.post(
        f"{SERVER_URL}/v1/video/generations",
        json=payload,
        timeout=600,
    )
    response.raise_for_status()

    result = response.json()

    # Decode and save the video
    video_data = result["data"][0]["video"]
    if video_data.startswith("data:"):
        video_data = video_data.split(",", 1)[1]

    video_bytes = base64.b64decode(video_data)
    Path(output_path).write_bytes(video_bytes)

    print(f"Video saved to: {output_path}")
    return output_path


def main():
    """Main function demonstrating video generation."""
    print("=" * 60)
    print("Wan 2.2 Video Generation Example")
    print("=" * 60)

    # Check server health
    print("\nChecking server health...")
    if not check_health():
        print(f"ERROR: Server at {SERVER_URL} is not responding.")
        print("Make sure SGLang is running with a Wan 2.2 model.")
        print("\nExample:")
        print("  docker run --gpus all -p 30000:30000 \\")
        print("    -e MODEL_PATH=/app/models/Wan2.2-T2V-A14B-Diffusers \\")
        print("    -v ./models:/app/models \\")
        print("    khalidnass/sglang:v0.5.0")
        return

    print("Server is healthy!")

    # List available models
    print("\nAvailable models:")
    models = list_models()
    for model in models.get("data", []):
        print(f"  - {model['id']}")

    # Example: Text-to-Video generation
    print("\n" + "=" * 60)
    print("Text-to-Video Generation")
    print("=" * 60)

    prompt = "A cat walking gracefully across a sunlit garden, realistic, 4K"

    try:
        output = generate_video_t2v(
            prompt=prompt,
            num_frames=81,  # ~3 seconds at 24fps
            height=480,
            width=832,
            num_inference_steps=50,
            guidance_scale=5.0,
            output_path="cat_walking.mp4",
        )
        print(f"\nSuccess! Video saved to: {output}")
    except requests.exceptions.HTTPError as e:
        print(f"Error generating video: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
