from typing import Dict, Any

def generate_explanation(stage: str, details: Dict[str, Any]) -> str:
    """
    Generate analyst-grade human readable explanation for each processing stage decision.
    """
    if stage == "spectral":
        bw = details.get("bandwidth_hz", 0)
        snr = details.get("snr_db", 0)
        cf = details.get("center_freq_hz", 0)
        return f"Spectral Analysis complete. Estimated Bandwidth: {bw/1e3:.2f} kHz, SNR: {snr:.2f} dB, Carrier Offset: {cf:.2f} Hz."
    
    elif stage == "amc":
        mod = details.get("modulation", "Unknown")
        conf = details.get("confidence", 0.0)
        reason = details.get("reason", "")
        return f"Modulation classified as {mod} with {conf*100:.1f}% confidence. Decision rationale: {reason}"
    
    elif stage == "joint_search":
        interleaver = details.get("interleaver", "None")
        fec = details.get("fec", "None")
        success = details.get("success", False)
        if success:
            return f"Joint Search succeeded. Discovered Interleaver: {interleaver}, FEC Scheme: {fec} with zero residual syndrome errors."
        else:
            return f"Joint Search finished without full decode convergence. Best hypothesis: Interleaver={interleaver}, FEC={fec}."
            
    elif stage == "correlation":
        sync = details.get("sync_word", "None")
        count = details.get("frame_count", 0)
        return f"Bitstream correlation matched sync word '{sync}' across {count} extracted frames."
        
    return f"Stage {stage} completed."
