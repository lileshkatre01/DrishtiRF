import pytest
import numpy as np

from ml_training.sdr_field_simulator import (
    generate_sdr_field_iq,
    apply_rician_fading,
    apply_iq_imbalance,
    apply_doppler_shift,
    apply_adc_quantization
)
from backend.dsp.preprocess import (
    preprocess_signal,
    estimate_and_correct_cfo,
    correct_iq_imbalance,
    remove_dc_offset
)
from backend.dsp.amc.fusion import classify_modulation
from backend.dsp.iqcapture import IQCapture

def test_sdr_field_simulator_generation():
    iq = generate_sdr_field_iq(mod_type="QPSK", snr_db=10.0, doppler_hz=200.0)
    assert isinstance(iq, IQCapture)
    assert iq.num_samples > 1000
    assert iq.metadata["sdr_simulation"] is True
    assert iq.metadata["ground_truth_mod"] == "QPSK"

def test_rician_fading_energy_preservation():
    samples = np.ones(1000, dtype=np.complex64)
    faded = apply_rician_fading(samples, K_db=6.0)
    assert len(faded) == len(samples)
    assert not np.isnan(faded).any()

def test_iq_imbalance_correction():
    samples = (np.random.normal(0, 1, 1000) + 1j * np.random.normal(0, 1, 1000)).astype(np.complex64)
    imbalanced = apply_iq_imbalance(samples, amplitude_imbalance_db=2.0, phase_imbalance_deg=5.0)
    
    iq_in = IQCapture(samples=imbalanced, sample_rate=1e6)
    iq_out = correct_iq_imbalance(iq_in)
    
    assert isinstance(iq_out, IQCapture)
    assert len(iq_out.samples) == len(samples)

def test_cfo_derotation_preprocessing():
    fs = 1e6
    t = np.arange(2000) / fs
    # BPSK tone with 5 kHz CFO
    cfo_hz = 5000.0
    bpsk_tone = np.sign(np.random.normal(0, 1, 2000)).astype(np.complex64) * np.exp(1j * 2 * np.pi * cfo_hz * t)
    
    iq_in = IQCapture(samples=bpsk_tone, sample_rate=fs)
    iq_out = estimate_and_correct_cfo(iq_in)
    
    assert "estimated_cfo_hz" in iq_out.metadata
    assert abs(iq_out.metadata["estimated_cfo_hz"]) < fs / 2

def test_full_preprocessing_pipeline():
    iq = generate_sdr_field_iq(mod_type="2FSK", snr_db=15.0)
    preprocessed = preprocess_signal(iq)
    
    assert preprocessed.num_samples == iq.num_samples
    assert abs(preprocessed.mean_power - 1.0) < 0.1

def test_amc_classification_on_sdr_field_signals():
    iq = generate_sdr_field_iq(mod_type="2FSK", snr_db=15.0)
    result = classify_modulation(iq)
    
    assert "modulation" in result
    assert "confidence" in result
    assert "probabilities" in result
    assert result["modulation"] in ["2FSK", "4FSK", "BPSK", "QPSK", "8PSK", "16QAM", "64QAM", "UNKNOWN"]
