import numpy as np
from typing import Tuple, Dict, Any

from backend.dsp.fec.viterbi import decode_viterbi
from backend.dsp.fec.reed_solomon import decode_reed_solomon
from backend.dsp.deinterleave.block import deinterleave_block

def decode_concatenated(bits: np.ndarray) -> Tuple[np.ndarray, bool, float]:
    """
    CCSDS Standard Concatenated Code Decoder:
    Inner Viterbi Convolutional Decoder -> Convolutional/Block De-interleaver -> Outer Reed-Solomon RS(255,223) Decoder.
    """
    # 1. Inner Viterbi Decoding
    viterbi_bits, viterbi_score = decode_viterbi(bits, rate="1/2", K=7)

    # 2. Intermediate De-interleaving
    deinterleaved_bits = deinterleave_block(viterbi_bits, rows=8, cols=16)

    # 3. Outer Reed-Solomon Decoding
    payload_bits, rs_success, err_count = decode_reed_solomon(deinterleaved_bits, n=255, k=223)

    overall_confidence = 0.98 if (rs_success and viterbi_score > 0.8) else (viterbi_score * 0.7)
    return payload_bits, rs_success, overall_confidence
