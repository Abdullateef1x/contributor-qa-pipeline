import pytest
import io
from PIL import Image
from app.services.qa import (
    validate_file_size,
    validate_image,
    validate_audio,
    compute_qa_score,
    QUALITY_THRESHOLDS,
)
from app.models.submission import FileType


def make_test_image(width=512, height=512, format="JPEG") -> bytes:
    img = Image.new("RGB", (width, height), color=(100, 149, 237))
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


# ── File size validation ──────────────────────────────────────────────────────

def test_file_size_too_small():
    result = validate_file_size(500)
    assert result["passed"] is False
    assert "too small" in result["reason"]


def test_file_size_too_large():
    result = validate_file_size(200_000_000)
    assert result["passed"] is False
    assert "too large" in result["reason"]


def test_file_size_valid():
    result = validate_file_size(50_000)
    assert result["passed"] is True


# ── Image validation ──────────────────────────────────────────────────────────

def test_image_valid():
    img_bytes = make_test_image(512, 512)
    result = validate_image(img_bytes)
    assert result["passed"] is True
    assert result["width"] == 512
    assert result["height"] == 512


def test_image_too_small():
    img_bytes = make_test_image(100, 100)
    result = validate_image(img_bytes)
    assert result["passed"] is False
    assert "too small" in result["reason"]


def test_image_corrupt():
    result = validate_image(b"not an image at all")
    assert result["passed"] is False


def test_image_minimum_size_boundary():
    """Image exactly at minimum should pass."""
    min_w = QUALITY_THRESHOLDS["min_image_width"]
    min_h = QUALITY_THRESHOLDS["min_image_height"]
    img_bytes = make_test_image(min_w, min_h)
    result = validate_image(img_bytes)
    assert result["passed"] is True


def test_image_below_minimum_boundary():
    """Image one pixel below minimum should fail."""
    min_w = QUALITY_THRESHOLDS["min_image_width"]
    min_h = QUALITY_THRESHOLDS["min_image_height"]
    img_bytes = make_test_image(min_w - 1, min_h - 1)
    result = validate_image(img_bytes)
    assert result["passed"] is False


# ── QA Score ──────────────────────────────────────────────────────────────────

def test_qa_score_failed_size():
    results = {
        "file_size": {"passed": False, "reason": "too small"},
        "type_specific": {"passed": True},
    }
    score = compute_qa_score(results, FileType.IMAGE)
    assert score == 0.0


def test_qa_score_failed_type():
    results = {
        "file_size": {"passed": True},
        "type_specific": {"passed": False, "reason": "corrupt"},
    }
    score = compute_qa_score(results, FileType.IMAGE)
    assert score == 20.0


def test_qa_score_high_quality_image():
    results = {
        "file_size": {"passed": True},
        "type_specific": {"passed": True, "width": 1024, "height": 1024, "mode": "RGB"},
    }
    score = compute_qa_score(results, FileType.IMAGE)
    assert score == 100.0


def test_qa_score_low_res_image():
    results = {
        "file_size": {"passed": True},
        "type_specific": {"passed": True, "width": 300, "height": 300, "mode": "RGB"},
    }
    score = compute_qa_score(results, FileType.IMAGE)
    assert score == 80.0


def test_qa_score_clamped_between_0_and_100():
    results = {
        "file_size": {"passed": True},
        "type_specific": {"passed": True, "width": 100, "height": 100, "mode": "P"},
    }
    score = compute_qa_score(results, FileType.IMAGE)
    assert 0.0 <= score <= 100.0
