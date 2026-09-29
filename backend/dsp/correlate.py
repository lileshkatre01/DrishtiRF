"""
DrishtiRF - Bitstream Search & Frame Correlation Engine
Performs cross-correlation across bit phase rotations, phase inversions, preamble alignment,
entropy-based header/payload segmentation, and frame extraction.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

from backend.dsp.sync_library import SYNC_PATTERNS, bits_to_hex
from backend.core.explain import generate_explanation

def calculate_shannon_entropy(byte_array: bytes) -> float:
    """
    Calculate Shannon Entropy in bits per byte (0.0 to 8.0).
    """
    if len(byte_array) == 0:
        return 0.0
    counts = Counter(byte_array)
    total = len(byte_array)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * np.log2(p)
    return float(entropy)

def correlate_bitstream(
    bits_input: Any,
    sync_threshold: float = 0.80,
    default_frame_len: int = 256
) -> Dict[str, Any]:
    """
    Cross-correlates raw/decoded bitstream against standard sync word patterns.
    Resolves bit phase shifts & 180-degree phase inversions.
    Extracts frame table, headers, payloads, and rolling entropy metrics.
    """
    bits = np.asarray(bits_input, dtype=np.uint8)
    
    if len(bits) < 16:
        return {
            "sync_found": False,
            "best_sync_word": "None",
            "bit_inverted": False,
            "frame_count": 0,
            "frame_length_bits": 0,
            "confidence": 0.0,
            "frames": [],
            "explanation": "Bitstream too short for sync-word correlation."
        }

    # Bipolar representation of input bitstream: 0 -> -1, 1 -> +1
    bipolar_bits = (2 * bits.astype(float)) - 1

    best_match_info = {
        "sync_name": "None",
        "score": 0.0,
        "pattern_len": 0,
        "inverted": False,
        "offsets": [],
        "frame_len": default_frame_len
    }

    # Search across all standard sync patterns
    for name, pattern_info in SYNC_PATTERNS.items():
        pat_bits = pattern_info["bits"]
        M = len(pat_bits)
        if len(bits) < M:
            continue

        bipolar_pat = (2 * pat_bits.astype(float)) - 1

        # Compute sliding normalized cross-correlation
        corr = np.correlate(bipolar_bits, bipolar_pat, mode='valid') / M

        # Test both normal and inverted orientation
        for inverted in [False, True]:
            test_corr = -corr if inverted else corr
            
            # Require higher threshold for short patterns (M < 10) to avoid false noise matches
            effective_thresh = max(sync_threshold, 0.95) if M < 10 else sync_threshold
            peak_indices = np.where(test_corr >= effective_thresh)[0]

            if len(peak_indices) > 0:
                max_score = float(np.max(test_corr[peak_indices]))
                
                # Estimate frame length from peak periodicity if multiple peaks exist
                est_frame_len = default_frame_len
                is_periodic = False
                if len(peak_indices) > 1:
                    diffs = np.diff(peak_indices)
                    valid_diffs = diffs[diffs >= M]
                    if len(valid_diffs) > 0:
                        most_common_diff, count = Counter(valid_diffs).most_common(1)[0]
                        est_frame_len = int(most_common_diff)
                        if count >= 1:
                            is_periodic = True

                # Score combines raw correlation, pattern length significance (M), and periodicity
                # Pattern length weighting: longer patterns carry exponentially higher information content
                overall_score = max_score * (1.0 + 0.03 * M) + (0.25 if is_periodic else 0.0)

                # Update best match if score is strictly greater, or equal score with longer pattern length
                if (overall_score > best_match_info["score"] + 1e-4) or (
                    abs(overall_score - best_match_info["score"]) <= 1e-4 and M > best_match_info["pattern_len"]
                ):
                    best_match_info = {
                        "sync_name": name,
                        "score": overall_score,
                        "pattern_len": M,
                        "inverted": inverted,
                        "offsets": peak_indices.tolist(),
                        "frame_len": est_frame_len
                    }

    sync_found = best_match_info["sync_name"] != "None"
    inverted = best_match_info["inverted"]
    processed_bits = (1 - bits) if inverted else bits

    extracted_frames = []
    start_offsets = best_match_info["offsets"] if sync_found else [0]
    frame_len = best_match_info["frame_len"]

    # Limit frame extraction to max 32 frames for API payload size safety
    for idx, offset in enumerate(start_offsets[:32]):
        frame_end = min(offset + frame_len, len(processed_bits))
        frame_slice = processed_bits[offset:frame_end]
        
        byte_arr = np.packbits(frame_slice).tobytes()
        
        # Partition header (first 8 bytes / 64 bits) vs payload
        header_byte_len = min(8, len(byte_arr))
        header_bytes = byte_arr[:header_byte_len]
        payload_bytes = byte_arr[header_byte_len:]

        header_hex = header_bytes.hex()
        payload_hex = payload_bytes.hex()
        
        header_entropy = calculate_shannon_entropy(header_bytes)
        payload_entropy = calculate_shannon_entropy(payload_bytes)

        extracted_frames.append({
            "frame_index": idx,
            "offset": int(offset),
            "sync_word": best_match_info["sync_name"],
            "header_hex": header_hex,
            "payload_hex": payload_hex,
            "header_entropy": round(header_entropy, 3),
            "payload_entropy": round(payload_entropy, 3),
            "bit_inverted": inverted
        })

    confidence = min(0.99, max(0.10, best_match_info["score"] / 2.0))
    
    explanation = generate_explanation("correlation", {
        "sync_word": best_match_info["sync_name"],
        "frame_count": len(extracted_frames)
    })

    return {
        "sync_found": sync_found,
        "best_sync_word": best_match_info["sync_name"],
        "bit_inverted": inverted,
        "frame_count": len(extracted_frames),
        "frame_length_bits": frame_len,
        "confidence": float(confidence),
        "frames": extracted_frames,
        "explanation": explanation
    }
