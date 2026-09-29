import numpy as np
from typing import Dict, Any, Optional, List

def decode_ais_payload(bit_string: str) -> Optional[Dict[str, Any]]:
    """
    AIS (Automatic Identification System) VHF Maritime Telemetry Decoder.
    Parses AIS 6-bit armor payload strings into structured vessel telemetry.
    """
    if len(bit_string) < 168:  # Minimum length for Type 1/2/3 position report (168 bits)
        return None

    # Convert binary string bits to 6-bit AIS characters or integers
    try:
        msg_type = int(bit_string[0:6], 2)
        repeat_indicator = int(bit_string[6:8], 2)
        mmsi = int(bit_string[8:38], 2)

        if msg_type in [1, 2, 3]:
            # Position Report Class A
            nav_status = int(bit_string[38:42], 2)
            rot = int(bit_string[42:50], 2)
            sog_raw = int(bit_string[50:60], 2)
            sog_knots = sog_raw / 10.0 if sog_raw < 1023 else None
            
            pos_accuracy = int(bit_string[60:61], 2)
            
            # Longitude: 28-bit signed int (1/10000 bit = minutes)
            lon_raw = int(bit_string[61:89], 2)
            if lon_raw & (1 << 27):
                lon_raw -= (1 << 28)
            longitude = lon_raw / 600000.0 if lon_raw != 0x6791AC0 else None
            
            # Latitude: 27-bit signed int
            lat_raw = int(bit_string[89:116], 2)
            if lat_raw & (1 << 26):
                lat_raw -= (1 << 27)
            latitude = lat_raw / 600000.0 if lat_raw != 0x3412140 else None
            
            cog_raw = int(bit_string[116:128], 2)
            cog_deg = cog_raw / 10.0 if cog_raw < 3600 else None
            
            heading = int(bit_string[128:137], 2)
            true_heading = heading if heading < 360 else None

            nav_status_map = {
                0: "Under way using engine",
                1: "At anchor",
                2: "Not under command",
                3: "Restricted manoeuvrability",
                4: "Constrained by her draught",
                5: "Moored",
                6: "Aground",
                7: "Engaged in Fishing",
                8: "Under way sailing"
            }

            return {
                "protocol": "AIS",
                "message_type": f"Type {msg_type} (Class A Position Report)",
                "mmsi": mmsi,
                "navigation_status": nav_status_map.get(nav_status, f"Status {nav_status}"),
                "latitude": latitude,
                "longitude": longitude,
                "speed_over_ground_knots": sog_knots,
                "course_over_ground_deg": cog_deg,
                "true_heading_deg": true_heading,
                "position_accuracy": "High (< 10m)" if pos_accuracy == 1 else "Low (> 10m)"
            }
        
        elif msg_type == 5:
            # Type 5 Static and Voyage Data
            callsign_bits = bit_string[70:112]
            vessel_name_bits = bit_string[112:232] if len(bit_string) >= 232 else ""
            
            return {
                "protocol": "AIS",
                "message_type": "Type 5 (Class A Static & Voyage Data)",
                "mmsi": mmsi,
                "callsign_raw_bits": len(callsign_bits),
                "vessel_name_raw_bits": len(vessel_name_bits)
            }
        else:
            return {
                "protocol": "AIS",
                "message_type": f"Type {msg_type}",
                "mmsi": mmsi
            }
            
    except Exception:
        return None
