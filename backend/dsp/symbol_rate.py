import numpy as np
from scipy.signal import welch, correlate
from typing import Tuple, Dict, Any, Optional

from backend.dsp.iqcapture import IQCapture

def estimate_symbol_rate(iq: IQCapture) -> Tuple[float, float]:
    """
    Symbol Rate Consensus Engine:
    Computes derivative transition energy and cyclostationary envelope variation to detect
    fundamental symbol boundary intervals for digital modulations (PSK, QAM, FSK, MSK, ASK).
    """
    if iq.num_samples < 256:
        return 0.0, 0.0

    # Use up to 16384 samples for high statistical precision
    n_pts = min(16384, iq.num_samples)
    samples = iq.samples[:n_pts]

    # 1. Derivative transition energy d[n] = |x[n] - x[n-1]|^2
    diff_energy = np.abs(samples[1:] - samples[:-1]) ** 2
    diff_energy -= np.mean(diff_energy)

    if len(diff_energy) < 256:
        return 0.0, 0.0

    autocorr = correlate(diff_energy, diff_energy, mode='full')
    autocorr = autocorr[len(autocorr)//2:]

    min_lag = 2
    # Search up to lag 2048 to support symbol rates down to ~500 Baud at 1 MHz Fs
    max_lag = min(2048, len(autocorr) - 1)

    if max_lag <= min_lag:
        return 0.0, 0.0

    lag_region = autocorr[min_lag:max_lag]
    max_peak_val = np.max(lag_region) if len(lag_region) > 0 else 0.0
    if max_peak_val <= 0:
        return 0.0, 0.0

    # Find first prominent local peak above 30% of max peak to isolate fundamental symbol interval
    thresh = 0.30 * max_peak_val
    best_lag = int(min_lag + np.argmax(lag_region))  # Fallback to max peak

    for idx in range(1, len(lag_region) - 1):
        if (lag_region[idx] >= thresh and
            lag_region[idx] >= lag_region[idx - 1] and
            lag_region[idx] >= lag_region[idx + 1]):
            best_lag = int(min_lag + idx)
            break

    if best_lag > 0 and autocorr[0] > 0:
        est_rate = float(iq.sample_rate / best_lag)
        peak_ratio = float(autocorr[best_lag] / (autocorr[0] + 1e-12))
        confidence = float(min(0.99, max(0.45, peak_ratio * 3.0)))
        return round(est_rate, 1), round(confidence, 3)

    return 0.0, 0.0
