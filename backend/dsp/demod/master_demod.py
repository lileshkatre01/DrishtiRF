import numpy as np
from typing import Dict, Any, Optional

from backend.dsp.iqcapture import IQCapture
from backend.dsp.demod.fsk import demodulate_fsk
from backend.dsp.demod.psk import demodulate_psk
from backend.dsp.demod.qam import demodulate_qam
from backend.dsp.demod.am import demodulate_am
from backend.dsp.demod.fm import demodulate_fm
from backend.dsp.demod.common import generate_constellation_points, generate_eye_diagram

def demodulate_signal(iq: IQCapture, mod_type: str = "QPSK", symbol_rate: float = 100e3) -> Dict[str, Any]:
    """
    Master Demodulation Router:
    Dispatches to AM, FM, FSK, PSK, or QAM demodulator chains dynamically based on modulation label.
    Computes constellation scatter points and eye-diagram time vs amplitude matrix.
    """
    mod_upper = mod_type.upper()

    if "AM" == mod_upper or "ASK" in mod_upper:
        demod_res = demodulate_am(iq, mod_type=mod_upper, symbol_rate=symbol_rate)
    elif "FM" == mod_upper:
        demod_res = demodulate_fm(iq, mod_type=mod_upper, symbol_rate=symbol_rate)
    elif "FSK" in mod_upper:
        demod_res = demodulate_fsk(iq, mod_type=mod_upper, symbol_rate=symbol_rate)
    elif "QAM" in mod_upper:
        demod_res = demodulate_qam(iq, mod_type=mod_upper, symbol_rate=symbol_rate)
    else:
        # Default to PSK (BPSK / QPSK / 8PSK)
        demod_res = demodulate_psk(iq, mod_type=mod_upper, symbol_rate=symbol_rate)


    symbols = demod_res["symbols"]
    bits = demod_res["bits"]
    sps = demod_res["sps"]

    # Generate 2D Constellation plot scatter points
    constellation_data = generate_constellation_points(symbols)

    # Generate Eye-Diagram matrix
    eye_diagram_data = generate_eye_diagram(iq.samples, sps=sps)

    # Format bitstream preview (hex & length)
    bit_str = "".join(str(b) for b in bits[:256])
    byte_array = np.packbits(bits) if len(bits) > 0 else np.array([], dtype=np.uint8)
    hex_preview = byte_array[:32].tobytes().hex()

    return {
        "modulation": mod_upper,
        "symbol_rate_baud": symbol_rate,
        "bit_count": len(bits),
        "symbol_count": len(symbols),
        "ber_proxy": demod_res["ber"],
        "bit_preview_str": bit_str,
        "hex_preview": hex_preview,
        "constellation": constellation_data,
        "eye_diagram": eye_diagram_data,
        "bits": bits.tolist(),
        "soft_symbols": demod_res["soft_symbols"].tolist()
    }
