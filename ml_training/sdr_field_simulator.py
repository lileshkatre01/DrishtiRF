import numpy as np
from typing import Dict, Any, Tuple
import os
import json

from backend.dsp.iqcapture import IQCapture
from ml_training.synth_generator import generate_synthetic_iq, SUPPORTED_MODULATIONS

def apply_rician_fading(samples: np.ndarray, K_db: float = 6.0, num_taps: int = 4) -> np.ndarray:
    """
    Apply Rician multipath fading channel model.
    K_db: Rician K-factor in dB (ratio of specular power to diffuse power).
    """
    K = 10 ** (K_db / 10.0)
    specular = np.sqrt(K / (K + 1))
    diffuse_std = np.sqrt(1 / (2 * (K + 1)))
    
    # Generate multipath channel impulse response
    taps = (np.random.normal(0, diffuse_std, size=num_taps) + 
            1j * np.random.normal(0, diffuse_std, size=num_taps))
    taps[0] += specular
    
    # Normalize channel energy
    taps = taps / np.sqrt(np.sum(np.abs(taps) ** 2))
    
    # Convolve signal with channel impulse response
    faded = np.convolve(samples, taps, mode='same')
    return faded

def apply_iq_imbalance(samples: np.ndarray, amplitude_imbalance_db: float = 0.5, phase_imbalance_deg: float = 3.0) -> np.ndarray:
    """
    Apply I/Q mismatch (amplitude imbalance g and phase imbalance phi).
    """
    g = 10 ** (amplitude_imbalance_db / 20.0)
    phi = np.radians(phase_imbalance_deg)
    
    i = np.real(samples)
    q = np.imag(samples)
    
    i_out = g * i
    q_out = np.sin(phi) * i + np.cos(phi) * q
    
    return i_out + 1j * q_out

def apply_phase_noise(samples: np.ndarray, sample_rate: float, noise_std: float = 0.05) -> np.ndarray:
    """
    Apply oscillator phase noise (random walk phase noise).
    """
    d_phase = np.random.normal(0, noise_std, size=len(samples))
    phase_noise = np.cumsum(d_phase)
    return samples * np.exp(1j * phase_noise)

def apply_doppler_shift(samples: np.ndarray, sample_rate: float, max_doppler_hz: float = 500.0) -> np.ndarray:
    """
    Apply Doppler frequency drift over time.
    """
    t = np.arange(len(samples)) / sample_rate
    # Linear or sinusoidal Doppler drift profile
    doppler_freq = max_doppler_hz * np.sin(2 * np.pi * 0.5 * t)
    phase = 2 * np.pi * np.cumsum(doppler_freq) / sample_rate
    return samples * np.exp(1j * phase)

def apply_adc_quantization(samples: np.ndarray, num_bits: int = 8) -> np.ndarray:
    """
    Simulate ADC finite bit depth quantization (e.g. 8-bit for RTL-SDR).
    """
    levels = 2 ** num_bits
    max_val = np.max(np.abs(samples))
    if max_val == 0:
        return samples
    
    norm_samples = samples / max_val
    quant_i = np.round(np.real(norm_samples) * (levels / 2)) / (levels / 2)
    quant_q = np.round(np.imag(norm_samples) * (levels / 2)) / (levels / 2)
    
    return (quant_i + 1j * quant_q) * max_val

def generate_sdr_field_iq(
    mod_type: str = "QPSK",
    snr_db: float = 5.0,
    k_factor_db: float = 4.0,
    iq_imbalance_db: float = 0.5,
    doppler_hz: float = 300.0,
    adc_bits: int = 8,
    sample_rate: float = 1e6,
    symbol_rate: float = 100e3
) -> IQCapture:
    """
    Generate realistic off-air SDR field signal with combined real-world channel impairments.
    """
    # 1. Base synthetic IQ generation
    base_iq = generate_synthetic_iq(
        mod_type=mod_type,
        num_symbols=3000,
        sample_rate=sample_rate,
        symbol_rate=symbol_rate,
        snr_db=snr_db
    )
    samples = base_iq.samples
    
    # 2. Rician Multipath Fading
    samples = apply_rician_fading(samples, K_db=k_factor_db)
    
    # 3. Doppler Frequency Shift
    samples = apply_doppler_shift(samples, sample_rate, max_doppler_hz=doppler_hz)
    
    # 4. Oscillator Phase Noise
    samples = apply_phase_noise(samples, sample_rate, noise_std=0.02)
    
    # 5. I/Q Front-end Imbalance
    samples = apply_iq_imbalance(samples, amplitude_imbalance_db=iq_imbalance_db, phase_imbalance_deg=2.5)
    
    # 6. ADC Quantization (RTL-SDR 8-bit simulation)
    samples = apply_adc_quantization(samples, num_bits=adc_bits)
    
    # Metadata update
    meta = base_iq.metadata
    meta.update({
        "sdr_simulation": True,
        "k_factor_db": k_factor_db,
        "doppler_hz": doppler_hz,
        "adc_bits": adc_bits,
        "iq_imbalance_db": iq_imbalance_db
    })
    
    return IQCapture(
        samples=samples.astype(np.complex64),
        sample_rate=sample_rate,
        center_freq=433.92e6, # Common ISM SDR band
        source_format="cf32",
        metadata=meta
    )

def generate_field_dataset(output_dir: str, samples_per_mod: int = 3) -> Dict[str, Any]:
    """
    Generate complete realistic SDR field dataset across SNRs (-5 dB to 20 dB).
    """
    os.makedirs(output_dir, exist_ok=True)
    generated = []
    
    snr_levels = [-5.0, 0.0, 5.0, 12.0, 20.0]
    
    for mod in SUPPORTED_MODULATIONS:
        for snr in snr_levels:
            iq = generate_sdr_field_iq(mod_type=mod, snr_db=snr)
            filename = f"field_sdr_{mod}_snr{int(snr)}dB.iq"
            filepath = os.path.join(output_dir, filename)
            
            iq.samples.tofile(filepath)
            with open(filepath + ".json", "w") as f:
                json.dump(iq.metadata, f, indent=2)
                
            generated.append(filepath)
            
    return {
        "status": "success",
        "files_generated": len(generated),
        "output_directory": output_dir
    }

if __name__ == "__main__":
    res = generate_field_dataset("sample_data/sdr_field_captures")
    print(f"Generated SDR Field Dataset: {res['files_generated']} captures created.")
