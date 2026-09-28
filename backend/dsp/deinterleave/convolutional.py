import numpy as np
from typing import Tuple

def deinterleave_conv(bits: np.ndarray, depth: int = 4, span: int = 2) -> np.ndarray:
    """
    Convolutional De-interleaver (Ramsey / Forney style):
    Passes bits through a set of shift registers of increasing delay (0, span, 2*span, ..., (depth-1)*span).
    """
    if depth <= 1 or len(bits) < depth * span:
        return bits

    output_bits = np.zeros(len(bits), dtype=np.uint8)
    delays = [i * span for i in range(depth)]
    buffers = [np.zeros(d, dtype=np.uint8) for d in delays]

    for i in range(len(bits)):
        branch = i % depth
        val = bits[i]
        
        if delays[branch] == 0:
            out_val = val
        else:
            out_val = buffers[branch][-1]
            buffers[branch] = np.roll(buffers[branch], 1)
            buffers[branch][0] = val

        output_bits[i] = out_val

    return output_bits

def search_conv_interleaver(bits: np.ndarray, max_depth: int = 16, max_span: int = 8) -> Tuple[int, int, float]:
    """
    Sweep convolutional interleaver parameters (depth D, span M) scored by bit transition structure.
    """
    if len(bits) < 128:
        return 1, 1, 0.0

    best_d, best_m = 1, 1
    best_score = 0.0

    for d in range(2, max_depth + 1):
        for m in range(1, max_span + 1):
            test_bits = deinterleave_conv(bits[:512], depth=d, span=m)
            score = float(np.mean(test_bits[:-1] == test_bits[1:]))
            if score > best_score:
                best_score = score
                best_d, best_m = d, m

    return best_d, best_m, best_score
