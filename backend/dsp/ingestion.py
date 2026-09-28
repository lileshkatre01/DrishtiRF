import os
import json
import re
import numpy as np
from scipy.signal import hilbert
import soundfile as sf
from typing import Tuple, Optional, Dict, Any

from backend.dsp.iqcapture import IQCapture

# Supported Raw IQ Format identifiers
FORMAT_DTYPE_MAP = {
    "cs8": np.int8,
    "cu8": np.uint8,
    "cs16": np.int16,
    "cf32": np.float32,
    "cs32": np.int32,
}

FORMAT_SCALE_MAP = {
    "cs8": 128.0,
    "cu8": 128.0,
    "cs16": 32768.0,
    "cf32": 1.0,
    "cs32": 2147483648.0,
}

def read_wav(file_path: str) -> Tuple[np.ndarray, float]:
    """
    Read WAV audio file.
    - Stereo WAV: Channel 0 = In-phase (I), Channel 1 = Quadrature (Q) -> I + 1j * Q.
    - Mono WAV: Real signal -> Analytic signal via Hilbert transform.
    """
    data, sample_rate = sf.read(file_path, dtype='float32')
    
    if data.ndim == 2 and data.shape[1] >= 2:
        # Stereo: I = Channel 0, Q = Channel 1
        i_data = data[:, 0]
        q_data = data[:, 1]
        complex_samples = (i_data + 1j * q_data).astype(np.complex64)
    else:
        # Mono: Generate analytic signal via Hilbert transform
        mono_data = data.flatten() if data.ndim == 2 else data
        analytic_signal = hilbert(mono_data)
        complex_samples = analytic_signal.astype(np.complex64)

    return complex_samples, float(sample_rate)

def read_raw_iq(file_path: str, fmt: str = "cs16", sample_rate: float = 1e6, center_freq: Optional[float] = None) -> IQCapture:
    """
    Read raw binary IQ file (cs8, cu8, cs16, cf32).
    De-interleaves In-phase and Quadrature samples. Truncates trailing odd bytes.
    """
    fmt_lower = fmt.lower()
    dtype = FORMAT_DTYPE_MAP.get(fmt_lower, np.int16)
    scale = FORMAT_SCALE_MAP.get(fmt_lower, 32768.0)

    # Read raw bytes
    raw_data = np.fromfile(file_path, dtype=dtype)
    
    # Truncate trailing odd byte/sample if interleaved I/Q count is odd
    if len(raw_data) % 2 != 0:
        raw_data = raw_data[:-1]

    if len(raw_data) == 0:
        return IQCapture(samples=np.array([], dtype=np.complex64), sample_rate=sample_rate, center_freq=center_freq, source_format=fmt)

    if fmt_lower == "cu8":
        # Unsigned 8-bit: shift zero to 128
        raw_data = raw_data.astype(np.float32) - 128.0

    i_samples = raw_data[0::2].astype(np.float32) / scale
    q_samples = raw_data[1::2].astype(np.float32) / scale

    complex_samples = (i_samples + 1j * q_samples).astype(np.complex64)

    return IQCapture(
        samples=complex_samples,
        sample_rate=sample_rate,
        center_freq=center_freq,
        source_format=fmt_lower,
        metadata={"raw_sample_count": len(complex_samples)}
    )

def read_sigmf(meta_path: str) -> IQCapture:
    """
    Read SigMF metadata sidecar (.sigmf-meta) and load corresponding data file (.sigmf-data).
    """
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    global_meta = meta.get("global", {})
    captures_meta = meta.get("captures", [{}])[0]

    sigmf_datatype = global_meta.get("core:datatype", "ci16_le")
    sample_rate = global_meta.get("core:sample_rate", 1000000.0)
    center_freq = captures_meta.get("core:frequency", None)

    # Map SigMF datatype to DrishtiRF format identifier
    datatype_map = {
        "ci8": "cs8",
        "cu8": "cu8",
        "ci16_le": "cs16",
        "ci16_be": "cs16",
        "cf32_le": "cf32",
        "cf32_be": "cf32",
        "ri32_le": "cs16"
    }
    fmt = datatype_map.get(sigmf_datatype, "cs16")

    # Locate binary data file (.sigmf-data)
    data_path = os.path.splitext(meta_path)[0] + ".sigmf-data"
    if not os.path.exists(data_path):
        data_path = os.path.splitext(meta_path)[0] + ".iq"

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"SigMF binary data file not found for {meta_path}")

    iq = read_raw_iq(data_path, fmt=fmt, sample_rate=sample_rate, center_freq=center_freq)
    iq.metadata["sigmf_datatype"] = sigmf_datatype
    iq.metadata["sigmf_global"] = global_meta
    return iq

def infer_format_and_params(
    file_path: str,
    format_override: Optional[str] = None,
    sample_rate_override: Optional[float] = None,
    center_freq_override: Optional[float] = None
) -> Tuple[str, float, Optional[float], float]:
    """
    Format Inference Engine:
    1. Check for SigMF metadata sidecar.
    2. Match Filename pattern conventions (_fs2000000_cf915000000_cs16.iq).
    3. User explicit override.
    4. Blind statistical fallback (flat kurtosis evaluation).
    
    Returns (inferred_format, sample_rate, center_freq, confidence_score)
    """
    confidence = 1.0

    # 1. SigMF check
    if file_path.endswith(".sigmf-meta"):
        with open(file_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        global_meta = meta.get("global", {})
        captures_meta = meta.get("captures", [{}])[0]
        fmt = global_meta.get("core:datatype", "cs16")
        sr = float(global_meta.get("core:sample_rate", 1e6))
        cf = captures_meta.get("core:frequency", None)
        return fmt, sr, cf, 1.0

    # Check for adjacent .sigmf-meta file
    meta_adjacent = os.path.splitext(file_path)[0] + ".sigmf-meta"
    if os.path.exists(meta_adjacent):
        return infer_format_and_params(meta_adjacent, format_override, sample_rate_override, center_freq_override)

    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    # Default values
    inferred_fmt = format_override or ("wav" if ext == ".wav" else "cs16")
    inferred_sr = sample_rate_override or 1000000.0
    inferred_cf = center_freq_override

    # 2. Filename Pattern Regex Check e.g., _fs2000000_cf915000000_cs16
    pattern = r"_fs(\d+(?:\.\d+)?)(?:_cf(\d+(?:\.\d+)?))?(?:_([a-z0-9]+))?"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        if match.group(1) and sample_rate_override is None:
            inferred_sr = float(match.group(1))
        if match.group(2) and center_freq_override is None:
            inferred_cf = float(match.group(2))
        if match.group(3) and format_override is None:
            fmt_cand = match.group(3).lower()
            if fmt_cand in FORMAT_DTYPE_MAP:
                inferred_fmt = fmt_cand

    # 3. WAV extension
    if ext == ".wav":
        return "wav", inferred_sr, inferred_cf, 1.0

    # 4. User Override
    if format_override or sample_rate_override:
        return inferred_fmt, inferred_sr, inferred_cf, 0.95

    # 5. Blind Statistical Fallback for raw IQ
    if ext in [".iq", ".raw", ".bin", ".dat"]:
        best_fmt = "cs16"
        min_kurtosis_diff = float("inf")

        for fmt in ["cs16", "cs8", "cf32"]:
            try:
                test_iq = read_raw_iq(file_path, fmt=fmt, sample_rate=inferred_sr)
                if test_iq.num_samples < 100:
                    continue
                # Kurtosis check: well-scaled complex signals have magnitude kurtosis near 1-3
                mags = np.abs(test_iq.samples[:10000])
                std_m = np.std(mags)
                if std_m > 0:
                    kurt = np.mean(((mags - np.mean(mags)) / std_m) ** 4)
                    diff = abs(kurt - 3.0)
                    if diff < min_kurtosis_diff:
                        min_kurtosis_diff = diff
                        best_fmt = fmt
            except Exception:
                pass
        
        inferred_fmt = best_fmt
        confidence = 0.65  # Flagged as inferred statistical fallback

    return inferred_fmt, inferred_sr, inferred_cf, confidence

def read_signal_file(
    file_path: str,
    sample_rate_override: Optional[float] = None,
    center_freq_override: Optional[float] = None,
    format_override: Optional[str] = None
) -> IQCapture:
    """
    Main Ingestion Gateway Function: Ingest any .iq, .wav, or .sigmf file into a canonical IQCapture.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Signal file not found: {file_path}")

    fmt, sr, cf, conf = infer_format_and_params(
        file_path,
        format_override=format_override,
        sample_rate_override=sample_rate_override,
        center_freq_override=center_freq_override
    )

    if fmt == "wav" or file_path.endswith(".wav"):
        complex_samples, wav_sr = read_wav(file_path)
        final_sr = sample_rate_override or wav_sr
        iq = IQCapture(
            samples=complex_samples,
            sample_rate=final_sr,
            center_freq=center_freq_override,
            source_format="wav",
            metadata={"inferred_confidence": conf, "wav_original_sr": wav_sr}
        )
    elif file_path.endswith(".sigmf-meta"):
        iq = read_sigmf(file_path)
    else:
        iq = read_raw_iq(file_path, fmt=fmt, sample_rate=sr, center_freq=cf)
        iq.metadata["inferred_confidence"] = conf

    return iq
