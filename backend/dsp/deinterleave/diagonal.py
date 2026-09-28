import numpy as np

def deinterleave_diagonal(bits: np.ndarray, rows: int = 8, cols: int = 8) -> np.ndarray:
    """
    Diagonal De-interleaver:
    Writes bits into a matrix of shape (rows, cols) and reads out diagonally.
    """
    block_size = rows * cols
    if len(bits) < block_size or block_size <= 0:
        return bits

    num_blocks = len(bits) // block_size
    output = []

    for b in range(num_blocks):
        block = bits[b * block_size : (b + 1) * block_size].reshape(rows, cols)
        diag_block = np.zeros((rows, cols), dtype=np.uint8)
        for r in range(rows):
            for c in range(cols):
                diag_block[r, c] = block[(r + c) % rows, c]
        output.extend(diag_block.flatten())

    if len(bits) > num_blocks * block_size:
        output.extend(bits[num_blocks * block_size:])

    return np.array(output, dtype=np.uint8)
