"""
DrishtiRF - Standard Sync-Word & Preamble Library
Provides standard SIGINT frame preamble/sync-word definitions and bit pattern conversion helpers.
"""

import numpy as np
from typing import Dict, List, Any

# Standard Sync Pattern Registry
SYNC_PATTERNS: Dict[str, Dict[str, Any]] = {
    "Barker-7": {
        "hex": "0x72",
        "bits": np.array([1, 1, 1, 0, 0, 1, 0], dtype=np.uint8),
        "description": "7-bit Barker code sequence [1,1,1,0,0,1,0]"
    },
    "Barker-11": {
        "hex": "0x712",
        "bits": np.array([1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0], dtype=np.uint8),
        "description": "11-bit Barker code sequence [1,1,1,0,0,0,1,0,0,1,0]"
    },
    "Barker-13": {
        "hex": "0x1F35",
        "bits": np.array([1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1], dtype=np.uint8),
        "description": "13-bit Barker code sequence [1,1,1,1,1,0,0,1,1,0,1,0,1]"
    },
    "CCSDS-ASM-32": {
        "hex": "0x1ACFFC1D",
        "bits": np.array([
            0, 0, 0, 1, 1, 0, 1, 0,
            1, 1, 0, 0, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 0, 0,
            0, 0, 0, 1, 1, 1, 0, 1
        ], dtype=np.uint8),
        "description": "CCSDS 32-bit Attached Sync Marker (0x1ACFFC1D)"
    },
    "AX.25-Flag": {
        "hex": "0x7E",
        "bits": np.array([0, 1, 1, 1, 1, 1, 1, 0], dtype=np.uint8),
        "description": "AX.25 / HDLC 8-bit Flag pattern (0x7E)"
    },
    "Ethernet-SFD": {
        "hex": "0xD5",
        "bits": np.array([1, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8),
        "description": "Ethernet Start Frame Delimiter SFD (0xD5)"
    },
    "Generic-Preamble-16": {
        "hex": "0xAAAA",
        "bits": np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8),
        "description": "16-bit Alternating 1/0 Preamble (0xAAAA)"
    }
}

def hex_to_bits(hex_str: str) -> np.ndarray:
    """
    Convert a hex string (e.g. '0x1ACFFC1D' or '1ACFFC1D') to a 1D uint8 numpy array of bits.
    """
    clean_hex = hex_str.lower().replace("0x", "")
    if len(clean_hex) % 2 != 0:
        clean_hex = "0" + clean_hex
    byte_vals = bytes.fromhex(clean_hex)
    bits = np.unpackbits(np.frombuffer(byte_vals, dtype=np.uint8))
    return bits

def bits_to_hex(bits: np.ndarray) -> str:
    """
    Convert a 1D uint8 array of bits to a clean hex string.
    """
    if len(bits) == 0:
        return ""
    # Pad bits to byte boundary if necessary
    remainder = len(bits) % 8
    if remainder != 0:
        pad_len = 8 - remainder
        bits = np.pad(bits, (0, pad_len), mode='constant', constant_values=0)
    byte_vals = np.packbits(bits)
    return byte_vals.tobytes().hex()

def get_all_patterns() -> Dict[str, Dict[str, Any]]:
    """
    Return all registered sync patterns.
    """
    return SYNC_PATTERNS
