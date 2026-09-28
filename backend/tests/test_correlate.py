import pytest
import numpy as np
import os
import soundfile as sf
from fastapi.testclient import TestClient

from backend.main import app
from backend.dsp.sync_library import SYNC_PATTERNS, hex_to_bits, bits_to_hex
from backend.dsp.correlate import correlate_bitstream, calculate_shannon_entropy

client = TestClient(app)

def test_sync_library_conversions():
    # Test hex <-> bits conversion
    hex_val = "1acffc1d"
    bits = hex_to_bits(hex_val)
    assert len(bits) == 32
    assert bits_to_hex(bits) == hex_val

    # Verify standard registry contains Barker & CCSDS
    assert "Barker-13" in SYNC_PATTERNS
    assert "CCSDS-ASM-32" in SYNC_PATTERNS
    assert len(SYNC_PATTERNS["Barker-13"]["bits"]) == 13
    assert len(SYNC_PATTERNS["CCSDS-ASM-32"]["bits"]) == 32

def test_barker_sync_detection():
    # Construct bitstream with Barker-13 pattern inserted at offset 50 and 200
    barker13 = SYNC_PATTERNS["Barker-13"]["bits"]
    np.random.seed(42)
    bitstream = np.random.randint(0, 2, 400, dtype=np.uint8)

    bitstream[50:50+13] = barker13
    bitstream[200:200+13] = barker13

    res = correlate_bitstream(bitstream, sync_threshold=0.80)

    assert res["sync_found"] is True
    assert res["best_sync_word"] == "Barker-13"
    assert res["bit_inverted"] is False
    assert res["frame_count"] >= 2
    assert 50 in [f["offset"] for f in res["frames"]]

def test_ccsds_sync_detection():
    ccsds32 = SYNC_PATTERNS["CCSDS-ASM-32"]["bits"]
    np.random.seed(123)
    bitstream = np.random.randint(0, 2, 600, dtype=np.uint8)

    bitstream[100:100+32] = ccsds32
    bitstream[356:356+32] = ccsds32

    res = correlate_bitstream(bitstream, sync_threshold=0.85)

    assert res["sync_found"] is True
    assert res["best_sync_word"] == "CCSDS-ASM-32"
    assert res["frame_count"] >= 2
    assert 100 in [f["offset"] for f in res["frames"]]

def test_inverted_bitstream_correlation():
    # Construct bitstream with 180-degree inverted Barker-11
    barker11 = SYNC_PATTERNS["Barker-11"]["bits"]
    np.random.seed(99)
    bitstream = np.random.randint(0, 2, 300, dtype=np.uint8)

    # Inverted pattern insertion
    bitstream[80:80+11] = 1 - barker11

    res = correlate_bitstream(bitstream, sync_threshold=0.80)

    assert res["sync_found"] is True
    assert res["best_sync_word"] == "Barker-11"
    assert res["bit_inverted"] is True

def test_shannon_entropy():
    # Low entropy: repeated single byte
    low_ent_bytes = b"\xAA" * 100
    ent_low = calculate_shannon_entropy(low_ent_bytes)
    assert ent_low == 0.0

    # High entropy: pseudo-random byte stream
    np.random.seed(42)
    high_ent_bytes = np.random.randint(0, 256, 1000, dtype=np.uint8).tobytes()
    ent_high = calculate_shannon_entropy(high_ent_bytes)
    assert ent_high > 7.5

def test_api_job_correlation_stage(tmp_path):
    # Create synthetic WAV signal
    fs = 44100
    t = np.linspace(0, 0.1, int(fs * 0.1), endpoint=False)
    signal = 0.5 * np.cos(2 * np.pi * 1000 * t)
    
    file_path = tmp_path / "test_corr_signal.wav"
    sf.write(str(file_path), signal, fs)

    # 1. Upload signal
    with open(file_path, "rb") as f:
        resp = client.post("/api/upload", files={"file": ("test_corr_signal.wav", f, "audio/wav")})
    assert resp.status_code == 201
    cap_id = resp.json()["id"]

    # 2. Run Job
    job_resp = client.post("/api/jobs", json={"capture_id": cap_id})
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]
    assert job_resp.json()["status"] == "COMPLETED"
    assert job_resp.json()["progress"] == 100.0

    # 3. Check Stage Results (must include CORRELATION stage)
    res_resp = client.get(f"/api/jobs/{job_id}/results")
    assert res_resp.status_code == 200
    stages = [r["stage"] for r in res_resp.json()]
    assert "SPECTRAL" in stages
    assert "AMC" in stages
    assert "DEMOD" in stages
    assert "JOINT_SEARCH" in stages
    assert "CORRELATION" in stages

    # 4. Check Extracted Frames Endpoint
    frames_resp = client.get(f"/api/jobs/{job_id}/frames")
    assert frames_resp.status_code == 200
    assert isinstance(frames_resp.json(), list)
