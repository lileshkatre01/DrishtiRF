import os
import json
import tempfile
import numpy as np
import soundfile as sf
import pytest
from fastapi.testclient import TestClient

from backend.dsp.iqcapture import IQCapture
from backend.dsp.preprocess import remove_dc_offset, normalize_power, correct_iq_imbalance, preprocess_signal
from backend.dsp.ingestion import read_wav, read_raw_iq, read_sigmf, infer_format_and_params, read_signal_file
from backend.main import app

client = TestClient(app)

def test_iq_capture_dataclass():
    samples = np.array([1+1j, 2+2j, 3+3j], dtype=np.complex64)
    iq = IQCapture(samples=samples, sample_rate=1e6)
    assert iq.num_samples == 3
    assert abs(iq.duration_seconds - 3e-6) < 1e-9
    assert iq.mean_power > 0.0

def test_preprocessing_dc_and_normalization():
    # Signal with DC offset and non-unit power
    t = np.linspace(0, 1, 1000)
    samples = (np.cos(2*np.pi*10*t) + 0.5) + 1j * (np.sin(2*np.pi*10*t) - 0.3)
    iq = IQCapture(samples=samples.astype(np.complex64), sample_rate=1000.0)

    clean_iq = preprocess_signal(iq)
    
    # Verify DC mean is near zero
    assert abs(np.mean(np.real(clean_iq.samples))) < 1e-4
    assert abs(np.mean(np.imag(clean_iq.samples))) < 1e-4
    
    # Verify power is normalized to 1.0
    assert abs(clean_iq.mean_power - 1.0) < 1e-3

def test_read_wav_stereo_and_mono(tmp_path):
    # Test Stereo WAV (I/Q)
    stereo_file = os.path.join(tmp_path, "stereo_test.wav")
    sr = 44100
    t = np.linspace(0, 0.1, int(sr*0.1))
    i_data = np.cos(2*np.pi*1000*t).astype(np.float32)
    q_data = np.sin(2*np.pi*1000*t).astype(np.float32)
    stereo_data = np.column_stack((i_data, q_data))
    sf.write(stereo_file, stereo_data, sr)

    samples, wav_sr = read_wav(stereo_file)
    assert wav_sr == 44100
    assert len(samples) == len(t)
    assert np.iscomplexobj(samples)

def test_read_raw_iq_formats(tmp_path):
    # Test cs16 format
    cs16_file = os.path.join(tmp_path, "test_cs16.iq")
    raw_i = np.array([1000, -1000, 2000, -2000], dtype=np.int16)
    raw_q = np.array([500, -500, 1500, -1500], dtype=np.int16)
    interleaved = np.empty((raw_i.size + raw_q.size,), dtype=np.int16)
    interleaved[0::2] = raw_i
    interleaved[1::2] = raw_q
    interleaved.tofile(cs16_file)

    iq = read_raw_iq(cs16_file, fmt="cs16", sample_rate=2e6)
    assert iq.num_samples == 4
    assert iq.sample_rate == 2e6
    assert iq.source_format == "cs16"

def test_read_sigmf_sidecar(tmp_path):
    meta_path = os.path.join(tmp_path, "test_sigmf.sigmf-meta")
    data_path = os.path.join(tmp_path, "test_sigmf.sigmf-data")

    meta_content = {
        "global": {
            "core:datatype": "ci16_le",
            "core:sample_rate": 2000000.0
        },
        "captures": [
            {"core:frequency": 915000000.0}
        ]
    }
    with open(meta_path, "w") as f:
        json.dump(meta_content, f)

    # Write dummy binary data
    raw_data = np.array([100, 200, 300, 400], dtype=np.int16)
    raw_data.tofile(data_path)

    iq = read_sigmf(meta_path)
    assert iq.sample_rate == 2000000.0
    assert iq.center_freq == 915000000.0
    assert iq.num_samples == 2

def test_filename_inference(tmp_path):
    test_file = os.path.join(tmp_path, "rec_fs2000000_cf915000000_cs16.iq")
    with open(test_file, "wb") as f:
        f.write(b"\x00" * 400)

    fmt, sr, cf, conf = infer_format_and_params(test_file)
    assert fmt == "cs16"
    assert sr == 2000000.0
    assert cf == 915000000.0

def test_upload_api_endpoint(tmp_path):
    # Create test raw IQ file
    test_file = os.path.join(tmp_path, "upload_test_cs16.iq")
    raw_data = np.array([1000, 500, -1000, -500] * 100, dtype=np.int16)
    raw_data.tofile(test_file)

    with open(test_file, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("upload_test_cs16.iq", f, "application/octet-stream")},
            data={
                "sample_rate_override": 1000000.0,
                "format_override": "cs16"
            }
        )

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["filename"] == "upload_test_cs16.iq"
    assert json_data["format"] == "cs16"
    assert json_data["sample_rate"] == 1000000.0
    assert json_data["n_samples"] == 200
    assert "id" in json_data
