import numpy as np
from typing import Dict, Any, Optional, List

from backend.dsp.deinterleave.block import deinterleave_block, search_block_interleaver
from backend.dsp.deinterleave.convolutional import deinterleave_conv, search_conv_interleaver
from backend.dsp.deinterleave.diagonal import deinterleave_diagonal
from backend.dsp.deinterleave.pseudo_random import deinterleave_pseudo_random, search_pseudo_random_interleaver
from backend.dsp.fec.viterbi import decode_viterbi
from backend.dsp.fec.reed_solomon import decode_reed_solomon
from backend.dsp.fec.concatenated import decode_concatenated
from backend.dsp.fec.ldpc import decode_ldpc
from backend.core.explain import generate_explanation


def search_joint_deinterleave_fec(bits_input: Any, soft_symbols: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """
    Core Novelty Joint Search Engine:
    Jointly enumerates and scores (Interleaver Type x Params) x (FEC Scheme x Params) hypotheses.
    Prunes candidates by entropy drop & ranks winners by syndrome zero-rate / decode path metrics.
    """
    bits = np.asarray(bits_input, dtype=np.uint8)

    if len(bits) < 16:
        return {
            "best_interleaver": "None",
            "best_fec": "None",
            "decoded_bits": bits.tolist(),
            "syndrome_zero": False,
            "confidence": 0.0,
            "explanation": "Bitstream too short for joint de-interleaver and FEC search"
        }

    # Limit bit evaluation window to max 1024 bits for fast hypothesis testing
    search_bits = bits[:1024] if len(bits) > 1024 else bits

    # 1. Discover potential interleaver candidates
    interleaver_candidates = [("None", {})]

    # Test Block interleaver
    r_opt, c_opt, block_score = search_block_interleaver(search_bits)
    if block_score > 0.55:
        interleaver_candidates.append(("Block", {"rows": r_opt, "cols": c_opt}))

    # Test Convolutional interleaver
    d_opt, m_opt, conv_score = search_conv_interleaver(search_bits)
    if conv_score > 0.55:
        interleaver_candidates.append(("Convolutional", {"depth": d_opt, "span": m_opt}))

    # Test Pseudo-Random interleaver (NEW — was previously missing)
    pr_seed, pr_block, pr_score = search_pseudo_random_interleaver(search_bits)
    if pr_score > 0.05:
        interleaver_candidates.append(("PseudoRandom", {"seed": pr_seed, "block_size": pr_block}))

    # Default fallback matrix candidates
    interleaver_candidates.append(("Block", {"rows": 8, "cols": 16}))
    interleaver_candidates.append(("Diagonal", {"rows": 8, "cols": 16}))

    # 2. Joint Search Loop across (Interleaver Candidate x FEC Candidate)
    best_score = -1.0
    best_payload = search_bits
    best_syndrome_zero = False
    best_interleaver_name = "None"
    best_fec_name = "None"

    fec_schemes = ["None", "Viterbi (Rate 1/2, K=7)", "Reed-Solomon RS(255,223)", "Concatenated RS+Viterbi", "LDPC (Rate 1/2)"]

    for ileav_type, ileav_params in interleaver_candidates:
        # Apply candidate de-interleaver
        if ileav_type == "Block":
            deint_bits = deinterleave_block(search_bits, ileav_params.get("rows", 8), ileav_params.get("cols", 16))
            ileav_str = f"Block ({ileav_params.get('rows', 8)}x{ileav_params.get('cols', 16)})"
        elif ileav_type == "Convolutional":
            deint_bits = deinterleave_conv(search_bits, ileav_params.get("depth", 4), ileav_params.get("span", 2))
            ileav_str = f"Convolutional (Depth {ileav_params.get('depth', 4)}, Span {ileav_params.get('span', 2)})"
        elif ileav_type == "Diagonal":
            deint_bits = deinterleave_diagonal(search_bits, ileav_params.get("rows", 8), ileav_params.get("cols", 16))
            ileav_str = f"Diagonal ({ileav_params.get('rows', 8)}x{ileav_params.get('cols', 16)})"
        elif ileav_type == "PseudoRandom":
            deint_bits = deinterleave_pseudo_random(search_bits, seed=ileav_params.get("seed", 42), block_size=ileav_params.get("block_size", 64))
            ileav_str = f"PseudoRandom (Seed={ileav_params.get('seed', 42)}, Block={ileav_params.get('block_size', 64)})"
        else:
            deint_bits = search_bits
            ileav_str = "None"

        # Evaluate candidate FEC decoders
        for fec in fec_schemes:
            if fec == "Viterbi (Rate 1/2, K=7)":
                payload, score = decode_viterbi(deint_bits, rate="1/2", K=7)
                syn_zero = score > 0.85
            elif fec == "Reed-Solomon RS(255,223)":
                payload, syn_zero, err_count = decode_reed_solomon(deint_bits, n=255, k=223)
                score = 0.95 if syn_zero else 0.40
            elif fec == "Concatenated RS+Viterbi":
                payload, syn_zero, score = decode_concatenated(deint_bits)
            elif fec == "LDPC (Rate 1/2)":
                payload, syn_zero, score = decode_ldpc(deint_bits, rate="1/2")
            else:
                payload = deint_bits
                syn_zero = False
                score = 0.30

            if syn_zero:
                score += 0.50

            if score > best_score:
                best_score = score
                best_payload = payload
                best_syndrome_zero = syn_zero
                best_interleaver_name = ileav_str
                best_fec_name = fec

    final_confidence = min(0.99, max(0.20, best_score / 1.50))
    explanation = generate_explanation("joint_search", {
        "interleaver": best_interleaver_name,
        "fec": best_fec_name,
        "success": best_syndrome_zero
    })

    byte_payload = np.packbits(best_payload) if len(best_payload) > 0 else np.array([], dtype=np.uint8)
    hex_payload = byte_payload[:64].tobytes().hex()

    return {
        "best_interleaver": best_interleaver_name,
        "best_fec": best_fec_name,
        "syndrome_zero": best_syndrome_zero,
        "confidence": float(final_confidence),
        "payload_bit_count": len(best_payload),
        "payload_hex_preview": hex_payload,
        "decoded_bits": best_payload.tolist(),
        "explanation": explanation
    }
