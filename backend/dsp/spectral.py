import numpy as np
from scipy.signal import welch, stft
from typing import Tuple, Dict, Any, Optional

from backend.dsp.iqcapture import IQCapture

def compute_psd(iq: IQCapture, nperseg: int = 1024) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Compute Power Spectral Density (PSD) using Welch's method.
    Returns (freqs_centered_hz, psd_db, estimated_noise_floor_db).
    """
    if iq.num_samples < 64:
        freqs = np.linspace(-iq.sample_rate / 2, iq.sample_rate / 2, nperseg)
        psd_db = np.zeros(nperseg, dtype=np.float32)
        return freqs, psd_db, 0.0

    nper = min(nperseg, iq.num_samples)
    freqs, psd = welch(
        iq.samples,
        fs=iq.sample_rate,
        window='hann',
        nperseg=nper,
        return_onesided=False,
        scaling='density'
    )

    # Shift frequencies and PSD to center at 0 Hz (-fs/2 to +fs/2)
    freqs_centered = np.fft.fftshift(freqs)
    psd_centered = np.fft.fftshift(psd)

    # Convert to dB scale
    psd_db = 10.0 * np.log10(np.maximum(psd_centered, 1e-12))

    # Estimate noise floor (median of lower 30th percentile of PSD values)
    sorted_psd = np.sort(psd_db)
    noise_floor_db = float(np.median(sorted_psd[:max(1, len(sorted_psd) // 3)]))

    return freqs_centered.astype(np.float32), psd_db.astype(np.float32), noise_floor_db

def compute_waterfall(
    iq: IQCapture,
    nperseg: int = 512,
    max_time_bins: int = 150,
    max_freq_bins: int = 256
) -> Dict[str, Any]:
    """
    Compute Short-Time Fourier Transform (STFT) waterfall matrix.
    Decimates matrix dimensions so multi-megabyte grids are NOT sent over API/WebSockets.
    """
    if iq.num_samples < nperseg:
        return {
            "times": [0.0],
            "frequencies": [0.0],
            "grid": [[-100.0]]
        }

    nper = min(nperseg, iq.num_samples)
    noverlap = nper // 2

    freqs, times, Zxx = stft(
        iq.samples,
        fs=iq.sample_rate,
        window='hann',
        nperseg=nper,
        noverlap=noverlap,
        return_onesided=False
    )

    # Centered FFT shift along frequency axis
    freqs_centered = np.fft.fftshift(freqs)
    Zxx_centered = np.fft.fftshift(Zxx, axes=0)
    mag_db = 20.0 * np.log10(np.maximum(np.abs(Zxx_centered), 1e-6))

    # Decimate time bins if exceeding max_time_bins
    if mag_db.shape[1] > max_time_bins:
        time_step = int(np.ceil(mag_db.shape[1] / max_time_bins))
        mag_db = mag_db[:, ::time_step]
        times = times[::time_step]

    # Decimate frequency bins if exceeding max_freq_bins
    if mag_db.shape[0] > max_freq_bins:
        freq_step = int(np.ceil(mag_db.shape[0] / max_freq_bins))
        mag_db = mag_db[::freq_step, :]
        freqs_centered = freqs_centered[::freq_step]

    # Format for JSON serializable response (grid: list of lists [time_idx][freq_idx])
    grid = mag_db.T.tolist()  # Time x Freq format

    return {
        "times": times.astype(np.float32).tolist(),
        "frequencies": freqs_centered.astype(np.float32).tolist(),
        "grid": grid
    }

def estimate_bandwidth(freqs: np.ndarray, psd_db: np.ndarray, noise_floor_db: float) -> Dict[str, float]:
    """
    Estimate signal bandwidth using -3 dB, -10 dB, and 99% power containment methods.
    """
    if len(psd_db) == 0:
        return {"bw_3db": 0.0, "bw_10db": 0.0, "bw_99pct": 0.0}

    peak_power_db = np.max(psd_db)
    
    # Threshold -3 dB and -10 dB relative to spectral peak
    thresh_3db = peak_power_db - 3.0
    thresh_10db = peak_power_db - 10.0

    idx_3db = np.where(psd_db >= thresh_3db)[0]
    idx_10db = np.where(psd_db >= thresh_10db)[0]

    bw_3db = float(freqs[idx_3db[-1]] - freqs[idx_3db[0]]) if len(idx_3db) > 1 else 0.0
    bw_10db = float(freqs[idx_10db[-1]] - freqs[idx_10db[0]]) if len(idx_10db) > 1 else 0.0

    # 99% Power Containment Bandwidth
    psd_linear = 10.0 ** (psd_db / 10.0)
    total_power = np.sum(psd_linear)
    if total_power > 0:
        cum_power = np.cumsum(psd_linear) / total_power
        idx_lower = np.searchsorted(cum_power, 0.005)
        idx_upper = np.searchsorted(cum_power, 0.995)
        idx_upper = min(idx_upper, len(freqs) - 1)
        bw_99pct = float(freqs[idx_upper] - freqs[idx_lower])
    else:
        bw_99pct = bw_10db

    return {
        "bw_3db": abs(bw_3db),
        "bw_10db": abs(bw_10db),
        "bw_99pct": abs(bw_99pct)
    }

def estimate_center_frequency(iq: IQCapture, freqs: np.ndarray, psd_db: np.ndarray) -> Tuple[float, float]:
    """
    Estimate center frequency offset (Hz) and confidence.
    1. PSD Peak Detection.
    2. Nonlinearity 2nd power (BPSK) & 4th power (QPSK) spectral line recovery for suppressed carriers.
    """
    if len(psd_db) == 0:
        return 0.0, 0.0

    # Primary PSD Peak
    peak_idx = np.argmax(psd_db)
    cf_psd = float(freqs[peak_idx])

    # For suppressed carrier signals (e.g. BPSK/QPSK), evaluate x^2 and x^4 spectral lines
    cf_offset = cf_psd
    confidence = 0.85

    if iq.num_samples >= 1024:
        try:
            # 2nd power nonlinearity: x^2[n] -> peak at 2 * f_offset
            sq_samples = iq.samples ** 2
            f_sq, p_sq = welch(sq_samples, fs=iq.sample_rate, nperseg=1024, return_onesided=False)
            f_sq_centered = np.fft.fftshift(f_sq)
            p_sq_centered = np.fft.fftshift(p_sq)
            peak_sq_idx = np.argmax(p_sq_centered)
            line_freq = f_sq_centered[peak_sq_idx] / 2.0

            # If 2nd power spectral line is prominent, refine estimate
            sq_peak_ratio = p_sq_centered[peak_sq_idx] / (np.median(p_sq_centered) + 1e-12)
            if sq_peak_ratio > 10.0:
                cf_offset = float(line_freq)
                confidence = 0.95
        except Exception:
            pass

    return cf_offset, confidence

def estimate_snr(psd_db: np.ndarray, noise_floor_db: float, bw_hz: float, sample_rate: float) -> Tuple[float, float]:
    """
    Estimate Signal-to-Noise Ratio (SNR in dB).
    Calculates ratio of total in-band power vs estimated noise floor.
    """
    if len(psd_db) == 0:
        return 0.0, 0.0

    peak_power_db = float(np.max(psd_db))
    snr_db = float(peak_power_db - noise_floor_db)
    snr_db = max(0.0, snr_db)  # Clip negative SNR to 0 dB

    confidence = min(1.0, snr_db / 30.0) if snr_db > 0 else 0.2
    return snr_db, confidence

def get_rf_band_label(center_freq_hz: float) -> str:
    """
    Classify the estimated center frequency into standard RF band labels.
    HF: 3-30 MHz | VHF: 30-300 MHz | UHF: 300 MHz - 3 GHz | SHF: 3-30 GHz
    """
    if center_freq_hz is None or center_freq_hz <= 0:
        return "UNKNOWN"
    freq_mhz = abs(center_freq_hz) / 1e6
    if freq_mhz < 0.3:
        return "LF/MF (< 300 kHz)"
    elif freq_mhz < 3.0:
        return "MF (300 kHz – 3 MHz)"
    elif freq_mhz < 30.0:
        return "HF (3 – 30 MHz)"
    elif freq_mhz < 300.0:
        return "VHF (30 – 300 MHz)"
    elif freq_mhz < 3000.0:
        return "UHF (300 MHz – 3 GHz)"
    elif freq_mhz < 30000.0:
        return "SHF (3 – 30 GHz)"
    else:
        return "EHF (> 30 GHz)"


def analyze_spectrum(iq: IQCapture) -> Dict[str, Any]:
    """
    Master Spectral Analysis Engine: Compute PSD, decimated waterfall, BW, CF offset, SNR, noise floor.
    Returns complete JSON-serializable spectral dictionary including RF band label and symbol rate.
    """
    from backend.dsp.symbol_rate import estimate_symbol_rate

    freqs, psd_db, noise_floor_db = compute_psd(iq)
    waterfall = compute_waterfall(iq)
    bw_dict = estimate_bandwidth(freqs, psd_db, noise_floor_db)
    cf_offset, cf_conf = estimate_center_frequency(iq, freqs, psd_db)
    snr_db, snr_conf = estimate_snr(psd_db, noise_floor_db, bw_dict["bw_10db"], iq.sample_rate)

    # Estimated absolute center frequency
    estimated_cf_hz = (iq.center_freq or 0.0) + cf_offset

    # RF Band Classification
    band_label = get_rf_band_label(estimated_cf_hz if estimated_cf_hz != 0 else iq.sample_rate / 2)

    # Symbol Rate (directly from spectral stage so UI can show it immediately)
    symbol_rate_hz, symbol_rate_conf = estimate_symbol_rate(iq)

    return {
        "sample_rate": iq.sample_rate,
        "center_freq_declared": iq.center_freq,
        "center_freq_offset_hz": cf_offset,
        "center_freq_estimated_hz": estimated_cf_hz,
        "center_freq_confidence": cf_conf,
        "rf_band": band_label,
        "noise_floor_db": noise_floor_db,
        "snr_db": snr_db,
        "snr_confidence": snr_conf,
        "bandwidth_3db_hz": bw_dict["bw_3db"],
        "bandwidth_10db_hz": bw_dict["bw_10db"],
        "bandwidth_99pct_hz": bw_dict["bw_99pct"],
        "symbol_rate_baud": float(symbol_rate_hz),
        "symbol_rate_confidence": float(symbol_rate_conf),
        "frequencies": freqs.tolist(),
        "psd_db": psd_db.tolist(),
        "waterfall": waterfall
    }

