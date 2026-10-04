"""
DrishtiRF - Domain Test Signal Generator
Generates synthetic sample .IQ files for all 5 target domains:
1. Aviation (ADS-B Transponder 1090 MHz)
2. Maritime (AIS Ship Positioning 162 MHz)
3. Drone / UAV (MAVLink Telemetry)
4. Satellite (NOAA Weather APT)
5. Tactical Defense (P25 Military Radio)
"""

import os
import numpy as np

# Ensure sample_data output directory exists
OUTPUT_DIR = os.path.join(os.path.dirname(__file__))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_iq_file(filename: str, preamble_bits: np.ndarray, mod_type: str = "2fsk", sample_rate: float = 1e6, symbol_rate: float = 100e3, freq_offset_hz: float = 0.0, snr_db: float = 20.0):
    """
    Generates a synthetic complex IQ binary signal (.iq) containing a specific preamble bit pattern,
    modulation type, and unique spectral frequency offset.
    """
    # Create payload bits (Preamble + Random Payload + Preamble + Random Payload)
    payload_bits = np.random.randint(0, 2, size=256, dtype=np.uint8)
    frame = np.concatenate([preamble_bits, payload_bits])
    bit_stream = np.tile(frame, 6)

    sps = int(sample_rate / symbol_rate)
    n_samples = len(bit_stream) * sps
    t = np.arange(n_samples) / sample_rate

    # Generate IQ waveform based on modulation type
    if mod_type == "2fsk":
        # Frequency Shift Keying
        freq_dev = symbol_rate * 0.5
        expanded_bits = np.repeat(bit_stream, sps)
        freq_inst = (2 * expanded_bits - 1) * freq_dev
        phase = 2 * np.pi * np.cumsum(freq_inst) / sample_rate
        iq = np.exp(1j * phase)

    elif mod_type == "qpsk":
        # Quadrature Phase Shift Keying
        if len(bit_stream) % 2 != 0:
            bit_stream = np.append(bit_stream, 0)
        i_bits = (2 * bit_stream[0::2] - 1)
        q_bits = (2 * bit_stream[1::2] - 1)
        i_upsampled = np.repeat(i_bits, sps * 2)
        q_upsampled = np.repeat(q_bits, sps * 2)
        iq = (i_upsampled + 1j * q_upsampled) / np.sqrt(2)
        if len(iq) > n_samples:
            iq = iq[:n_samples]

    else:
        # BPSK
        bipolar = (2 * bit_stream - 1)
        bipolar_upsampled = np.repeat(bipolar, sps)
        iq = bipolar_upsampled + 0j

    # Apply Carrier Frequency Offset (CFO)
    if freq_offset_hz != 0.0:
        cfo_rotator = np.exp(1j * 2 * np.pi * freq_offset_hz * t[:len(iq)])
        iq = iq * cfo_rotator

    # Add Gaussian Noise for realistic SNR
    signal_power = np.mean(np.abs(iq)**2)
    noise_power = signal_power / (10 ** (snr_db / 10.0))
    noise = (np.random.normal(0, np.sqrt(noise_power / 2), size=len(iq)) + 
             1j * np.random.normal(0, np.sqrt(noise_power / 2), size=len(iq)))
    
    clean_iq = (iq + noise).astype(np.complex64)

    # Convert complex float32 to cs16 (interleaved int16)
    i_int16 = np.clip(np.real(clean_iq) * 32767.0, -32768, 32767).astype(np.int16)
    q_int16 = np.clip(np.imag(clean_iq) * 32767.0, -32768, 32767).astype(np.int16)

    interleaved = np.empty(2 * len(clean_iq), dtype=np.int16)
    interleaved[0::2] = i_int16
    interleaved[1::2] = q_int16

    filepath = os.path.join(OUTPUT_DIR, filename)
    interleaved.tofile(filepath)

    # Save sidecar metadata JSON
    meta_json = {
        "filename": filename,
        "sample_rate": sample_rate,
        "center_freq": 1090e6 if "aviation" in filename else (162e6 if "maritime" in filename else 433e6),
        "format": "cs16",
        "adc_bits": 16,
        "num_samples": len(clean_iq)
    }
    with open(filepath + ".json", "w") as f:
        import json
        json.dump(meta_json, f, indent=2)

    print(f"Generated {filename} ({len(interleaved)} bytes)")

if __name__ == "__main__":
    # 1. Aviation ADS-B (Preamble 0x8D, Offset +45 kHz, BW ~150 kHz)
    adsb_preamble = np.array([1, 0, 0, 0, 1, 1, 0, 1], dtype=np.uint8)
    generate_iq_file("aviation_adsb_1090mhz_fs1M_cs16.iq", adsb_preamble, mod_type="2fsk", symbol_rate=120e3, freq_offset_hz=45e3, snr_db=18.0)

    # 2. Maritime AIS (Preamble 0x7E, Offset -25 kHz, BW ~50 kHz)
    ais_preamble = np.array([0, 1, 1, 1, 1, 1, 1, 0], dtype=np.uint8)
    generate_iq_file("maritime_ais_162mhz_fs1M_cs16.iq", ais_preamble, mod_type="2fsk", symbol_rate=50e3, freq_offset_hz=-25e3, snr_db=20.0)

    # 3. Drone MAVLink (Preamble 0xFE, Offset +15 kHz, BW ~100 kHz)
    mavlink_preamble = np.array([1, 1, 1, 1, 1, 1, 1, 0], dtype=np.uint8)
    generate_iq_file("drone_mavlink_telemetry_fs1M_cs16.iq", mavlink_preamble, mod_type="2fsk", symbol_rate=80e3, freq_offset_hz=15e3, snr_db=22.0)

    # 4. Satellite NOAA (Preamble 0x2A, Offset -60 kHz, Wide QPSK)
    noaa_preamble = np.array([0, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8)
    generate_iq_file("satellite_noaa_apt_fs1M_cs16.iq", noaa_preamble, mod_type="qpsk", symbol_rate=160e3, freq_offset_hz=-60e3, snr_db=16.0)

    # 5. Tactical P25 Defense (Preamble 0x755E, Offset +80 kHz, 2FSK)
    p25_preamble = np.array([0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0], dtype=np.uint8)
    generate_iq_file("tactical_p25_military_radio_fs1M_cs16.iq", p25_preamble, mod_type="2fsk", symbol_rate=60e3, freq_offset_hz=80e3, snr_db=19.0)
