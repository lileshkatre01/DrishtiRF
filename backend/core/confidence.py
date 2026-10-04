"""
DrishtiRF - 3-Tier Defense-Grade Confidence & Evidence Accounting Engine
Evaluates overall signal processing confidence across Spectral, AMC, Demodulation, Joint FEC, and Correlation stages.
Assigns Tier A (Verified Payload Recovery), Tier B (Demodulated Parameters), or Tier C (Spectral Fallback / UNKNOWN).
Enforces zero-hallucination / zero-overclaiming rules.
"""

from enum import Enum
from typing import Dict, Any, List

class ConfidenceTier(str, Enum):
    TIER_A = "Tier A: High-Confidence Payload Recovery (Verified)"
    TIER_B = "Tier B: Demodulated Bitstream & Parameter Recovery (Plausible)"
    TIER_C = "Tier C: Spectral Parameters Only / Low SNR / Hypothesis"

def evaluate_job_confidence(stage_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates 3-Tier confidence breakdown, evidence levels, limits, and engineering rationale.
    
    stage_results expected keys: 'spectral', 'amc', 'demod', 'joint_search', 'correlation'
    """
    spectral = stage_results.get("spectral", {})
    amc = stage_results.get("amc", {})
    demod = stage_results.get("demod", {})
    joint = stage_results.get("joint_search", {})
    corr = stage_results.get("correlation", {})

    snr_db = float(spectral.get("snr_db", 0.0))
    amc_conf = float(amc.get("confidence", 0.0))
    mod_name = str(amc.get("modulation", "Unknown"))
    is_analog = bool(amc.get("is_analog", False) or mod_name.upper() in ["AM", "FM", "SSB", "ANALOG_AUDIO"])
    
    demod_bit_count = int(demod.get("bit_count", 0))
    syndrome_zero = bool(joint.get("syndrome_zero", False))
    joint_conf = float(joint.get("confidence", 0.0))
    fec_status = str(joint.get("fec_status", "VERIFIED" if syndrome_zero else "PARTIAL"))
    
    sync_found = bool(corr.get("sync_found", False))
    corr_conf = float(corr.get("confidence", 0.0))
    sync_is_periodic = bool(corr.get("is_periodic", False))
    sync_name = str(corr.get("best_sync_word", "None"))
    crc_passed = bool(corr.get("crc_passed", False))

    # Sub-scores (0.0 to 1.0)
    spectral_score = min(1.0, max(0.1, snr_db / 25.0))
    amc_score = amc_conf
    demod_score = 0.90 if demod_bit_count > 64 else (0.40 if demod_bit_count > 0 else 0.0)
    fec_score = joint_conf if syndrome_zero else joint_conf * 0.45
    corr_score = corr_conf if sync_found else corr_conf * 0.25

    # 1. ANALOG SIGNAL HANDLING
    if is_analog:
        overall_confidence = round(0.40 * spectral_score + 0.60 * amc_score, 3)
        tier = ConfidenceTier.TIER_B
        tier_code = "TIER_B"
        rationale = (
            f"Assigned Tier B (Analog Audio/Carrier): Detected analog modulation ({mod_name}) "
            f"with AMC confidence {amc_conf*100:.1f}% and SNR {snr_db:.1f} dB. "
            f"Digital FEC de-interleaving and framing stages were appropriately bypassed."
        )
    else:
        # Weighted Overall Confidence for Digital
        overall_confidence = (
            0.15 * spectral_score +
            0.20 * amc_score +
            0.20 * demod_score +
            0.25 * fec_score +
            0.20 * corr_score
        )
        overall_confidence = round(min(0.99, max(0.05, overall_confidence)), 3)

        # STRICT Tier A Rules (Mathematical or Multi-Period Proof Required):
        # Tier A ONLY if:
        # - High SNR (>= 5.0 dB)
        # - High AMC confidence (>= 0.65)
        # - Decoded bits exist (>= 64 bits)
        # - AND (Syndrome Zero is True OR CRC Passed is True OR (Sync is Periodic + High Correlation + High FEC Score))
        # AND FEC status is NOT PARTIAL without proof.
        has_mathematical_proof = syndrome_zero or crc_passed or (sync_found and sync_is_periodic and corr_conf >= 0.85 and joint_conf >= 0.70)
        
        if has_mathematical_proof and snr_db >= 5.0 and amc_conf >= 0.65 and demod_bit_count >= 64:
            tier = ConfidenceTier.TIER_A
            tier_code = "TIER_A"
            proof_desc = "Syndrome Zero = True" if syndrome_zero else ("CRC Check Passed" if crc_passed else f"Periodic Sync Pattern '{sync_name}'")
            rationale = (
                f"Assigned Tier A (Verified): Full payload recovery verified via {proof_desc}. "
                f"Modulation: {mod_name} ({amc_conf*100:.1f}%), SNR: {snr_db:.1f} dB, Decoded Bits: {demod_bit_count}."
            )
        elif (amc_conf >= 0.35 or demod_bit_count > 0) and snr_db >= 2.5:
            tier = ConfidenceTier.TIER_B
            tier_code = "TIER_B"
            fec_note = "FEC Parity Partial / Unconverged" if not syndrome_zero else "Unverified Sync Alignment"
            rationale = (
                f"Assigned Tier B (Plausible Hypothesis): Signal parameters & bitstream extracted, but {fec_note}. "
                f"Modulation: {mod_name}, SNR: {snr_db:.1f} dB, Bit Count: {demod_bit_count}. Human review recommended."
            )
        else:
            tier = ConfidenceTier.TIER_C
            tier_code = "TIER_C"
            rationale = (
                f"Assigned Tier C (Low SNR / Hypothesis): In-band SNR ({snr_db:.1f} dB) or modulation confidence ({amc_conf*100:.1f}%) "
                f"is insufficient for reliable digital demodulation. Fallback spectral parameters provided."
            )

    # Granular Evidence Levels
    if is_analog:
        evidence_levels = {
            "spectral": {
                "level": "MEASURED",
                "method": "Welch Periodogram + Band Integration",
                "basis": f"SNR: {snr_db:.1f} dB, Noise Floor: {spectral.get('noise_floor_db', -90):.1f} dB"
            },
            "amc": {
                "level": "ESTIMATED",
                "method": "Instantaneous Envelope Variance + Spectral Carrier",
                "basis": f"{mod_name} Audio Carrier ({amc_conf*100:.1f}% confidence)"
            },
            "demod": {
                "level": "N/A",
                "method": f"Analog Baseband Demodulation ({mod_name})",
                "basis": "Continuous analog audio waveform (no discrete bits)"
            },
            "joint_fec": {
                "level": "N/A",
                "method": "Bypassed for Analog Signals",
                "basis": "FEC parity not applicable on continuous analog audio"
            },
            "framing": {
                "level": "N/A",
                "method": "Bypassed for Analog Signals",
                "basis": "Packet framing not applicable on analog audio streams"
            }
        }
    else:
        evidence_levels = {
            "spectral": {
                "level": "MEASURED",
                "method": "Welch Periodogram + Band Integration",
                "basis": f"SNR: {snr_db:.1f} dB, Noise Floor: {spectral.get('noise_floor_db', -90):.1f} dB"
            },
            "amc": {
                "level": "ESTIMATED" if amc_conf >= 0.75 else ("HYPOTHESIS" if amc_conf >= 0.35 else "UNKNOWN"),
                "method": "Higher-Order Cumulants (C20, C42) + Feature Classifier",
                "basis": f"{mod_name} ({amc_conf*100:.1f}% confidence)"
            },
            "demod": {
                "level": "DEMODULATED" if demod_bit_count > 0 else "UNKNOWN",
                "method": f"Matched Filter + Slicer ({mod_name})",
                "basis": f"{demod_bit_count} bits recovered" if demod_bit_count > 0 else "No bitstream recovered"
            },
            "joint_fec": {
                "level": "VERIFIED" if syndrome_zero else ("HYPOTHESIS" if joint_conf >= 0.40 else "UNKNOWN"),
                "method": "Syndrome Parity Check / Viterbi Path Metric",
                "basis": f"FEC: {joint.get('best_fec', 'None')}, Interleaver: {joint.get('best_interleaver', 'None')} (Syndrome Zero: {syndrome_zero})"
            },
            "framing": {
                "level": "VERIFIED" if (sync_found and (sync_is_periodic or corr_conf >= 0.85)) else ("HYPOTHESIS" if sync_found else "UNKNOWN"),
                "method": "Cross-Correlation & Periodicity Search",
                "basis": f"Sync: '{sync_name}', Frames: {corr.get('frame_count', 0)}" if sync_found else "No standard sync word detected"
            }
        }

    # Defense-Grade Stated Limits
    limits = [
        "Non-catalog LDPC matrices or non-standard proprietary interleavers fall back to hypothesis ranking.",
        "Blind symbol rate estimation assumes >= 4 samples per symbol and SNR > 2.5 dB.",
        "Unsynchronized raw bitstreams without CRC or periodic sync words are labeled CANDIDATE frames.",
        "Analog transmissions (AM/FM/SSB) bypass digital FEC/Interleaver stages to prevent false decoding."
    ]

    needs_review = (tier_code != "TIER_A") or any(
        ev["level"] in ["HYPOTHESIS", "UNKNOWN"] for ev in evidence_levels.values()
    )

    return {
        "tier": tier.value,
        "tier_code": tier_code,
        "overall_confidence": overall_confidence,
        "sub_scores": {
            "spectral": round(spectral_score, 3),
            "amc": round(amc_score, 3),
            "demod": round(demod_score, 3),
            "joint_fec": round(fec_score, 3),
            "correlation": round(corr_score, 3)
        },
        "evidence_levels": evidence_levels,
        "limits": limits,
        "needs_review": needs_review,
        "rationale": rationale
    }
