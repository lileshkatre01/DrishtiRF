import numpy as np

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
