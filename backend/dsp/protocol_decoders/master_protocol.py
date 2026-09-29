from typing import Dict, Any, Optional
import numpy as np

from backend.dsp.protocol_decoders.ais import decode_ais_payload
from backend.dsp.protocol_decoders.adsb import decode_adsb_payload
from backend.dsp.protocol_decoders.dmr import decode_dmr_payload
from backend.dsp.protocol_decoders.telemetry import decode_satellite_telemetry

def decode_protocol_payload(bit_string: str, sync_name: str = "") -> Dict[str, Any]:
    """
    Master Protocol Decoder Router:
    Inspects bitstream headers, sync words, and metadata to dispatch to protocol decoders.
    """
    if not bit_string or len(bit_string) < 16:
        return {
            "protocol": "RAW_BITSTREAM",
            "decoded": False,
            "reason": "Bitstream too short for protocol payload parsing"
        }

    sync_upper = sync_name.upper()

    # 1. AIS Maritime Check
    if "AIS" in sync_upper or bit_string.startswith("01111110"):  # 0x7E HDLC flag
        res = decode_ais_payload(bit_string)
        if res:
            res["decoded"] = True
            return res

    # 2. ADS-B Aviation Check
    if "ADSB" in sync_upper or "MODE_S" in sync_upper or len(bit_string) == 112:
        res = decode_adsb_payload(bit_string)
        if res:
            res["decoded"] = True
            return res

    # 3. DMR Digital Mobile Radio Check
    if "DMR" in sync_upper or "4FSK" in sync_upper:
        res = decode_dmr_payload(bit_string)
        if res:
            res["decoded"] = True
            return res

    # 4. Satellite Telemetry Check (CCSDS / AX.25)
    if "CCSDS" in sync_upper or "AX25" in sync_upper or "SATELLITE" in sync_upper:
        res = decode_satellite_telemetry(bit_string)
        if res:
            res["decoded"] = True
            return res

    # Fallback to Generic Protocol Auto-Discovery
    for decoder_fn in [decode_adsb_payload, decode_ais_payload, decode_satellite_telemetry, decode_dmr_payload]:
        res = decoder_fn(bit_string)
        if res:
            res["decoded"] = True
            return res

    return {
        "protocol": "RAW_BINARY_STREAM",
        "decoded": False,
        "bit_length": len(bit_string),
        "reason": "No matched protocol signature (Generic payload frame)"
    }
