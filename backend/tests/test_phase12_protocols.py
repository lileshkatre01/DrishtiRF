import pytest
import numpy as np

from backend.dsp.protocol_decoders.ais import decode_ais_payload
from backend.dsp.protocol_decoders.adsb import decode_adsb_payload
from backend.dsp.protocol_decoders.dmr import decode_dmr_payload
from backend.dsp.protocol_decoders.telemetry import decode_satellite_telemetry
from backend.dsp.protocol_decoders.master_protocol import decode_protocol_payload
from backend.dsp.acceleration import fast_fft_psd, fast_hamming_correlation, estimate_acceleration_metrics

def test_ais_maritime_decoder():
    # 168-bit synthetic AIS Type 1 Position Report bitstring
    type_bits = "000001"  # Type 1
    repeat = "00"
    mmsi_bits = f"{366999123:030b}"  # MMSI 366999123
    nav_status = "0000"  # Under way using engine
    rot = "00000000"
    sog = f"{125:010b}"  # 12.5 knots
    accuracy = "1"
    lon = f"{int(-122.3320 * 600000) & (2**28 - 1):028b}"
    lat = f"{int(47.6062 * 600000) & (2**27 - 1):027b}"
    cog = f"{1800:012b}"  # 180.0 deg
    heading = f"{180:09b}"
    
    ais_bitstring = (type_bits + repeat + mmsi_bits + nav_status + rot + sog + accuracy + lon + lat + cog + heading).ljust(168, '0')
    assert len(ais_bitstring) >= 168
    
    res = decode_ais_payload(ais_bitstring)
    assert res is not None
    assert res["protocol"] == "AIS"
    assert res["mmsi"] == 366999123
    assert res["speed_over_ground_knots"] == 12.5
    assert abs(res["longitude"] - (-122.3320)) < 0.01
    assert abs(res["latitude"] - 47.6062) < 0.01

def test_adsb_aviation_decoder():
    # 112-bit ADS-B DF17 Callsign Extended Squitter bitstring
    df_bits = f"{17:05b}"
    ca_bits = "101"
    icao_bits = f"{0xABCD12:024b}"
    # Callsign "AAL123" ME payload
    me_bits = f"{1:05b}" + f"{1:03b}" + f"{1:06b}" + f"{1:06b}" + f"{12:06b}" + f"{49:06b}" + f"{50:06b}" + f"{51:06b}" + "000000"
    me_bits = me_bits.ljust(56, '0')
    crc_bits = "0" * 24
    
    adsb_bitstring = df_bits + ca_bits + icao_bits + me_bits + crc_bits
    assert len(adsb_bitstring) == 112
    
    res = decode_adsb_payload(adsb_bitstring)
    assert res is not None
    assert res["protocol"] == "ADS-B"
    assert res["icao_address"] == "0xABCD12"

def test_dmr_radio_decoder():
    # DMR 4FSK bitstring with Voice Sync
    from backend.dsp.protocol_decoders.dmr import DMR_VOICE_SYNC
    dmr_bits = "0001" + "0" * 24 + "0" * 24 + DMR_VOICE_SYNC + "0" * 50
    res = decode_dmr_payload(dmr_bits)
    assert res is not None
    assert res["protocol"] == "DMR"
    assert res["burst_sync"] == "Voice Sync"

def test_satellite_telemetry_decoder():
    # CCSDS 48-bit header
    version = "000"
    type_f = "0"
    sec_h = "1"
    apid = f"{0x1A2:011b}"
    seq_f = "11"
    seq_c = f"{1024:014b}"
    pkt_len = f"{127:016b}"
    
    ccsds_bits = version + type_f + sec_h + apid + seq_f + seq_c + pkt_len
    res = decode_satellite_telemetry(ccsds_bits)
    assert res is not None
    assert res["protocol"] == "CCSDS / AX.25 Satellite Telemetry"
    assert res["apid"] == "0x1A2 (418)"
    assert res["sequence_counter"] == 1024

def test_master_protocol_router():
    ais_str = "000001" + "0"*165
    res = decode_protocol_payload(ais_str, sync_name="AIS_SYNC")
    assert res["decoded"] is True
    assert res["protocol"] == "AIS"

def test_dsp_acceleration_engine():
    samples = (np.random.normal(0, 1, 4096) + 1j * np.random.normal(0, 1, 4096)).astype(np.complex64)
    freqs, psd = fast_fft_psd(samples, fs=1e6)
    
    assert len(freqs) == 1024
    assert len(psd) == 1024
    
    arr_a = np.array([1, 0, 1, 1, 0, 1])
    arr_b = np.array([1, 0, 1])
    h_dist = fast_hamming_correlation(arr_a, arr_b)
    assert len(h_dist) == 4
    
    metrics = estimate_acceleration_metrics(4096, 1e6)
    assert metrics["throughput_msps"] == 1.0
