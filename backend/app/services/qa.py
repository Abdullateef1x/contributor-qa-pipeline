import time
import io
from typing import Optional
from PIL import Image
import mutagen
import anthropic
from app.config import settings
from app.models.submission import QAStatus, FileType


QUALITY_THRESHOLDS = {
    "min_image_width": 224,
    "min_image_height": 224,
    "min_audio_duration": 1.0,
    "max_audio_duration": 300.0,
    "min_file_size": 1024,        # 1KB
    "max_file_size": 104857600,   # 100MB
}

def validate_file_size(file_size: int):
    if file_size < QUALITY_THRESHOLDS["min_file_size"]:
        return {"passed": False, "reason": "file too small", "file_size": f"{file_size} bytes"}
    if file_size > QUALITY_THRESHOLDS["max_file_size"]:
        return {"passed": False, "reason": "file too large", "file_size": f"{file_size} bytes"}
    return {"passed": True}


def validate_image(file_content: bytes) -> dict:
    results = {}
    try:
        img = Image.open(io.BytesIO(file_content))
        width, height = img.size
        results["width"] = width
        results["height"] = height
        results["format"] = img.format
        results["mode"] = img.mode

        if width < QUALITY_THRESHOLDS["min_image_width"] or height < QUALITY_THRESHOLDS["min_image_height"]:
            results["passed"] = False
            results["reason"] = f"Image too small: {width}x{height}px (min 224x224)"
        else:
            results["passed"] = True

        # Check for corrupt image
        img.verify()
    except Exception as e:
        results["passed"] = False
        results["reason"] = f"Invalid or corrupt image: {str(e)}"

    return results


def validate_audio(file_content: bytes, filename: str) -> dict:
    results = {}
    try:
        audio = mutagen.mp3.MP3(io.BytesIO(file_content), filename=filename)
        if audio is None:
            return {"passed": False, "reason": "Could not parse audio file"}

        duration = audio.info.length if hasattr(audio, "info") else 0
        results["duration_seconds"] = round(duration, 2)
        results["format"] = type(audio).__name__

        if audio.info:
            results["bitrate"] = getattr(audio.info, "bitrate", None)
            results["sample_rate"] = getattr(audio.info, "sample_rate", None)

        if duration < QUALITY_THRESHOLDS["min_audio_duration"]:
            results["passed"] = False
            results["reason"] = f"Audio too short: {duration:.1f}s (min 1s)"
        elif duration > QUALITY_THRESHOLDS["max_audio_duration"]:
            results["passed"] = False
            results["reason"] = f"Audio too long: {duration:.1f}s (max 300s)"
        else:
            results["passed"] = True

    except Exception as e:
        results["passed"] = False
        results["reason"] = f"Invalid or corrupt audio: {str(e)}"

    return results