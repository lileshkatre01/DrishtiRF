import numpy as np
from typing import Dict, Any

from backend.dsp.amc.cumulants import extract_amc_features, compute_higher_order_cumulants

def classify_modulation_features(samples: np.ndarray) -> Dict[str, Any]:
    """
    Classical Feature-Based AMC Classifier using higher-order cumulants and instantaneous features.
    """
    if len(samples) < 100:
        return {
            "modulation": "UNKNOWN",
            "family": "UNKNOWN",
            "order": 0,
            "confidence": 0.0,
            "probabilities": {},
            "reason": "Insufficient samples for feature classification"
        }

    feat = extract_amc_features(samples)
    cum = compute_higher_order_cumulants(samples)
    
    c20_mag = float(np.abs(cum["C20"]))
    c21 = float(cum["C21"])
    c40_norm = float(cum["C40_norm"])
    c42_norm = float(cum["C42_norm"])
    sig_ap = feat["sigma_ap"]
    sig_af = feat["sigma_af"]
    med_dphase = feat["median_diff_phase"]
    papr = feat["papr_db"]

    c20_norm = c20_mag / (c21 + 1e-12)

    # 1. Variable Envelope (QAM Family)
    if sig_ap > 0.22 or papr > 3.8:
        family = "QAM"
        if sig_ap < 0.45 or c42_norm > -0.75:
            mod = "16QAM"
            order = 16
            conf = 0.92
            reason = f"Multi-amplitude envelope (sigma_ap={sig_ap:.2f}) and C42_norm={c42_norm:.2f} match 16-QAM"
        else:
            mod = "64QAM"
            order = 64
            conf = 0.88
            reason = f"Multi-amplitude QAM distribution (sigma_ap={sig_ap:.2f}, PAPR={papr:.1f} dB)"

    # 2. Continuous Tone Frequency Modulation (FSK Family)
    elif med_dphase > 0.18 and sig_ap < 0.20:
        family = "FSK"
        if sig_af > 0.15:
            mod = "4FSK"
            order = 4
            conf = 0.91
            reason = f"Multi-tone frequency variation (sigma_af={sig_af:.3f}) matches 4FSK"
        else:
            mod = "2FSK"
            order = 2
            conf = 0.94
            reason = f"Constant envelope with discrete binary tone shifts (median_dphase={med_dphase:.3f}) matches 2FSK"

    # 3. Phase Shift Keying (PSK Family)
    else:
        family = "PSK"
        if c20_norm > 0.40 or c40_norm > 1.3:
            mod = "BPSK"
            order = 2
            conf = 0.96
            reason = f"Strong squared moment (C20_norm={c20_norm:.2f}, C40_norm={c40_norm:.2f}) matches BPSK"
        elif c42_norm < -0.50 or c40_norm > 0.40:
            mod = "QPSK"
            order = 4
            conf = 0.94
            reason = f"Zero C20 moment (C20_norm={c20_norm:.2f}) and C42_norm={c42_norm:.2f} match QPSK"
        else:
            mod = "8PSK"
            order = 8
            conf = 0.87
            reason = f"Constant envelope with 8-phase distribution (C42_norm={c42_norm:.2f})"

    all_mods = ["2FSK", "4FSK", "BPSK", "QPSK", "8PSK", "16QAM", "64QAM"]
    probs = {m: 0.02 for m in all_mods}
    probs[mod] = float(conf)
    remaining_prob = 1.0 - conf
    other_mods = [m for m in all_mods if m != mod]
    for m in other_mods:
        probs[m] = float(remaining_prob / len(other_mods))

    return {
        "modulation": mod,
        "family": family,
        "order": order,
        "confidence": conf,
        "probabilities": probs,
        "reason": reason,
        "features": feat
    }
