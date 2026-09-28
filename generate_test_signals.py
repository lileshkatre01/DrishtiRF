"""
DrishtiRF - Test Signal Generator
Generates synthetic .wav and .iq files for testing the upload pipeline.
Run: python generate_test_signals.py
"""

import numpy as np
import wave
import struct
import os

OUTPUT_DIR = "test_signals"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 48000   # 48 kHz
DURATION    = 5       # seconds
N           = SAMPLE_RATE * DURATION

print("=" * 50)
print("  DrishtiRF Test Signal Generator")
print("=" * 50)

# ── 1. AM-modulated WAV ──────────────────────────────
def gen_am_wav(filename):
    t = np.linspace(0, DURATION, N, endpoint=False)
    carrier   = np.cos(2 * np.pi * 5000 * t)          # 5 kHz carrier
    message   = 0.5 * np.cos(2 * np.pi * 300 * t)     # 300 Hz audio tone
    am_signal = (1 + message) * carrier                # AM modulation

    # Normalize to 16-bit PCM
    am_int16 = np.int16(am_signal / np.max(np.abs(am_signal)) * 32767)

    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)          # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(am_int16.tobytes())

    print(f"  [✓] WAV (AM)  → {filename}")

# ── 2. FM-modulated WAV ──────────────────────────────
def gen_fm_wav(filename):
    t         = np.linspace(0, DURATION, N, endpoint=False)
    fc        = 10000   # 10 kHz carrier
    kf        = 2000    # frequency deviation
    fm        = 400     # message frequency (Hz)
    message   = np.cos(2 * np.pi * fm * t)
    phase     = 2 * np.pi * fc * t + (kf / fm) * np.sin(2 * np.pi * fm * t)
    fm_signal = np.cos(phase)

    fm_int16 = np.int16(fm_signal / np.max(np.abs(fm_signal)) * 32767)

    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(fm_int16.tobytes())

    print(f"  [✓] WAV (FM)  → {filename}")

# ── 3. Raw IQ file (interleaved float32 I/Q samples) ─
def gen_iq_file(filename):
    t         = np.linspace(0, DURATION, N, endpoint=False)
    fc        = 1000    # baseband offset
    # BPSK-like: switch phase every 1000 samples
    bits      = np.repeat(np.random.choice([-1, 1], N // 1000), 1000)[:N]
    I         = bits * np.cos(2 * np.pi * fc * t)
    Q         = bits * np.sin(2 * np.pi * fc * t)

    # Interleave I and Q as float32
    iq = np.empty(2 * N, dtype=np.float32)
    iq[0::2] = I.astype(np.float32)
    iq[1::2] = Q.astype(np.float32)
    iq.tofile(filename)

    print(f"  [✓] IQ (BPSK) → {filename}")

# ── Generate all files ────────────────────────────────
gen_am_wav(os.path.join(OUTPUT_DIR, "test_am_signal.wav"))
gen_fm_wav(os.path.join(OUTPUT_DIR, "test_fm_signal.wav"))
gen_iq_file(os.path.join(OUTPUT_DIR, "test_bpsk_signal.iq"))

print()
print(f"All files saved to: ./{OUTPUT_DIR}/")
print("Upload any of these to DrishtiRF to test the pipeline!")
print("=" * 50)
