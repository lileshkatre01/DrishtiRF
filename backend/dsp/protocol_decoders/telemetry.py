import numpy as np
from typing import Dict, Any, Optional

def decode_satellite_telemetry(bit_string: str) -> Optional[Dict[str, Any]]:
    """
    CCSDS & AX.25 Satellite Telemetry Payload Decoder.
    Parses CubeSat beacon headers, APID, packet sequence counters, and sensor metrics.
    """
    if len(bit_string) < 48:
        return None

    try:
        # CCSDS Primary Header (48 bits = 6 bytes)
        version = int(bit_string[0:3], 2)
        type_flag = int(bit_string[3:4], 2)
        sec_header_flag = int(bit_string[4:5], 2)
        apid = int(bit_string[5:16], 2)  # Application Process Identifier
        
        seq_flags = int(bit_string[16:18], 2)
        seq_count = int(bit_string[18:32], 2)
        packet_len = int(bit_string[32:48], 2) + 1

        seq_map = {0: "Continuation Segment", 1: "First Segment", 2: "Last Segment", 3: "Unsegmented Standalone"}

        return {
            "protocol": "CCSDS / AX.25 Satellite Telemetry",
            "apid": f"0x{apid:03X} ({apid})",
            "packet_type": "Telemetry" if type_flag == 0 else "Telecommand",
            "sequence_counter": seq_count,
            "sequence_flag": seq_map.get(seq_flags, "Unknown"),
            "payload_length_bytes": packet_len,
            "secondary_header_present": bool(sec_header_flag)
        }
    except Exception:
        return None
