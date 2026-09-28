import pytest
from backend.core.confidence import evaluate_job_confidence, ConfidenceTier

def test_confidence_tier_a_eval():
    results_a = {
        "spectral": {"snr_db": 15.0, "snr_confidence": 0.95},
        "amc": {"modulation": "QPSK", "confidence": 0.90},
        "demod": {"bit_count": 500},
        "joint_search": {"syndrome_zero": True, "confidence": 0.98},
        "correlation": {"sync_found": True, "best_sync_word": "Barker-13", "confidence": 0.95}
    }
    eval_res = evaluate_job_confidence(results_a)
    assert eval_res["tier_code"] == "TIER_A"
    assert "High-Confidence" in eval_res["tier"]
    assert eval_res["overall_confidence"] > 0.80
    assert eval_res["sub_scores"]["joint_fec"] > 0.80

def test_confidence_tier_b_eval():
    results_b = {
        "spectral": {"snr_db": 8.0, "snr_confidence": 0.80},
        "amc": {"modulation": "2FSK", "confidence": 0.70},
        "demod": {"bit_count": 200},
        "joint_search": {"syndrome_zero": False, "confidence": 0.40},
        "correlation": {"sync_found": False, "best_sync_word": "None", "confidence": 0.20}
    }
    eval_res = evaluate_job_confidence(results_b)
    assert eval_res["tier_code"] == "TIER_B"
    assert "Demodulated" in eval_res["tier"]
    assert eval_res["overall_confidence"] > 0.30

def test_confidence_tier_c_eval():
    results_c = {
        "spectral": {"snr_db": 1.2, "snr_confidence": 0.30},
        "amc": {"modulation": "Unknown", "confidence": 0.20},
        "demod": {"bit_count": 0},
        "joint_search": {"syndrome_zero": False, "confidence": 0.10},
        "correlation": {"sync_found": False, "best_sync_word": "None", "confidence": 0.0}
    }
    eval_res = evaluate_job_confidence(results_c)
    assert eval_res["tier_code"] == "TIER_C"
    assert "Spectral" in eval_res["tier"]
