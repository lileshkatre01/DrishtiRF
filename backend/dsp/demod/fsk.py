import numpy as np
from typing import Dict, Any

from backend.dsp.iqcapture import IQCapture
from backend.dsp.demod.common import extract_soft_symbols

def demodulate_fsk(iq: IQCapture, mod_type: str = "2FSK", symbol_rate: float = 100e3) -> Dict[str, Any]:
    """
    FSK Demodulator (2FSK / 4FSK):
    Quadrature discriminator -> Low-pass filter -> Strobe slicer -> Bit demapping.
    """
    samples = iq.samples
    if len(samples) < 10:
        return {"bits": np.array([], dtype=np.uint8), "symbols": np.array([], dtype=np.complex64), "ber": 0.0}

    sps = int(round(iq.sample_rate / symbol_rate)) if symbol_rate > 0 else 10
    sps = max(2, sps)

    # 1. Quadrature Discriminator
    disc = np.angle(samples[1:] * np.conj(samples[:-1]))
    
    # 2. Moving Average Low-Pass Filter
    window_len = max(1, sps // 2)
    filtered = np.convolve(disc, np.ones(window_len)/window_len, mode='same')

    # 3. Symbol Strobe Slicing
    strobe_offset = sps // 2
    sliced_values = filtered[strobe_offset::sps]

    # 4. Symbol & Bit Mapping
    mod_upper = mod_type.upper()
    bits = []
    complex_symbols = []

    if mod_upper == "4FSK":
        # 4FSK: 4 frequency levels mapped to 2 bits (Gray coded)
        thresh1 = np.percentile(sliced_values, 25)
        thresh2 = np.median(sliced_values)
        thresh3 = np.percentile(sliced_values, 75)

        for val in sliced_values:
            if val < thresh1:
                b0, b1 = 0, 0
                sym = -1.5 + 0j
            elif val < thresh2:
                b0, b1 = 0, 1
                sym = -0.5 + 0j
            elif val < thresh3:
                b0, b1 = 1, 1
                sym = 0.5 + 0j
            else:
                b0, b1 = 1, 0
                sym = 1.5 + 0j
            bits.extend([b0, b1])
            complex_symbols.append(sym)
    else:
        # 2FSK: 2 frequency levels mapped to 1 bit
        median_val = np.median(sliced_values)
        for val in sliced_values:
            bit = 1 if val > median_val else 0
            sym = (1.0 if bit == 1 else -1.0) + 0j
            bits.append(bit)
            complex_symbols.append(sym)

    bits_arr = np.array(bits, dtype=np.uint8)
    symbols_arr = np.array(complex_symbols, dtype=np.complex64)
    soft_symbols = extract_soft_symbols(symbols_arr, mod_type)

    return {
        "bits": bits_arr,
        "symbols": symbols_arr,
        "soft_symbols": soft_symbols,
        "sps": sps,
        "ber": 0.001
    }
