import numpy as np
from typing import Dict, Any

def compute_higher_order_cumulants(samples: np.ndarray) -> Dict[str, float]:
    """
    Compute higher-order cumulants (C20, C21, C40, C41, C42) and normalized cumulants (C40_norm, C42_norm).
    """
    if len(samples) == 0:
        return {
            "C20": 0.0, "C21": 0.0, "C40": 0.0, "C41": 0.0, "C42": 0.0,
            "C40_norm": 0.0, "C42_norm": 0.0
        }

    x = samples.astype(np.complex128)
    x_conj = np.conj(x)

    m20 = np.mean(x ** 2)
    m21 = np.mean(np.abs(x) ** 2)
    m40 = np.mean(x ** 4)
    m41 = np.mean((x ** 3) * x_conj)
    m42 = np.mean((np.abs(x) ** 2) * (x ** 2))
    m44 = np.mean(np.abs(x) ** 4)

    c20 = m20
    c21 = m21
    c40 = m40 - 3.0 * (c20 ** 2)
    c41 = m41 - 3.0 * c20 * c21
    c42 = m44 - np.abs(c20) ** 2 - 2.0 * (c21 ** 2)

    c21_sq = c21 ** 2 if c21 > 0 else 1.0
    c40_norm = complex(c40 / c21_sq)
    c42_norm = float(np.real(c42 / c21_sq))

    return {
        "C20": complex(c20),
        "C21": float(c21),
        "C40": complex(c40),
        "C41": complex(c41),
        "C42": float(np.real(c42)),
        "C40_norm": float(np.abs(c40_norm)),
        "C42_norm": c42_norm
    }

def compute_instantaneous_features(samples: np.ndarray) -> Dict[str, float]:
    """
    Compute instantaneous signal features:
    - sigma_ap: Instantaneous amplitude variance
    - sigma_dp: Instantaneous direct phase variance
    - sigma_af: Instantaneous frequency variance
    - median_diff_phase: Median phase derivative (key discriminator for FSK)
    - papr_db: Peak-to-Average Power Ratio
    """
    if len(samples) == 0:
        return {"sigma_ap": 0.0, "sigma_dp": 0.0, "sigma_af": 0.0, "median_diff_phase": 0.0, "papr_db": 0.0}

    amp = np.abs(samples)
    mean_amp = np.mean(amp) + 1e-12
    norm_amp = amp / mean_amp

    # Apply moving average AGC to filter out slow multipath channel fading
    window_len = min(64, max(8, len(samples) // 50))
    if window_len > 1:
        fading_envelope = np.convolve(norm_amp, np.ones(window_len)/window_len, mode='same')
        eq_norm_amp = norm_amp / (fading_envelope + 1e-6)
        sigma_ap = float(np.std(eq_norm_amp))
    else:
        sigma_ap = float(np.std(norm_amp))

    phase = np.angle(samples)
    unwrapped_phase = np.unwrap(phase)
    sigma_dp = float(np.std(phase))

    inst_freq = np.diff(unwrapped_phase)
    sigma_af = float(np.std(inst_freq / (2 * np.pi))) if len(inst_freq) > 0 else 0.0
    median_diff_phase = float(np.median(np.abs(inst_freq))) if len(inst_freq) > 0 else 0.0

    p_peak = np.max(amp ** 2)
    p_mean = np.mean(amp ** 2) + 1e-12
    papr_db = float(10.0 * np.log10(p_peak / p_mean))

    return {
        "sigma_ap": sigma_ap,
        "sigma_dp": sigma_dp,
        "sigma_af": sigma_af,
        "median_diff_phase": median_diff_phase,
        "papr_db": papr_db
    }

def extract_amc_features(samples: np.ndarray) -> Dict[str, float]:
    cumulants = compute_higher_order_cumulants(samples)
    inst = compute_instantaneous_features(samples)

    features = {
        "C40_norm": cumulants["C40_norm"],
        "C42_norm": cumulants["C42_norm"],
        "sigma_ap": inst["sigma_ap"],
        "sigma_dp": inst["sigma_dp"],
        "sigma_af": inst["sigma_af"],
        "median_diff_phase": inst["median_diff_phase"],
        "papr_db": inst["papr_db"]
    }
    return features
