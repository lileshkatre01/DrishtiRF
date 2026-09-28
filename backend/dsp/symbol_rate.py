import numpy as np
from scipy.signal import welch, correlate
from typing import Tuple, Dict, Any, Optional

from backend.dsp.iqcapture import IQCapture

def estimate_symbol_rate(iq: IQCapture) -> Tuple[float, float]:
    """
    Symbol Rate Consensus Engine:
    Computes derivative transition energy d[n] = |x[n] - x[n-1]|^2 to detect fundamental
    symbol boundary interval for phase/frequency/amplitude modulated signals.
    """
    if iq.num_samples < 256:
        return 0.0, 0.0

    samples = iq.samples
    diff_energy = np.abs(samples[1:] - samples[:-1]) ** 2
    diff_energy -= np.mean(diff_energy)

    if len(diff_energy) < 256:
        return 0.0, 0.0

    autocorr = correlate(diff_energy[:4096], diff_energy[:4096], mode='full')
    autocorr = autocorr[len(autocorr)//2:]

    min_lag = 2
    max_lag = min(150, len(autocorr) - 1)

    if max_lag <= min_lag:
        return 0.0, 0.0

    lag_region = autocorr[min_lag:max_lag]
    max_peak_val = np.max(lag_region)
    if max_peak_val <= 0:
        return 0.0, 0.0

    # Find FIRST prominent local peak above 35% of max peak to isolate fundamental symbol interval
    thresh = 0.35 * max_peak_val
    best_lag = int(min_lag + np.argmax(lag_region))  # Fallback to max peak

    for idx in range(1, len(lag_region) - 1):
        if (lag_region[idx] >= thresh and
            lag_region[idx] >= lag_region[idx - 1] and
            lag_region[idx] >= lag_region[idx + 1]):
            best_lag = int(min_lag + idx)
            break

    if best_lag > 0 and autocorr[0] > 0:
        est_rate = float(iq.sample_rate / best_lag)
        confidence = float(min(1.0, max(0.40, autocorr[best_lag] / (autocorr[0] + 1e-12))))
        return est_rate, confidence

    return 0.0, 0.0
