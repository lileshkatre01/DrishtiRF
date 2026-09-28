from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.api.deps import get_db
from backend.api.schemas import JobOut, JobCreate, StageResultOut
from backend.core.explain import generate_explanation
from backend.core.logging import logger
from backend.db.models import Capture, Job, StageResult
from backend.dsp.ingestion import read_signal_file
from backend.dsp.preprocess import preprocess_signal
from backend.dsp.spectral import analyze_spectrum
from backend.dsp.amc.fusion import classify_modulation

router = APIRouter(tags=["Analysis & Results"])

@router.get("/captures/{capture_id}/spectrum")
def get_capture_spectrum(capture_id: str, db: Session = Depends(get_db)):
    """
    Get Welch PSD, decimated time-frequency waterfall, Bandwidth (-3dB/-10dB/99%), SNR, and Center Frequency Offset.
    """
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")

    try:
        raw_iq = read_signal_file(
            capture.path,
            sample_rate_override=capture.sample_rate,
            center_freq_override=capture.center_freq,
            format_override=capture.format
        )
        clean_iq = preprocess_signal(raw_iq)
        spectral_data = analyze_spectrum(clean_iq)
    except Exception as e:
        logger.error(f"Failed to analyze spectrum for capture {capture_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Spectral analysis error: {str(e)}")

    return spectral_data

@router.post("/jobs", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """
    Start a new pipeline analysis job for an uploaded signal capture.
    Executes Spectral Analysis and Automatic Modulation Classification (AMC).
    """
    capture = db.query(Capture).filter(Capture.id == job_in.capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")

    job = Job(
        capture_id=capture.id,
        status="PROCESSING",
        stage="SPECTRAL",
        progress=10.0
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        raw_iq = read_signal_file(capture.path, sample_rate_override=capture.sample_rate, format_override=capture.format)
        clean_iq = preprocess_signal(raw_iq)
        
        # 1. Spectral Stage
        spectral_res = analyze_spectrum(clean_iq)
        explanation_spectral = generate_explanation("spectral", {
            "bandwidth_hz": spectral_res["bandwidth_10db_hz"],
            "snr_db": spectral_res["snr_db"],
            "center_freq_hz": spectral_res["center_freq_offset_hz"]
        })

        stage_spectral = StageResult(
            job_id=job.id,
            stage="SPECTRAL",
            json_result=spectral_res,
            confidence=spectral_res["snr_confidence"],
            explanation=explanation_spectral
        )
        db.add(stage_spectral)
        job.progress = 40.0
        job.stage = "AMC"

        # 2. AMC Stage
        amc_res = classify_modulation(clean_iq)
        stage_amc = StageResult(
            job_id=job.id,
            stage="AMC",
            json_result=amc_res,
            confidence=amc_res["confidence"],
            explanation=amc_res["explanation"]
        )
        db.add(stage_amc)
        job.progress = 60.0
        job.status = "COMPLETED"
        db.commit()
        db.refresh(job)

    except Exception as e:
        logger.error(f"Job execution failed for job {job.id}: {str(e)}")
        job.status = "FAILED"
        db.commit()

    return job

@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get job status, current execution stage, and progress percentage.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/results", response_model=List[StageResultOut])
def get_job_results(job_id: str, db: Session = Depends(get_db)):
    """
    Get all stage results, confidence tiers, and explanations for a job.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    results = db.query(StageResult).filter(StageResult.job_id == job_id).all()
    return results
