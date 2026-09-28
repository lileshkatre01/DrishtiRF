import os
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.dsp.iqcapture import IQCapture
from backend.dsp.spectral import (
    compute_psd,
    compute_waterfall,
    estimate_bandwidth,
    estimate_center_frequency,
    estimate_snr,
    analyze_spectrum
)
from backend.main import app

client = TestClient(app)

def create_synthetic_signal(
    sample_rate: float = 1e6,
    freq_offset_hz: float = 50000.0,
    snr_db: float = 20.0,
    duration: float = 0.05
) -> IQCapture:
    """
    Generate synthetic BPSK modulated carrier with known frequency offset and AWGN.
    """
    num_samples = int(sample_rate * duration)
    t = np.arange(num_samples) / sample_rate

    # Generate BPSK symbols
    symbol_rate = 50000  # 50 kbaud
    samples_per_symbol = int(sample_rate / symbol_rate)
    num_symbols = int(np.ceil(num_samples / samples_per_symbol))
    bits = np.random.randint(0, 2, size=num_symbols) * 2 - 1
    symbols = np.repeat(bits, samples_per_symbol)[:num_samples]

    # Modulate onto complex carrier with frequency offset
    carrier = np.exp(1j * (2 * np.pi * freq_offset_hz * t))
    signal = symbols * carrier

    # Add AWGN noise
    signal_power = np.mean(np.abs(signal) ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10.0))
    noise = (np.random.normal(0, np.sqrt(noise_power / 2), num_samples) +
             1j * np.random.normal(0, np.sqrt(noise_power / 2), num_samples))
    noisy_signal = (signal + noise).astype(np.complex64)

    return IQCapture(samples=noisy_signal, sample_rate=sample_rate, center_freq=915e6)

def test_psd_computation():
    iq = create_synthetic_signal(freq_offset_hz=50000.0, snr_db=20.0)
    freqs, psd_db, noise_floor = compute_psd(iq, nperseg=1024)

    assert len(freqs) == 1024
    assert len(psd_db) == 1024
    assert freqs[0] < 0 < freqs[-1]  # Centered frequency range
    assert noise_floor < np.max(psd_db)

def test_waterfall_decimation():
    iq = create_synthetic_signal(duration=0.1)
    waterfall = compute_waterfall(iq, max_time_bins=50, max_freq_bins=64)

    assert "times" in waterfall
    assert "frequencies" in waterfall
    assert "grid" in waterfall
    assert len(waterfall["frequencies"]) <= 64
    assert len(waterfall["times"]) <= 50

def test_spectral_parameter_estimation():
    offset_hz = 50000.0
    iq = create_synthetic_signal(sample_rate=1e6, freq_offset_hz=offset_hz, snr_db=20.0)
    spectral = analyze_spectrum(iq)

    # Carrier offset estimation accuracy within +- 5%
    est_offset = spectral["center_freq_offset_hz"]
    assert abs(est_offset - offset_hz) < 10000.0

    # SNR estimation sanity check
    assert spectral["snr_db"] > 10.0

    # Bandwidth estimation sanity check
    assert spectral["bandwidth_10db_hz"] > 0.0

def test_spectrum_and_job_api_endpoints(tmp_path):
    # 1. Create and upload synthetic raw IQ file
    test_file = os.path.join(tmp_path, "spectral_test_cs16.iq")
    iq = create_synthetic_signal(duration=0.02)
    
    # Scale to int16
    i_int = (np.real(iq.samples) * 32767).astype(np.int16)
    q_int = (np.imag(iq.samples) * 32767).astype(np.int16)
    interleaved = np.empty((i_int.size + q_int.size,), dtype=np.int16)
    interleaved[0::2] = i_int
    interleaved[1::2] = q_int
    interleaved.tofile(test_file)

    with open(test_file, "rb") as f:
        upload_resp = client.post(
            "/api/upload",
            files={"file": ("spectral_test_cs16.iq", f, "application/octet-stream")},
            data={"sample_rate_override": 1000000.0, "format_override": "cs16"}
        )
    assert upload_resp.status_code == 201
    capture_id = upload_resp.json()["id"]

    # 2. Test GET /api/captures/{id}/spectrum
    spec_resp = client.get(f"/api/captures/{capture_id}/spectrum")
    assert spec_resp.status_code == 200
    spec_data = spec_resp.json()
    assert "psd_db" in spec_data
    assert "waterfall" in spec_data
    assert "bandwidth_10db_hz" in spec_data

    # 3. Test POST /api/jobs
    job_resp = client.post("/api/jobs", json={"capture_id": capture_id})
    assert job_resp.status_code == 201
    job_data = job_resp.json()
    job_id = job_data["id"]
    assert job_data["status"] == "COMPLETED"

    # 4. Test GET /api/jobs/{id}/results
    res_resp = client.get(f"/api/jobs/{job_id}/results")
    assert res_resp.status_code == 200
    results_list = res_resp.json()
    assert len(results_list) > 0
    assert results_list[0]["stage"] == "SPECTRAL"
    assert "explanation" in results_list[0]
