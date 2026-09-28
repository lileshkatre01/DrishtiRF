import numpy as np
from typing import Dict, Any

from backend.dsp.iqcapture import IQCapture
from backend.dsp.symbol_rate import estimate_symbol_rate
from backend.dsp.amc.feature_classifier import classify_modulation_features
from backend.dsp.amc.cnn_classifier import classify_modulation_cnn
from backend.core.explain import generate_explanation

def classify_modulation(iq: IQCapture, min_confidence_threshold: float = 0.45) -> Dict[str, Any]:
    """
    Master Automatic Modulation Classification (AMC) Fusion Engine:
    Combines Symbol Rate Consensus, Classical Cumulants, and Deep CNN paths.
    """
    # 1. Estimate Symbol Rate
    symbol_rate_hz, symbol_rate_conf = estimate_symbol_rate(iq)

    # 2. Run Classical Feature Classifier (Cumulants + Instantaneous features)
    feat_res = classify_modulation_features(iq.samples)

    # 3. Run Deep CNN Classifier
    cnn_res = classify_modulation_cnn(iq.samples)

    # 4. Fusion Engine: Probability Weighting (60% Classical + 40% Deep)
    all_mods = ["2FSK", "4FSK", "BPSK", "QPSK", "8PSK", "16QAM", "64QAM"]
    fused_probs = {}

    for mod in all_mods:
        p_feat = feat_res["probabilities"].get(mod, 0.0)
        p_cnn = cnn_res["probabilities"].get(mod, 0.0)
        fused_probs[mod] = float(0.6 * p_feat + 0.4 * p_cnn)

    # Winner selection
    best_mod = max(fused_probs, key=fused_probs.get)
    best_conf = fused_probs[best_mod]

    # Map order and family
    mod_order_map = {"2FSK": 2, "4FSK": 4, "BPSK": 2, "QPSK": 4, "8PSK": 8, "16QAM": 16, "64QAM": 64}
    mod_family_map = {"2FSK": "FSK", "4FSK": "FSK", "BPSK": "PSK", "QPSK": "PSK", "8PSK": "PSK", "16QAM": "QAM", "64QAM": "QAM"}

    final_mod = best_mod
    final_family = mod_family_map.get(best_mod, "UNKNOWN")
    final_order = mod_order_map.get(best_mod, 0)

    # Graceful degradation to "UNKNOWN" if below threshold
    if best_conf < min_confidence_threshold or iq.num_samples < 50:
        final_mod = "UNKNOWN"
        final_family = "UNKNOWN"
        final_order = 0
        best_conf = 0.0
        reason = "Signal SNR or sample count too low for confident modulation classification"
    else:
        reason = f"{feat_res['reason']}. Combined probability: {best_conf*100:.1f}%."

    explanation = generate_explanation("amc", {
        "modulation": final_mod,
        "confidence": best_conf,
        "reason": reason
    })

    return {
        "modulation": final_mod,
        "family": final_family,
        "order": final_order,
        "confidence": float(best_conf),
        "symbol_rate_baud": float(symbol_rate_hz),
        "symbol_rate_confidence": float(symbol_rate_conf),
        "probabilities": fused_probs,
        "explanation": explanation,
        "reason": reason,
        "features": feat_res.get("features", {})
    }
