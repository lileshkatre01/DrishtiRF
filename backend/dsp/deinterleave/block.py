import numpy as np
from typing import Tuple, Dict, Any

def deinterleave_block(bits: np.ndarray, rows: int, cols: int) -> np.ndarray:
    """
    Block De-interleaver:
    Writes bits into a matrix of shape (rows, cols) by columns and reads out by rows.
    """
    block_size = rows * cols
    if len(bits) < block_size or block_size <= 0:
        return bits

    num_blocks = len(bits) // block_size
    trimmed_len = num_blocks * block_size
    trimmed_bits = bits[:trimmed_len]

    # Reshape into blocks and transpose (write by columns, read by rows)
    blocks = trimmed_bits.reshape(num_blocks, cols, rows)
    deinterleaved = blocks.transpose(0, 2, 1).reshape(-1)

    # Append any remaining trailing bits
    if len(bits) > trimmed_len:
        deinterleaved = np.concatenate([deinterleaved, bits[trimmed_len:]])

    return deinterleaved.astype(np.uint8)

def search_block_interleaver(bits: np.ndarray, max_dim: int = 32) -> Tuple[int, int, float]:
    """
    Sweep matrix dimensions (rows x cols) to discover block interleaver geometry scored by autocorrelation peak.
    """
    if len(bits) < 128:
        return 1, 1, 0.0

    best_r, best_c = 1, 1
    best_score = 0.0

    for r in range(2, max_dim + 1):
        for c in range(2, max_dim + 1):
            if r * c > len(bits) // 2:
                continue

            test_bits = deinterleave_block(bits[:1024], r, c)
            # Evaluate autocorrelation at lag 1 to score structure
            if len(test_bits) > 2:
                score = float(np.mean(test_bits[:-1] == test_bits[1:]))
                if score > best_score:
                    best_score = score
                    best_r, best_c = r, c

    return best_r, best_c, best_score
