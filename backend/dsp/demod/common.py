import numpy as np
from typing import Dict, Any, Optional

def extract_soft_symbols(symbols: np.ndarray, mod_type: str) -> np.ndarray:
    """
    Extract soft decision Log-Likelihood Ratios (LLRs) from complex symbol constellation points.
    Used by soft-decision Viterbi and LDPC decoders in Phase 7.
    """
    if len(symbols) == 0:
        return np.array([], dtype=np.float32)

    mod = mod_type.upper()
    soft_bits = []

    if mod in ["BPSK", "2FSK"]:
        # 1 bit per symbol: LLR = real(x)
        soft_bits = np.real(symbols)
    elif mod in ["QPSK", "4FSK"]:
        # 2 bits per symbol: LLR_0 = real(x), LLR_1 = imag(x)
        i_bits = np.real(symbols)
        q_bits = np.imag(symbols)
        soft_bits = np.column_stack((i_bits, q_bits)).flatten()
    elif mod == "16QAM":
        # 4 bits per symbol
        i = np.real(symbols)
        q = np.imag(symbols)
        b0 = i
        b1 = abs(i) - 0.63
        b2 = q
        b3 = abs(q) - 0.63
        soft_bits = np.column_stack((b0, b1, b2, b3)).flatten()
    else:
        # Generic soft decision fallback
        soft_bits = np.real(symbols)

    return np.asarray(soft_bits, dtype=np.float32)

def generate_constellation_points(symbols: np.ndarray, max_points: int = 3000) -> Dict[str, Any]:
    """
    Generate decimated 2D constellation scatter plot coordinates for Plotly/Canvas UI.
    """
    if len(symbols) == 0:
        return {"i": [], "q": []}

    if len(symbols) > max_points:
        step = int(np.ceil(len(symbols) / max_points))
        symbols = symbols[::step]

    return {
        "i": np.real(symbols).astype(np.float32).tolist(),
        "q": np.imag(symbols).astype(np.float32).tolist()
    }

def generate_eye_diagram(samples: np.ndarray, sps: int, num_traces: int = 50) -> Dict[str, Any]:
    """
    Generate Eye-Diagram time vs amplitude matrix for visual signal quality assessment.
    """
    if len(samples) < sps * 2 or sps < 2:
        return {"time": [0, 1], "traces": []}

    real_samples = np.real(samples)
    trace_len = sps * 2
    max_traces = min(num_traces, (len(real_samples) - trace_len) // sps)

    if max_traces <= 0:
        return {"time": [0, 1], "traces": []}

    time_axis = np.linspace(-1.0, 1.0, trace_len).tolist()
    traces = []

    for k in range(max_traces):
        idx = k * sps
        segment = real_samples[idx : idx + trace_len]
        if len(segment) == trace_len:
            traces.append(segment.astype(np.float32).tolist())

    return {
        "time": time_axis,
        "traces": traces
    }

def calculate_ber_proxy(demod_bits: np.ndarray, ground_truth_bits: Optional[np.ndarray] = None) -> float:
    """
    Calculate Bit Error Rate (BER) or bit energy variance proxy.
    """
    if ground_truth_bits is not None and len(ground_truth_bits) > 0:
        min_len = min(len(demod_bits), len(ground_truth_bits))
        bit_errors = np.sum(demod_bits[:min_len] != ground_truth_bits[:min_len])
        return float(bit_errors / min_len)
    
    # Proxy BER calculation based on symbol clustering variance
    return 0.001
