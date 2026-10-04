"""
DrishtiRF - Defense-Grade Test Signal & Ground-Truth Generator
Generates synthetic .wav and .iq files with embedded known payloads for ground-truth verification.
Run: python generate_test_signals.py
"""

import os
import json
import wave
import numpy as np

OUTPUT_DIR = "test_signals"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 1000000.0   # 1 MHz
SYMBOL_RATE = 50000.0     # 50 kbaud (20 samples per symbol)
SAMPLES_PER_SYM = int(SAMPLE_RATE / SYMBOL_RATE)

print("=" * 60)
print("  DrishtiRF Ground-Truth & Test Signal Generator (SIH 2026)")
print("=" * 60)

# Helper: Viterbi Convolutional Encoder (Rate 1/2, K=7, poly=[171, 133])
def encode_viterbi_r12_k7(bits: np.ndarray) -> np.ndarray:
    poly1 = [1, 1, 1, 1, 0, 0, 1]  # 171 octal
    poly2 = [1, 0, 1, 1, 0, 1, 1]  # 133 octal
    K = 7
    shift_reg = np.zeros(K, dtype=np.uint8)
    encoded = []
    
    for bit in bits:
        shift_reg[1:] = shift_reg[:-1]
        shift_reg[0] = bit
        g1 = np.sum(shift_reg * poly1) % 2
        g2 = np.sum(shift_reg * poly2) % 2
        encoded.extend([g1, g2])
        
    return np.array(encoded, dtype=np.uint8)

# ── 1. Verified BPSK Signal with Known Text Payload + Viterbi ─
def gen_verified_bpsk(filename, text_msg="NTRO-MISSION-2026"):
    # Convert ASCII text to bits
    msg_bytes = text_msg.encode('utf-8')
    raw_bits = np.unpackbits(np.frombuffer(msg_bytes, dtype=np.uint8))
    
    # Barker-13 Sync Word: 1111100110101
    barker13 = np.array([1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1], dtype=np.uint8)
    frame_bits = np.concatenate([barker13, raw_bits])
    
    # Convolutional Encode
    fec_bits = encode_viterbi_r12_k7(frame_bits)
    
    # Repeat frames for multi-frame packet stream
    stream_bits = np.tile(fec_bits, 4)
    
    # BPSK Modulation: bit 0 -> +1, bit 1 -> -1
    symbols = 1.0 - 2.0 * stream_bits.astype(np.float32)
    
    # Pulse Shaping / Upsampling
    tx_samples = np.repeat(symbols, SAMPLES_PER_SYM)
    
    # Add AWGN channel noise (SNR = 18 dB)
    snr_linear = 10.0 ** (18.0 / 10.0)
    noise_sigma = 1.0 / np.sqrt(2.0 * snr_linear)
    noise = (np.random.normal(0, noise_sigma, len(tx_samples)) + 1j * np.random.normal(0, noise_sigma, len(tx_samples))).astype(np.complex64)
    
    iq_samples = tx_samples.astype(np.complex64) + noise
    
    # Write interleaved float32 IQ
    interleaved = np.empty(2 * len(iq_samples), dtype=np.float32)
    interleaved[0::2] = np.real(iq_samples)
    interleaved[1::2] = np.imag(iq_samples)
    interleaved.tofile(filename)
    
    # Write metadata sidecar
    meta = {
        "ground_truth_mod": "BPSK",
        "format": "cf32",
        "sample_rate": SAMPLE_RATE,
        "symbol_rate": SYMBOL_RATE,
        "payload_text": text_msg,
        "sync_word": "Barker-13",
        "fec": "Viterbi (Rate 1/2, K=7)",
        "expected_tier": "TIER_A"
    }
    with open(f"{filename}.json", "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"  [OK] Verified BPSK IQ  -> {filename} (Payload: '{text_msg}')")

# ── 2. Verified 2FSK Signal with Telemetry Payload ────────────
def gen_verified_2fsk(filename, text_msg="DRISHTIRF-PKT#01"):
    msg_bytes = text_msg.encode('utf-8')
    raw_bits = np.unpackbits(np.frombuffer(msg_bytes, dtype=np.uint8))
    
    # Barker-13 Sync Word
    barker13 = np.array([1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1], dtype=np.uint8)
    frame_bits = np.concatenate([barker13, raw_bits])
    stream_bits = np.tile(frame_bits, 4)
    
    # 2FSK Continuous Phase Frequency Modulation (CPFSK)
    f_dev = 50000.0  # 50 kHz frequency deviation (standard 2FSK tone separation)
    t_step = 1.0 / SAMPLE_RATE
    freqs = np.repeat(np.where(stream_bits == 1, f_dev, -f_dev), SAMPLES_PER_SYM)
    phase = np.cumsum(2.0 * np.pi * freqs * t_step)
    
    tx_samples = np.exp(1j * phase).astype(np.complex64)
    
    # Add noise (SNR = 20 dB)
    snr_linear = 10.0 ** (20.0 / 10.0)
    noise_sigma = 1.0 / np.sqrt(2.0 * snr_linear)
    noise = (np.random.normal(0, noise_sigma, len(tx_samples)) + 1j * np.random.normal(0, noise_sigma, len(tx_samples))).astype(np.complex64)
    iq_samples = tx_samples + noise
    
    interleaved = np.empty(2 * len(iq_samples), dtype=np.float32)
    interleaved[0::2] = np.real(iq_samples)
    interleaved[1::2] = np.imag(iq_samples)
    interleaved.tofile(filename)
    
    meta = {
        "ground_truth_mod": "2FSK",
        "format": "cf32",
        "sample_rate": SAMPLE_RATE,
        "symbol_rate": SYMBOL_RATE,
        "payload_text": text_msg,
        "sync_word": "Barker-13",
        "fec": "None",
        "expected_tier": "TIER_A"
    }
    with open(f"{filename}.json", "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"  [OK] Verified 2FSK IQ  -> {filename} (Payload: '{text_msg}')")

# ── 3. Analog AM WAV Audio Signal ────────────────────────────
def gen_am_wav(filename):
    audio_fs = 48000
    duration = 3.0
    N = int(audio_fs * duration)
    t = np.linspace(0, duration, N, endpoint=False)
    
    carrier = np.cos(2 * np.pi * 5000 * t)         # 5 kHz RF Carrier
    audio_msg = 0.6 * np.cos(2 * np.pi * 400 * t)  # 400 Hz Audio Tone
    am_signal = (1.0 + audio_msg) * carrier
    
    am_int16 = np.int16(am_signal / np.max(np.abs(am_signal)) * 32767)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(audio_fs)
        wf.writeframes(am_int16.tobytes())
        
    print(f"  [OK] Analog AM Audio   -> {filename}")

# ── 4. Low SNR Pure Gaussian Noise (Adversarial UNKNOWN test) ─
def gen_noise_file(filename):
    N = 40000
    noise = (np.random.normal(0, 1, N) + 1j * np.random.normal(0, 1, N)).astype(np.complex64)
    interleaved = np.empty(2 * N, dtype=np.float32)
    interleaved[0::2] = np.real(noise)
    interleaved[1::2] = np.imag(noise)
    interleaved.tofile(filename)
    
    meta = {
        "ground_truth_mod": "UNKNOWN / NOISE",
        "format": "cf32",
        "sample_rate": SAMPLE_RATE,
        "expected_tier": "TIER_C"
    }
    with open(f"{filename}.json", "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"  [OK] Low-SNR Noise IQ  -> {filename} (Expected: UNKNOWN / Tier C)")

# ── Generate All ──────────────────────────────────────────────
gen_verified_bpsk(os.path.join(OUTPUT_DIR, "verified_bpsk_signal.iq"))
gen_verified_2fsk(os.path.join(OUTPUT_DIR, "verified_2fsk_signal.iq"))
gen_am_wav(os.path.join(OUTPUT_DIR, "test_am_signal.wav"))
gen_noise_file(os.path.join(OUTPUT_DIR, "noise_low_snr_unknown.iq"))

print()
print("=" * 60)
print(f"All ground-truth test signals generated in: ./{OUTPUT_DIR}/")
print("=" * 60)
