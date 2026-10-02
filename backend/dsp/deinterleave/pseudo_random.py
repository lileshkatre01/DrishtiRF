import numpy as np
from typing import Tuple

def deinterleave_pseudo_random(bits: np.ndarray, seed: int = 42, block_size: int = 64) -> np.ndarray:
    """
    Pseudo-Random De-interleaver:
    Permutes bits within block_size using a pseudo-random seed permutation index.
    """
    if len(bits) < block_size or block_size <= 0:
        return bits

    rng = np.random.RandomState(seed)
    perm = rng.permutation(block_size)
    inv_perm = np.argsort(perm)

    num_blocks = len(bits) // block_size
    output = []

    for b in range(num_blocks):
        block = bits[b * block_size : (b + 1) * block_size]
        deinterleaved_block = block[inv_perm]
        output.extend(deinterleaved_block)

    if len(bits) > num_blocks * block_size:
        output.extend(bits[num_blocks * block_size:])

    return np.array(output, dtype=np.uint8)


def search_pseudo_random_interleaver(bits: np.ndarray) -> Tuple[int, int, float]:
    """
    Auto-search for best Pseudo-Random interleaver parameters.
    Sweeps common LFSR seeds and block sizes, scores by output entropy reduction.
    Returns (best_seed, best_block_size, best_score).
    """
    if len(bits) < 32:
        return 42, 64, 0.0

    # Common LFSR seeds used in real-world systems
    seeds_to_test = [42, 0, 1, 7, 15, 31, 63, 127, 255]
    # Common block sizes aligned to standard frame sizes
    block_sizes_to_test = [32, 64, 128, 256]

    best_seed = 42
    best_block_size = 64
    best_score = 0.0

    search_bits = bits[:512] if len(bits) > 512 else bits

    # Baseline entropy of raw input
    raw_bytes = np.packbits(search_bits).tobytes()
    from collections import Counter
    def _entropy(b: bytes) -> float:
        if not b:
            return 0.0
        counts = Counter(b)
        total = len(b)
        return -sum((c / total) * np.log2(c / total + 1e-12) for c in counts.values())

    baseline_entropy = _entropy(raw_bytes)

    for seed in seeds_to_test:
        for block_size in block_sizes_to_test:
            if block_size > len(search_bits):
                continue
            deint = deinterleave_pseudo_random(search_bits, seed=seed, block_size=block_size)
            out_bytes = np.packbits(deint).tobytes()
            out_entropy = _entropy(out_bytes)
            # Score: how much entropy was reduced (lower output entropy = better structure found)
            score = max(0.0, baseline_entropy - out_entropy)
            if score > best_score:
                best_score = score
                best_seed = seed
                best_block_size = block_size

    # Normalize score to 0-1 range
    normalized_score = min(1.0, best_score / max(1.0, baseline_entropy))
    return best_seed, best_block_size, float(normalized_score)

