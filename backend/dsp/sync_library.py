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
        "domain": "Tactical RF / Radar",
        "protocol": "Barker 7-bit Radar Code",
        "icon": "radio",
        "description": "7-bit Barker code sequence [1,1,1,0,0,1,0]"
    },
    "Barker-11": {
        "hex": "0x712",
        "bits": np.array([1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0], dtype=np.uint8),
        "domain": "Tactical RF / Radar",
        "protocol": "Barker 11-bit Radar Code",
        "icon": "radio",
        "description": "11-bit Barker code sequence [1,1,1,0,0,0,1,0,0,1,0]"
    },
    "Barker-13": {
        "hex": "0x1F35",
        "bits": np.array([1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1], dtype=np.uint8),
        "domain": "Tactical RF / Radar",
        "protocol": "Barker 13-bit Radar Code",
        "icon": "radio",
        "description": "13-bit Barker code sequence [1,1,1,1,1,0,0,1,1,0,1,0,1]"
    },
    "ADS-B-1090": {
        "hex": "0x8D",
        "bits": np.array([1, 0, 0, 0, 1, 1, 0, 1], dtype=np.uint8),
        "domain": "Aviation",
        "protocol": "ADS-B Aircraft Transponder",
        "icon": "plane",
        "description": "Commercial / Military Aircraft 1090 MHz Mode-S Transponder Preamble (0x8D)"
    },
    "ACARS-VHF": {
        "hex": "0x1616",
        "bits": np.array([0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0], dtype=np.uint8),
        "domain": "Aviation",
        "protocol": "ACARS Aircraft Telemetry",
        "icon": "plane",
        "description": "VHF ACARS Aircraft Data Link SYN SYN Preamble (0x1616)"
    },
    "AIS-Maritime": {
        "hex": "0x7E",
        "bits": np.array([0, 1, 1, 1, 1, 1, 1, 0], dtype=np.uint8),
        "domain": "Maritime",
        "protocol": "AIS Ship Positioning System",
        "icon": "ship",
        "description": "AIS Maritime Vessel Tracking GMSK HDLC Flag Pattern (0x7E)"
    },
    "MAVLink-Drone": {
        "hex": "0xFE",
        "bits": np.array([1, 1, 1, 1, 1, 1, 1, 0], dtype=np.uint8),
        "domain": "Drone / UAV",
        "protocol": "MAVLink Telemetry Protocol",
        "icon": "drone",
        "description": "Unmanned Aerial Vehicle (UAV) MAVLink v1 Packet STX (0xFE)"
    },
    "NOAA-Satellite": {
        "hex": "0x2A",
        "bits": np.array([0, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8),
        "domain": "Satellite",
        "protocol": "NOAA Weather Satellite APT",
        "icon": "satellite",
        "description": "NOAA LEO Weather Satellite Automatic Picture Transmission Sync (0x2A)"
    },
    "CCSDS-ASM-32": {
        "hex": "0x1ACFFC1D",
        "bits": np.array([
            0, 0, 0, 1, 1, 0, 1, 0,
            1, 1, 0, 0, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 0, 0,
            0, 0, 0, 1, 1, 1, 0, 1
        ], dtype=np.uint8),
        "domain": "Satellite",
        "protocol": "CCSDS Deep Space Link",
        "icon": "satellite",
        "description": "CCSDS 32-bit Attached Sync Marker (0x1ACFFC1D)"
    },
    "P25-Tactical": {
        "hex": "0x755E",
        "bits": np.array([0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0], dtype=np.uint8),
        "domain": "Tactical Defense",
        "protocol": "P25 Land Mobile Radio",
        "icon": "radio",
        "description": "APCO P25 Tactical Military / Emergency Service Frame Sync (0x755E)"
    },
    "AX.25-Flag": {
        "hex": "0x7E",
        "bits": np.array([0, 1, 1, 1, 1, 1, 1, 0], dtype=np.uint8),
        "domain": "Maritime / Amateur Radio",
        "protocol": "AX.25 Packet Radio",
        "icon": "radio",
        "description": "AX.25 / HDLC 8-bit Flag pattern (0x7E)"
    },
    "Ethernet-SFD": {
        "hex": "0xD5",
        "bits": np.array([1, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8),
        "domain": "Digital Network",
        "protocol": "Ethernet Frame SFD",
        "icon": "radio",
        "description": "Ethernet Start Frame Delimiter SFD (0xD5)"
    },
    "Generic-Preamble-16": {
        "hex": "0xAAAA",
        "bits": np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8),
        "domain": "Tactical RF",
        "protocol": "Generic FSK/PSK Preamble",
        "icon": "radio",
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
