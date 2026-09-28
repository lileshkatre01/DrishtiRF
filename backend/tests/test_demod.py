import os
import numpy as np
import pytest
from fastapi.testclient import TestClient

from ml_training.synth_generator import generate_synthetic_iq
from backend.dsp.demod.fsk import demodulate_fsk
from backend.dsp.demod.psk import demodulate_psk
from backend.dsp.demod.qam import demodulate_qam
from backend.dsp.demod.master_demod import demodulate_signal
from backend.dsp.demod.common import generate_constellation_points, generate_eye_diagram
from backend.main import app

client = TestClient(app)

def test_fsk_demodulation():
    iq = generate_synthetic_iq(mod_type="2FSK", num_symbols=1000, symbol_rate=100e3, snr_db=25.0)
    res = demodulate_fsk(iq, mod_type="2FSK", symbol_rate=100e3)

    assert "bits" in res
    assert "symbols" in res
    assert len(res["bits"]) > 0
    assert len(res["soft_symbols"]) == len(res["bits"])

def test_psk_demodulation():
    iq = generate_synthetic_iq(mod_type="QPSK", num_symbols=1000, symbol_rate=100e3, snr_db=25.0)
    res = demodulate_psk(iq, mod_type="QPSK", symbol_rate=100e3)

    assert "bits" in res
    assert "symbols" in res
    assert len(res["bits"]) == len(res["symbols"]) * 2
    assert len(res["soft_symbols"]) == len(res["bits"])

def test_qam_demodulation():
    iq = generate_synthetic_iq(mod_type="16QAM", num_symbols=1000, symbol_rate=100e3, snr_db=25.0)
    res = demodulate_qam(iq, mod_type="16QAM", symbol_rate=100e3)

    assert "bits" in res
    assert "symbols" in res
    assert len(res["bits"]) == len(res["symbols"]) * 4
    assert len(res["soft_symbols"]) == len(res["bits"])

def test_constellation_and_eye_diagram_generation():
    iq = generate_synthetic_iq(mod_type="QPSK", num_symbols=500)
    res = demodulate_signal(iq, mod_type="QPSK", symbol_rate=100e3)

    assert "constellation" in res
    assert "eye_diagram" in res
    assert len(res["constellation"]["i"]) > 0
    assert len(res["eye_diagram"]["traces"]) > 0

def test_job_api_with_demod_stage(tmp_path):
    test_file = os.path.join(tmp_path, "demod_job_test_cf32.iq")
    iq = generate_synthetic_iq(mod_type="QPSK", num_symbols=1000, snr_db=20.0)
    iq.samples.tofile(test_file)

    with open(test_file, "rb") as f:
        up_resp = client.post(
            "/api/upload",
            files={"file": ("demod_job_test_cf32.iq", f, "application/octet-stream")},
            data={"sample_rate_override": 1000000.0, "format_override": "cf32"}
        )
    assert up_resp.status_code == 201
    cap_id = up_resp.json()["id"]

    # Post Job (Executes SPECTRAL -> AMC -> DEMOD -> JOINT_SEARCH)
    job_resp = client.post("/api/jobs", json={"capture_id": cap_id})
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    # Fetch Job Results
    res_resp = client.get(f"/api/jobs/{job_id}/results")
    assert res_resp.status_code == 200
    results_list = res_resp.json()
    assert len(results_list) >= 3
    stages = [r["stage"] for r in results_list]
    assert "SPECTRAL" in stages
    assert "AMC" in stages
    assert "DEMOD" in stages
