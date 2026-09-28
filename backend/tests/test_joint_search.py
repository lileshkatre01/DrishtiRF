import os
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.dsp.deinterleave.block import deinterleave_block, search_block_interleaver
from backend.dsp.deinterleave.convolutional import deinterleave_conv
from backend.dsp.deinterleave.diagonal import deinterleave_diagonal
from backend.dsp.deinterleave.pseudo_random import deinterleave_pseudo_random
from backend.dsp.fec.viterbi import encode_convolutional, decode_viterbi
from backend.dsp.fec.reed_solomon import decode_reed_solomon
from backend.dsp.fec.concatenated import decode_concatenated
from backend.dsp.fec.ldpc import decode_ldpc
from backend.dsp.joint_search import search_joint_deinterleave_fec
from ml_training.synth_generator import generate_synthetic_iq
from backend.main import app

client = TestClient(app)

def test_block_deinterleaver():
    bits = np.arange(16, dtype=np.uint8)
    deint = deinterleave_block(bits, rows=4, cols=4)
    assert len(deint) == 16
    assert np.any(deint != bits)

def test_convolutional_deinterleaver():
    bits = np.ones(32, dtype=np.uint8)
    deint = deinterleave_conv(bits, depth=4, span=2)
    assert len(deint) == 32

def test_viterbi_encoder_decoder():
    payload = np.array([1, 0, 1, 1, 0, 0, 1, 0], dtype=np.uint8)
    encoded = encode_convolutional(payload, rate="1/2", K=7)
    assert len(encoded) >= 16

    decoded, score = decode_viterbi(encoded, rate="1/2", K=7)
    assert len(decoded) >= 8
    assert np.array_equal(decoded[:len(payload)], payload)
    assert score >= 0.80

def test_reed_solomon_decoder():
    payload_bytes = b"DrishtiRF NTRO SIH 2026 Test Payload"
    import reedsolo
    codec = reedsolo.RSCodec(32)
    encoded_bytes = codec.encode(payload_bytes)
    encoded_bits = np.unpackbits(np.frombuffer(encoded_bytes, dtype=np.uint8))

    decoded_bits, success, err_count = decode_reed_solomon(encoded_bits, n=255, k=223)
    assert success is True
    assert len(decoded_bits) > 0

def test_joint_search_loop():
    payload = np.array([1, 0, 1, 1, 0, 1, 0, 0] * 8, dtype=np.uint8)
    encoded = encode_convolutional(payload, rate="1/2", K=7)
    
    res = search_joint_deinterleave_fec(encoded)
    assert "best_interleaver" in res
    assert "best_fec" in res
    assert "confidence" in res
    assert res["payload_bit_count"] > 0

def test_job_api_with_joint_search_stage(tmp_path):
    test_file = os.path.join(tmp_path, "joint_job_test_cf32.iq")
    iq = generate_synthetic_iq(mod_type="QPSK", num_symbols=1000, snr_db=20.0)
    iq.samples.tofile(test_file)

    with open(test_file, "rb") as f:
        up_resp = client.post(
            "/api/upload",
            files={"file": ("joint_job_test_cf32.iq", f, "application/octet-stream")},
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
    assert len(results_list) == 5
    stages = [r["stage"] for r in results_list]
    assert "SPECTRAL" in stages
    assert "AMC" in stages
    assert "DEMOD" in stages
    assert "JOINT_SEARCH" in stages
    assert "CORRELATION" in stages
