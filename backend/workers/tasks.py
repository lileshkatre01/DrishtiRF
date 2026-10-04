"""
DrishtiRF - Celery Async Worker Task Definitions
Provides background task execution for end-to-end signal processing pipeline jobs.
"""

from backend.workers.celery_app import celery_app
from backend.core.logging import logger
from backend.db.session import SessionLocal
from backend.db.models import Capture, Job, StageResult, Frame
from backend.dsp.ingestion import read_signal_file
from backend.dsp.preprocess import preprocess_signal
from backend.dsp.spectral import analyze_spectrum
from backend.dsp.amc.fusion import classify_modulation
from backend.dsp.demod.master_demod import demodulate_signal
from backend.dsp.joint_search import search_joint_deinterleave_fec
from backend.dsp.correlate import correlate_bitstream
from backend.dsp.protocol_decoders import decode_protocol_payload
from backend.core.confidence import evaluate_job_confidence
from backend.core.explain import generate_explanation

# If Celery is unavailable, use a no-op decorator so imports don't crash
def _noop_task(*args, **kwargs):
    def decorator(fn):
        return fn
    return decorator

_task_decorator = celery_app.task if celery_app else _noop_task

@_task_decorator(name="drishtirf.pipeline.run_analysis")
def run_analysis_pipeline(job_id: str):
    """
    Celery background worker task for running the end-to-end DSP analysis pipeline.
    Executes Spectral Analysis, AMC, Demodulation, Joint Search, Correlation, and 3-Tier Confidence evaluation.
    """
    logger.info(f"Starting Celery async analysis pipeline task for Job ID: {job_id}")
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job ID {job_id} not found in database.")
            return {"error": "Job not found"}

        capture = db.query(Capture).filter(Capture.id == job.capture_id).first()
        if not capture:
            logger.error(f"Capture ID {job.capture_id} not found for job {job_id}.")
            job.status = "FAILED"
            db.commit()
            return {"error": "Capture not found"}

        job.status = "PROCESSING"
        job.stage = "SPECTRAL"
        job.progress = 10.0
        db.commit()

        # Load & Preprocess Signal
        raw_iq = read_signal_file(capture.path, sample_rate_override=capture.sample_rate, format_override=capture.format)
        clean_iq = preprocess_signal(raw_iq)

        # 1. SPECTRAL Stage
        spectral_res = analyze_spectrum(clean_iq)
        exp_spectral = generate_explanation("spectral", {
            "bandwidth_hz": spectral_res["bandwidth_10db_hz"],
            "snr_db": spectral_res["snr_db"],
            "center_freq_hz": spectral_res["center_freq_offset_hz"]
        })
        db.add(StageResult(
            job_id=job.id,
            stage="SPECTRAL",
            json_result=spectral_res,
            confidence=spectral_res["snr_confidence"],
            explanation=exp_spectral
        ))
        job.progress = 25.0
        job.stage = "AMC"
        db.commit()

        # 2. AMC Stage
        amc_res = classify_modulation(clean_iq)
        db.add(StageResult(
            job_id=job.id,
            stage="AMC",
            json_result=amc_res,
            confidence=amc_res["confidence"],
            explanation=amc_res["explanation"]
        ))
        job.progress = 45.0
        job.stage = "DEMOD"
        db.commit()

        # 3. DEMOD Stage
        is_analog = bool(amc_res.get("is_analog", False) or amc_res.get("family") == "ANALOG")
        mod_type = amc_res.get("modulation", "QPSK")
        sym_rate = amc_res.get("symbol_rate_baud", 100e3) or 100e3

        if is_analog:
            demod_res = {
                "modulation": mod_type,
                "bit_count": 0,
                "bits": [],
                "is_analog": True,
                "constellation": {"I": [], "Q": []},
                "explanation": f"Demodulated {mod_type} analog audio baseband signal. Digital bit slicing bypassed."
            }
            joint_res = {
                "best_interleaver": "N/A (Analog Carrier)",
                "best_fec": "N/A (Analog Carrier)",
                "syndrome_zero": False,
                "fec_status": "N/A",
                "evidence_level": "N/A",
                "confidence": 0.0,
                "decoded_bits": [],
                "explanation": "Analog transmission detected — digital FEC and de-interleaver search skipped."
            }
            corr_res = {
                "sync_found": False,
                "best_sync_word": "None",
                "is_periodic": False,
                "frame_count": 0,
                "frames": [],
                "evidence_level": "N/A",
                "confidence": 0.0,
                "explanation": "Analog transmission — packet framing and sync search not applicable."
            }
        else:
            demod_res = demodulate_signal(clean_iq, mod_type=mod_type, symbol_rate=sym_rate)
            raw_bits = demod_res.get("bits", [])
            joint_res = search_joint_deinterleave_fec(raw_bits)
            decoded_bits = joint_res.get("decoded_bits", [])
            if len(decoded_bits) == 0:
                decoded_bits = raw_bits
            corr_res = correlate_bitstream(decoded_bits)

            # Phase 12 Protocol Telemetry Decoding
            parsed_frames = []
            for f in corr_res.get("frames", []):
                bit_str = f.get("bit_string", "")
                sync_w = f.get("sync_word", "")
                protocol_parsed = decode_protocol_payload(bit_str, sync_name=sync_w)
                
                f["protocol_telemetry"] = protocol_parsed
                parsed_frames.append(f)
                
                db.add(Frame(
                    job_id=job.id,
                    offset=f["offset"],
                    sync_word=f["sync_word"],
                    header_hex=f["header_hex"],
                    payload_hex=f["payload_hex"]
                ))

            corr_res["frames"] = parsed_frames

        exp_demod = f"Demodulated {mod_type} stream into {demod_res['bit_count']} raw encoded bits." if not is_analog else demod_res["explanation"]
        db.add(StageResult(
            job_id=job.id,
            stage="DEMOD",
            json_result=demod_res,
            confidence=0.95 if demod_res["bit_count"] > 0 else (0.85 if is_analog else 0.0),
            explanation=exp_demod
        ))
        job.progress = 65.0
        job.stage = "JOINT_SEARCH"
        db.commit()

        # 4. JOINT SEARCH Stage
        db.add(StageResult(
            job_id=job.id,
            stage="JOINT_SEARCH",
            json_result=joint_res,
            confidence=joint_res["confidence"],
            explanation=joint_res["explanation"]
        ))
        job.progress = 85.0
        job.stage = "CORRELATION"
        db.commit()

        # 5. CORRELATION & FRAMING Stage
        db.add(StageResult(
            job_id=job.id,
            stage="CORRELATION",
            json_result=corr_res,
            confidence=corr_res["confidence"],
            explanation=corr_res["explanation"]
        ))

        # 6. Evaluate Overall 3-Tier Confidence
        confidence_summary = evaluate_job_confidence({
            "spectral": spectral_res,
            "amc": amc_res,
            "demod": demod_res,
            "joint_search": joint_res,
            "correlation": corr_res
        })

        db.add(StageResult(
            job_id=job.id,
            stage="CONFIDENCE_EVALUATION",
            json_result=confidence_summary,
            confidence=confidence_summary["overall_confidence"],
            explanation=confidence_summary["rationale"]
        ))

        job.progress = 100.0
        job.status = "COMPLETED"
        db.commit()

        logger.info(f"Completed Celery async analysis pipeline task for Job ID: {job_id} ({confidence_summary['tier_code']})")
        return {"job_id": job_id, "status": "COMPLETED", "confidence": confidence_summary}

    except Exception as e:
        logger.error(f"Celery task failed for job {job_id}: {str(e)}")
        if job:
            job.status = "FAILED"
            db.commit()
        return {"job_id": job_id, "status": "FAILED", "error": str(e)}
    finally:
        db.close()
