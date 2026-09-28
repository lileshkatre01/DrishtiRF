import numpy as np
from typing import Tuple, Dict, Any
import commpy.channelcoding.convcode as cc

# Standard CCSDS / NASA (171, 133) K=7 Rate 1/2 Trellis
_TRELLIS_K7_R12 = cc.Trellis(np.array([7]), np.array([[0o171, 0o133]]))

def encode_convolutional(bits: np.ndarray, rate: str = "1/2", K: int = 7) -> np.ndarray:
    """
    Standard Convolutional Encoder (NASA / CCSDS K=7 Rate 1/2 polynomials 171/133 octal).
    """
    if len(bits) == 0:
        return np.array([], dtype=np.uint8)

    bits_int = bits.astype(int)
    encoded = cc.conv_encode(bits_int, _TRELLIS_K7_R12)
    return encoded.astype(np.uint8)

def decode_viterbi(bits: np.ndarray, rate: str = "1/2", K: int = 7) -> Tuple[np.ndarray, float]:
    """
    Viterbi Convolutional Decoder:
    Decodes hard/soft decision bits using trellised Viterbi algorithm.
    Returns (decoded_payload_bits, syndrome_score).
    """
    if len(bits) == 0:
        return np.array([], dtype=np.uint8), 0.0

    try:
        bits_float = bits.astype(float)
        decoded_full = cc.viterbi_decode(bits_float, _TRELLIS_K7_R12, tb_depth=15)
        
        # Determine payload length (rate 1/2)
        payload_len = len(bits) // 2
        decoded = decoded_full[:payload_len].astype(np.uint8)

        # Re-encode to verify syndrome / match score
        re_encoded = encode_convolutional(decoded, rate=rate, K=K)
        min_comp = min(len(bits), len(re_encoded))
        if min_comp > 0:
            match_score = float(np.mean(bits[:min_comp] == re_encoded[:min_comp]))
        else:
            match_score = 0.50

        return decoded, match_score
    except Exception:
        # Fallback for odd / truncated bit streams
        min_len = len(bits) // 2
        decoded = bits[:min_len*2:2]
        return decoded.astype(np.uint8), 0.30
