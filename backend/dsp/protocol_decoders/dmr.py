import numpy as np
from typing import Dict, Any, Optional

DMR_VOICE_SYNC = "011101010101111111010111010101111111011101011101"
DMR_DATA_SYNC  = "110111111111010101111101011101011101111101011101"

def decode_dmr_payload(bit_string: str) -> Optional[Dict[str, Any]]:
    """
    DMR (Digital Mobile Radio / ETSI TS 102 361) 4FSK Telemetry Decoder.
    Parses DMR burst headers into Color Code, Target ID, Source ID, and Burst Type.
    """
    if len(bit_string) < 96:
        return None

    try:
        is_voice_sync = DMR_VOICE_SYNC in bit_string
        is_data_sync = DMR_DATA_SYNC in bit_string

        sync_type = "Voice Sync" if is_voice_sync else ("Data Sync" if is_data_sync else "Custom Sync")
        
        # Color code (4 bits)
        cc = int(bit_string[0:4], 2) if len(bit_string) >= 4 else 0
        
        # Target ID & Source ID parsing (if length >= 52)
        target_id = int(bit_string[4:28], 2) if len(bit_string) >= 28 else 0
        source_id = int(bit_string[28:52], 2) if len(bit_string) >= 52 else 0

        return {
            "protocol": "DMR",
            "burst_sync": sync_type,
            "color_code": cc,
            "target_id": target_id,
            "source_id": source_id,
            "modulation": "4FSK (9.6 kbps / 12.5 kHz)"
        }
    except Exception:
        return None
