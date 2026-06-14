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


def compute_qa_score(validation_results: dict, file_type: FileType) -> float:
    """Compute 0-100 quality score from validation results."""
    if not validation_results.get("file_size", {}).get("passed", True):
        return 0.0

    type_results = validation_results.get("type_specific", {})
    if not type_results.get("passed", True):
        return 20.0

    score = 100.0

    if file_type == FileType.IMAGE:
        width = type_results.get("width", 0)
        height = type_results.get("height", 0)
        if width < 512 or height < 512:
            score -= 20
        if type_results.get("mode") not in ["RGB", "RGBA"]:
            score -= 10

    elif file_type == FileType.AUDIO:
        duration = type_results.get("duration_seconds", 0)
        bitrate = type_results.get("bitrate", 0) or 0
        if bitrate < 64000:
            score -= 20
        if duration < 3:
            score -= 10

    return max(0.0, min(100.0, score))



async def analyze_with_ai(
    file_content: bytes,
    file_type: FileType,
    filename: str,
    validation_results: dict
) -> Optional[str]:
    """Use Groq to analyze submission quality."""
    if not settings.groq_api_key:
        return None

    try:
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)

        context = f"""You are a QA analyst for an AI training data company.
A contributor submitted a {file_type.value} file named '{filename}'.

Validation results:
{validation_results}

Provide a brief 2-3 sentence quality assessment. Be specific about:
1. Whether this submission is suitable for AI training data
2. Any quality concerns
3. A recommendation: PASS, FLAG, or REJECT

Keep your response under 100 words."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": context}],
            max_tokens=200,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"



async def run_qa_pipeline(
    file_content: bytes,
    filename: str,
    file_type: FileType,
    file_size: int,
) -> dict:
    """Run full QA pipeline on a submission."""
    start_time = time.time()

    results = {}

    # File size check
    results["file_size"] = validate_file_size(file_size)

    # Type-specific validation
    if file_type == FileType.IMAGE:
        results["type_specific"] = validate_image(file_content)
    elif file_type == FileType.AUDIO:
        results["type_specific"] = validate_audio(file_content, filename)
    else:
        results["type_specific"] = {"passed": True, "note": "Video validation not yet implemented"}

    # Compute score
    score = compute_qa_score(results, file_type)
    results["qa_score"] = score

    # AI analysis
    ai_analysis = await analyze_with_ai(file_content, file_type, filename, results)

    # Determine final status
    size_passed = results["file_size"].get("passed", True)
    type_passed = results["type_specific"].get("passed", True)

    if not size_passed or not type_passed:
        status = QAStatus.FAILED
        flag_reason = results["file_size"].get("reason") or results["type_specific"].get("reason")
    elif score < 50:
        status = QAStatus.FLAGGED
        flag_reason = f"Low quality score: {score:.1f}/100"
    else:
        status = QAStatus.PASSED
        flag_reason = None

    processing_time = int((time.time() - start_time) * 1000)

    return {
        "status": status,
        "qa_score": score,
        "qa_results": results,
        "ai_analysis": ai_analysis,
        "flag_reason": flag_reason,
        "processing_time_ms": processing_time,
    }
