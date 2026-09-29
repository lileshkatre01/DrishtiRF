import numpy as np
from typing import Dict, Any, Optional

def decode_adsb_payload(bit_string: str) -> Optional[Dict[str, Any]]:
    """
    1090 MHz Mode S Extended Squitter (ADS-B Aviation Telemetry) Decoder.
    Parses 112-bit Mode S PPM bitstreams into aircraft telemetry (ICAO, Callsign, Altitude, Speed).
    """
    if len(bit_string) < 112:
        return None

    try:
        df = int(bit_string[0:5], 2)
        if df not in [17, 18]:  # DF=17 is Mode S Extended Squitter, DF=18 is Non-ICAO ADS-B
            return None

        ca = int(bit_string[5:8], 2)
        icao_address = f"{int(bit_string[8:32], 2):06X}"
        me_bits = bit_string[32:88]  # 56-bit Extended Squitter payload
        type_code = int(me_bits[0:5], 2)

        res = {
            "protocol": "ADS-B",
            "downlink_format": f"DF{df}",
            "icao_address": f"0x{icao_address}",
            "type_code": type_code,
            "capability": ca
        }

        if 1 <= type_code <= 4:
            # Aircraft Identification & Category (Callsign)
            charset = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######"
            callsign = ""
            for i in range(8):
                char_code = int(me_bits[8 + i*6 : 8 + (i+1)*6], 2)
                if char_code < len(charset):
                    callsign += charset[char_code]
            res["callsign"] = callsign.strip("_# ")
            res["message_type"] = "Aircraft Identification"

        elif 9 <= type_code <= 18:
            # Airborne Position (Barometric Altitude)
            alt_bits = me_bits[8:20]
            q_bit = int(alt_bits[7])
            if q_bit == 1:
                # 25 ft increments
                n = (int(alt_bits[0:7], 2) << 4) | int(alt_bits[8:12], 2)
                altitude_ft = n * 25 - 1000
                res["altitude_feet"] = altitude_ft
            res["cpr_frame"] = "Odd" if int(me_bits[21]) == 1 else "Even"
            res["message_type"] = "Airborne Position"

        elif type_code == 19:
            # Airborne Velocity
            subtype = int(me_bits[5:8], 2)
            if subtype in [1, 2]:
                ew_dir = int(me_bits[13])
                ew_vel = int(me_bits[14:24], 2) - 1
                ns_dir = int(me_bits[25])
                ns_vel = int(me_bits[26:36], 2) - 1

                vx = -ew_vel if ew_dir else ew_vel
                vy = -ns_vel if ns_dir else ns_vel

                speed_kts = np.sqrt(vx**2 + vy**2)
                heading_deg = (np.degrees(np.arctan2(vx, vy)) + 360) % 360
                
                res["velocity_knots"] = float(round(speed_kts, 1))
                res["heading_deg"] = float(round(heading_deg, 1))
                res["message_type"] = "Airborne Velocity"

        return res

    except Exception:
        return None
