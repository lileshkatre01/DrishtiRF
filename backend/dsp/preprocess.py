import numpy as np
from backend.dsp.iqcapture import IQCapture

def remove_dc_offset(iq: IQCapture) -> IQCapture:
    """
    Remove DC offset independently from In-phase (I) and Quadrature (Q) components.
    """
    if iq.num_samples == 0:
        return iq
    
    i_real = np.real(iq.samples) - np.mean(np.real(iq.samples))
    q_imag = np.imag(iq.samples) - np.mean(np.imag(iq.samples))
    clean_samples = (i_real + 1j * q_imag).astype(np.complex64)
    
    return IQCapture(
        samples=clean_samples,
        sample_rate=iq.sample_rate,
        center_freq=iq.center_freq,
        source_format=iq.source_format,
        metadata=iq.metadata.copy()
    )

def normalize_power(iq: IQCapture, target_power: float = 1.0) -> IQCapture:
    """
    Normalize signal amplitude so mean power E[|x|^2] equals target_power (default 1.0).
    """
    current_power = iq.mean_power
    if current_power <= 0.0 or np.isnan(current_power):
        return iq
    
    scale_factor = np.sqrt(target_power / current_power)
    normalized_samples = (iq.samples * scale_factor).astype(np.complex64)
    
    return IQCapture(
        samples=normalized_samples,
        sample_rate=iq.sample_rate,
        center_freq=iq.center_freq,
        source_format=iq.source_format,
        metadata=iq.metadata.copy()
    )

def correct_iq_imbalance(iq: IQCapture) -> IQCapture:
    """
    Correct IQ amplitude and phase imbalance using Gram-Schmidt orthogonalization.
    Guards against 1D signals (BPSK, AM) where Q energy is predominantly noise.
    """
    if iq.num_samples < 64:
        return iq

    i_data = np.real(iq.samples)
    q_data = np.imag(iq.samples)

    p_i = float(np.mean(i_data ** 2))
    p_q = float(np.mean(q_data ** 2))
    
    # If one channel is negligible (< 5% of other), signal is 1D (e.g. BPSK or real audio), skip imbalance correction
    if p_i <= 1e-9 or p_q <= 1e-9 or (p_q < 0.05 * p_i) or (p_i < 0.05 * p_q):
        return iq

    ratio = p_i / (p_q + 1e-12)
    # Only correct if moderate imbalance exists (ratio between 0.33 and 3.0)
    if ratio < 0.33 or ratio > 3.0:
        return iq

    amp_scale = np.sqrt(ratio)
    q_scaled = q_data * amp_scale

    # Estimate phase imbalance
    sin_phi = float(np.mean(i_data * q_scaled) / (p_i + 1e-12))
    if np.abs(sin_phi) >= 0.70:
        return iq

    cos_phi = np.sqrt(max(1e-6, 1.0 - sin_phi ** 2))
    q_corrected = (q_scaled - i_data * sin_phi) / cos_phi

    corrected_samples = (i_data + 1j * q_corrected).astype(np.complex64)

    return IQCapture(
        samples=corrected_samples,
        sample_rate=iq.sample_rate,
        center_freq=iq.center_freq,
        source_format=iq.source_format,
        metadata=iq.metadata.copy()
    )

def estimate_and_correct_cfo(iq: IQCapture) -> IQCapture:
    """
    Estimate Carrier Frequency Offset (CFO) / Doppler shift using 4th-power spectral peak and derotate.
    """
    if iq.num_samples < 64:
        return iq
        
    samples = iq.samples
    fs = iq.sample_rate

    # 4th-power non-linear spectrum for M-PSK/QAM carrier recovery
    x4 = samples ** 4
    fft_vals = np.fft.fftshift(np.fft.fft(x4))
    freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), d=1.0/fs))

    peak_idx = np.argmax(np.abs(fft_vals))
    cfo_est = freqs[peak_idx] / 4.0

    # Derotate samples
    t = np.arange(len(samples)) / fs
    derotated = samples * np.exp(-1j * 2 * np.pi * cfo_est * t)

    meta = iq.metadata.copy()
    meta["estimated_cfo_hz"] = float(cfo_est)

    return IQCapture(
        samples=derotated.astype(np.complex64),
        sample_rate=iq.sample_rate,
        center_freq=iq.center_freq,
        source_format=iq.source_format,
        metadata=meta
    )

def preprocess_signal(
    iq: IQCapture,
    remove_dc: bool = True,
    correct_imbalance: bool = True,
    correct_cfo: bool = False,
    normalize: bool = True
) -> IQCapture:
    """
    Full preprocessing pipeline: CFO derotation -> DC offset removal -> IQ imbalance correction -> Power normalization.
    """
    result = iq
    if correct_cfo:
        result = estimate_and_correct_cfo(result)
    if remove_dc:
        result = remove_dc_offset(result)
    if correct_imbalance:
        result = correct_iq_imbalance(result)
    if normalize:
        result = normalize_power(result)
    return result
