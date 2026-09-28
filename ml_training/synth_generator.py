import os
import json
import numpy as np
from typing import Tuple, Dict, Any, List

from backend.dsp.iqcapture import IQCapture

SUPPORTED_MODULATIONS = ["2FSK", "4FSK", "BPSK", "QPSK", "8PSK", "16QAM", "64QAM"]

def generate_synthetic_iq(
    mod_type: str = "QPSK",
    num_symbols: int = 4000,
    sample_rate: float = 1e6,
    symbol_rate: float = 100e3,
    snr_db: float = 15.0,
    freq_offset_hz: float = 0.0,
    center_freq: float = 915e6
) -> IQCapture:
    """
    Generate synthetic IQ waveform for a given modulation scheme, symbol rate, SNR, and frequency offset.
    """
    mod_upper = mod_type.upper()
    if mod_upper not in SUPPORTED_MODULATIONS:
        raise ValueError(f"Unsupported modulation: {mod_type}. Must be one of {SUPPORTED_MODULATIONS}")

    sps = int(round(sample_rate / symbol_rate))
    if sps < 2:
        sps = 2
        symbol_rate = sample_rate / sps

    total_samples = num_symbols * sps
    t = np.arange(total_samples) / sample_rate

    if "FSK" in mod_upper:
        # FSK Modulation
        M = 2 if mod_upper == "2FSK" else 4
        freq_dev = symbol_rate * 0.5
        symbols = np.random.randint(0, M, size=num_symbols)
        
        if M == 2:
            freq_shifts = (symbols * 2 - 1) * freq_dev
        else:
            freq_shifts = (symbols - 1.5) * (freq_dev * 2 / 3)
            
        freq_stream = np.repeat(freq_shifts, sps)
        phase = 2 * np.pi * np.cumsum(freq_stream) / sample_rate
        baseband = np.exp(1j * phase)

    elif "PSK" in mod_upper:
        # PSK Modulation (BPSK, QPSK, 8PSK)
        if mod_upper == "BPSK":
            M = 2
            phases = np.array([0, np.pi])
        elif mod_upper == "QPSK":
            M = 4
            phases = np.array([np.pi/4, 3*np.pi/4, -3*np.pi/4, -np.pi/4])
        else:  # 8PSK
            M = 8
            phases = np.linspace(0, 2*np.pi, 8, endpoint=False)
            
        symbols = np.random.randint(0, M, size=num_symbols)
        constellation = np.exp(1j * phases[symbols])
        baseband = np.repeat(constellation, sps)

    elif "QAM" in mod_upper:
        # QAM Modulation (16QAM, 64QAM)
        if mod_upper == "16QAM":
            grid_side = 4
        else:  # 64QAM
            grid_side = 8
            
        values = np.linspace(-(grid_side-1), grid_side-1, grid_side)
        real_part = np.random.choice(values, size=num_symbols)
        imag_part = np.random.choice(values, size=num_symbols)
        constellation = real_part + 1j * imag_part
        # Normalize constellation power to 1
        constellation = constellation / np.sqrt(np.mean(np.abs(constellation)**2))
        baseband = np.repeat(constellation, sps)

    # Apply Carrier Frequency Offset
    if freq_offset_hz != 0.0:
        cfo_carrier = np.exp(1j * (2 * np.pi * freq_offset_hz * t))
        baseband = baseband * cfo_carrier

    # Apply Additive White Gaussian Noise (AWGN)
    signal_power = np.mean(np.abs(baseband) ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10.0))
    noise = (np.random.normal(0, np.sqrt(noise_power / 2), total_samples) +
             1j * np.random.normal(0, np.sqrt(noise_power / 2), total_samples))

    noisy_samples = (baseband + noise).astype(np.complex64)

    return IQCapture(
        samples=noisy_samples,
        sample_rate=sample_rate,
        center_freq=center_freq,
        source_format="cf32",
        metadata={
            "ground_truth_mod": mod_upper,
            "ground_truth_symbol_rate": symbol_rate,
            "ground_truth_snr_db": snr_db,
            "ground_truth_cfo_hz": freq_offset_hz,
            "samples_per_symbol": sps
        }
    )

def save_synthetic_iq_dataset(output_dir: str, count_per_mod: int = 2) -> List[str]:
    """
    Generate synthetic test corpus across all modulations and save as raw binary files.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []

    for mod in SUPPORTED_MODULATIONS:
        for i in range(count_per_mod):
            snr = float(np.random.choice([10, 15, 20]))
            cfo = float(np.random.choice([0, 10000, -15000]))
            iq = generate_synthetic_iq(mod_type=mod, snr_db=snr, freq_offset_hz=cfo)
            
            filename = f"synth_{mod}_snr{int(snr)}_fs1000000_cf915000000_cf32_{i}.iq"
            filepath = os.path.join(output_dir, filename)
            
            # Save raw complex64 bytes
            iq.samples.tofile(filepath)
            
            # Save JSON ground truth sidecar
            meta_path = filepath + ".json"
            with open(meta_path, "w") as f:
                json.dump(iq.metadata, f, indent=2)
                
            generated_files.append(filepath)

    return generated_files
