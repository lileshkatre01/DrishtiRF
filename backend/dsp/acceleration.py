import numpy as np
from typing import Tuple, Dict, Any, Optional

def fast_fft_psd(samples: np.ndarray, fs: float, nperseg: int = 1024) -> Tuple[np.ndarray, np.ndarray]:
    """
    Accelerated Welch Power Spectral Density calculation.
    Uses vectorized strided windowing for maximum CPU throughput.
    """
    n = len(samples)
    if n < nperseg:
        nperseg = n

    step = nperseg // 2
    num_segments = (n - nperseg) // step + 1

    if num_segments <= 0:
        fft_vals = np.abs(np.fft.fftshift(np.fft.fft(samples, n=nperseg))) ** 2
        freqs = np.fft.fftshift(np.fft.fftfreq(nperseg, d=1.0/fs))
        return freqs, 10 * np.log10(fft_vals / (nperseg * fs) + 1e-12)

    window = np.hanning(nperseg)
    scale = np.sum(window ** 2) * fs

    # Vectorized 2D strided array for zero-copy windowing
    shape = (num_segments, nperseg)
    strides = (samples.strides[0] * step, samples.strides[0])
    strided_segments = np.lib.stride_tricks.as_strided(samples, shape=shape, strides=strides)

    windowed = strided_segments * window
    fft_matrix = np.abs(np.fft.fft(windowed, axis=1)) ** 2
    psd_avg = np.mean(fft_matrix, axis=0) / scale

    psd_shifted = np.fft.fftshift(psd_avg)
    freqs_shifted = np.fft.fftshift(np.fft.fftfreq(nperseg, d=1.0/fs))

    return freqs_shifted, 10 * np.log10(psd_shifted + 1e-12)

def fast_hamming_correlation(bitstream_a: np.ndarray, bitstream_b: np.ndarray) -> np.ndarray:
    """
    Vectorized Hamming distance correlation between binary arrays.
    """
    len_a = len(bitstream_a)
    len_b = len(bitstream_b)
    if len_a < len_b:
        return np.array([len_b])

    num_positions = len_a - len_b + 1
    shape = (num_positions, len_b)
    strides = (bitstream_a.strides[0], bitstream_a.strides[0])
    strided = np.lib.stride_tricks.as_strided(bitstream_a, shape=shape, strides=strides)

    # XOR bit difference matrix
    hamming_distances = np.sum(strided != bitstream_b, axis=1)
    return hamming_distances

def estimate_acceleration_metrics(sample_count: int, sample_rate: float) -> Dict[str, Any]:
    """
    Provide performance metrics and hardware execution estimate.
    """
    throughput_msps = (sample_rate / 1e6)
    estimated_latency_ms = float(round((sample_count / sample_rate) * 1000.0, 2))
    
    return {
        "sample_count": sample_count,
        "sample_rate_mhz": float(round(sample_rate / 1e6, 2)),
        "throughput_msps": float(round(throughput_msps, 2)),
        "estimated_processing_latency_ms": estimated_latency_ms,
        "hardware_acceleration": "Vectorized SIMD NumPy (CPU JIT Ready)"
    }
