from enum import Enum
from typing import Dict, Any

class ConfidenceTier(str, Enum):
    TIER_A = "Tier A: Fully Decoded"
    TIER_B = "Tier B: Parameters Identified, Decode Failed"
    TIER_C = "Tier C: Unknown / Insufficient Signal"

def calculate_tier(
    syndrome_zero: bool = False,
    sync_matched: bool = False,
    amc_confidence: float = 0.0,
    snr_db: float = 0.0
) -> ConfidenceTier:
    """
    Determine final confidence tier based on syndrome check, sync word correlation,
    modulation classification confidence, and estimated SNR.
    """
    if syndrome_zero and sync_matched:
        return ConfidenceTier.TIER_A
    elif amc_confidence >= 0.70 or snr_db >= 5.0:
        return ConfidenceTier.TIER_B
    else:
        return ConfidenceTier.TIER_C
