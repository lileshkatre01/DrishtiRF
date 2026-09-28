"""
DrishtiRF - 3-Tier Confidence & Explainability Engine
Evaluates overall signal processing confidence across Spectral, AMC, Demodulation, Joint FEC, and Correlation stages.
Assigns Tier A (Full Payload Recovery), Tier B (Demodulated Parameters), or Tier C (Spectral Fallback).
"""

from enum import Enum
from typing import Dict, Any, Optional

class ConfidenceTier(str, Enum):
    TIER_A = "Tier A: High-Confidence Payload Recovery"
    TIER_B = "Tier B: Demodulated Bitstream & Parameter Recovery"
    TIER_C = "Tier C: Spectral Parameters Only / Low SNR"

def evaluate_job_confidence(stage_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates 3-Tier confidence breakdown and rationale across all 5 job stages.
    
    stage_results expected keys: 'spectral', 'amc', 'demod', 'joint_search', 'correlation'
    """
    spectral = stage_results.get("spectral", {})
    amc = stage_results.get("amc", {})
    demod = stage_results.get("demod", {})
    joint = stage_results.get("joint_search", {})
    corr = stage_results.get("correlation", {})

    snr_db = float(spectral.get("snr_db", 0.0))
    amc_conf = float(amc.get("confidence", 0.0))
    demod_bit_count = int(demod.get("bit_count", 0))
    syndrome_zero = bool(joint.get("syndrome_zero", False))
    joint_conf = float(joint.get("confidence", 0.0))
    sync_found = bool(corr.get("sync_found", False))
    corr_conf = float(corr.get("confidence", 0.0))

    # Sub-scores (0.0 to 1.0)
    spectral_score = min(1.0, max(0.1, snr_db / 25.0))
    amc_score = amc_conf
    demod_score = 0.90 if demod_bit_count > 64 else (0.40 if demod_bit_count > 0 else 0.0)
    fec_score = joint_conf if syndrome_zero else joint_conf * 0.5
    corr_score = corr_conf if sync_found else corr_conf * 0.3

    # Weighted Overall Confidence
    overall_confidence = (
        0.15 * spectral_score +
        0.20 * amc_score +
        0.20 * demod_score +
        0.25 * fec_score +
        0.20 * corr_score
    )
    overall_confidence = round(min(0.99, max(0.05, overall_confidence)), 3)

    # 3-Tier Classification Decision Logic
    if (syndrome_zero or sync_found) and snr_db >= 5.0 and amc_conf >= 0.50:
        tier = ConfidenceTier.TIER_A
        rationale = (
            f"Assigned Tier A: Signal decoded with verified payload integrity. "
            f"Syndrome Zero: {syndrome_zero}, Sync Word Matched: '{corr.get('best_sync_word', 'None')}', "
            f"SNR: {snr_db:.2f} dB, AMC Confidence: {amc_conf*100:.1f}%."
        )
    elif amc_conf >= 0.40 or demod_bit_count > 0 or snr_db >= 3.0:
        tier = ConfidenceTier.TIER_B
        rationale = (
            f"Assigned Tier B: Signal parameters and raw demodulated bitstream extracted. "
            f"Modulation: {amc.get('modulation', 'Unknown')}, Bit Count: {demod_bit_count}, "
            f"SNR: {snr_db:.2f} dB. FEC decoding / framing sync not fully zero-syndrome."
        )
    else:
        tier = ConfidenceTier.TIER_C
        rationale = (
            f"Assigned Tier C: Low SNR ({snr_db:.2f} dB) or unclassifiable modulation. "
            f"Spectral parameters (PSD, Bandwidth, Carrier Offset) extracted with fallback parameters."
        )

    return {
        "tier": tier.value,
        "tier_code": tier.name,
        "overall_confidence": overall_confidence,
        "sub_scores": {
            "spectral": round(spectral_score, 3),
            "amc": round(amc_score, 3),
            "demod": round(demod_score, 3),
            "joint_fec": round(fec_score, 3),
            "correlation": round(corr_score, 3)
        },
        "rationale": rationale
    }
