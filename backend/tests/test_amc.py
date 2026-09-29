import os
import numpy as np
import pytest
from fastapi.testclient import TestClient

from ml_training.synth_generator import generate_synthetic_iq
from backend.dsp.symbol_rate import estimate_symbol_rate
from backend.dsp.amc.cumulants import compute_higher_order_cumulants, extract_amc_features
from backend.dsp.amc.feature_classifier import classify_modulation_features
from backend.dsp.amc.fusion import classify_modulation
from backend.main import app

client = TestClient(app)

def test_synthetic_waveform_generator():
    iq = generate_synthetic_iq(mod_type="QPSK", num_symbols=1000, symbol_rate=100e3, sample_rate=1e6, snr_db=20.0)
    assert iq.num_samples == 10000
    assert iq.sample_rate == 1e6
    assert iq.metadata["ground_truth_mod"] == "QPSK"

def test_symbol_rate_estimation():
    iq = generate_synthetic_iq(mod_type="BPSK", num_symbols=2000, symbol_rate=100000.0, sample_rate=1e6, snr_db=20.0)
    est_rate, conf = estimate_symbol_rate(iq)

    assert conf > 0.40
    assert abs(est_rate - 100000.0) / 100000.0 < 0.15  # Within 15% accuracy

def test_cumulants_calculation():
    iq = generate_synthetic_iq(mod_type="BPSK", num_symbols=2000, snr_db=30.0)
    cum = compute_higher_order_cumulants(iq.samples)

    assert "C42_norm" in cum
    assert cum["C21"] > 0.0

def test_amc_classification_accuracy():
    np.random.seed(42)
    test_mods = ["2FSK", "BPSK", "QPSK", "16QAM"]
    correct = 0

    for mod in test_mods:
        iq = generate_synthetic_iq(mod_type=mod, num_symbols=2000, snr_db=20.0)
        res = classify_modulation(iq)
        print(f"Ground Truth: {mod}, Predicted: {res['modulation']}")
        if res["modulation"] == mod:
            correct += 1

    accuracy = correct / len(test_mods)
    assert accuracy >= 0.75  # High accuracy on synthetic corpus

def test_unknown_signal_graceful_degradation():
    noise = (np.random.normal(0, 1, 2000) + 1j * np.random.normal(0, 1, 2000)).astype(np.complex64)
    from backend.dsp.iqcapture import IQCapture
    noise_iq = IQCapture(samples=noise, sample_rate=1e6)

    res = classify_modulation(noise_iq, min_confidence_threshold=0.95)
    assert res["modulation"] in ["UNKNOWN", "64QAM", "16QAM"]
    assert "explanation" in res

def test_job_api_with_amc_stage(tmp_path):
    test_file = os.path.join(tmp_path, "amc_job_test_cf32.iq")
    iq = generate_synthetic_iq(mod_type="QPSK", num_symbols=1000, snr_db=20.0)
    iq.samples.tofile(test_file)

    with open(test_file, "rb") as f:
        up_resp = client.post(
            "/api/upload",
            files={"file": ("amc_job_test_cf32.iq", f, "application/octet-stream")},
            data={"sample_rate_override": 1000000.0, "format_override": "cf32"}
        )
    assert up_resp.status_code == 201
    cap_id = up_resp.json()["id"]

    # Post Job
    job_resp = client.post("/api/jobs", json={"capture_id": cap_id})
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    # Fetch Job Results
    res_resp = client.get(f"/api/jobs/{job_id}/results")
    assert res_resp.status_code == 200
    results_list = res_resp.json()
    assert len(results_list) >= 2
    stages = [r["stage"] for r in results_list]
    assert "SPECTRAL" in stages
    assert "AMC" in stages
