import numpy as np
import reedsolo
from typing import Tuple, Dict, Any

def decode_reed_solomon(bits: np.ndarray, n: int = 255, k: int = 223) -> Tuple[np.ndarray, bool, int]:
    """
    Reed-Solomon (RS) Block Decoder (e.g. RS(255, 223) CCSDS standard):
    Packs bits into bytes, runs RS error correction using reedsolo.
    Returns (decoded_payload_bits, syndrome_zero_success, corrected_errors_count).
    """
    if len(bits) < (n * 8):
        # Packing fewer bits into byte array
        byte_arr = np.packbits(bits)
        if len(byte_arr) <= (n - k):
            return bits, False, 0
    else:
        byte_arr = np.packbits(bits[: n * 8])

    nsym = n - k
    codec = reedsolo.RSCodec(nsym)

    try:
        decoded_bytes, decoded_full, err_count = codec.decode(byte_arr.tobytes())
        decoded_bits = np.unpackbits(np.frombuffer(decoded_bytes, dtype=np.uint8))
        return decoded_bits, True, err_count
    except Exception:
        # If decode failed, unpack uncorrected bytes
        decoded_bits = np.unpackbits(byte_arr[:k])
        return decoded_bits, False, 0
