from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import uuid
import shutil
from typing import Optional

from backend.api.deps import get_db
from backend.api.schemas import CaptureOut
from backend.core.config import settings
from backend.core.logging import logger
from backend.db.models import Capture
from backend.dsp.ingestion import read_signal_file
from backend.dsp.preprocess import preprocess_signal

router = APIRouter(prefix="/upload", tags=["Ingestion & Upload"])

@router.post("", response_model=CaptureOut, status_code=status.HTTP_201_CREATED)
async def upload_signal_file(
    file: UploadFile = File(...),
    format_override: Optional[str] = Form(None),
    sample_rate_override: Optional[float] = Form(None),
    center_freq_override: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and ingest an offline .iq, .wav, or .sigmf signal file.
    - Saves raw file to storage.
    - Infers/parses format and parameters.
    - Normalizes power and applies DC offset correction.
    - Writes record to database.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{os.path.basename(file.filename)}"
    save_path = os.path.join(settings.STORAGE_DIR, "uploads", safe_filename)

    # Save uploaded bytes to disk
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save upload file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Ingest and preprocess signal file
    try:
        raw_iq = read_signal_file(
            save_path,
            sample_rate_override=sample_rate_override,
            center_freq_override=center_freq_override,
            format_override=format_override
        )
        clean_iq = preprocess_signal(raw_iq)
    except Exception as e:
        logger.error(f"Failed to parse signal file {file.filename}: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Error parsing signal file: {str(e)}")

    # Write capture metadata record to database
    capture_entry = Capture(
        id=file_id,
        filename=file.filename,
        path=save_path,
        format=clean_iq.source_format,
        sample_rate=clean_iq.sample_rate,
        center_freq=clean_iq.center_freq,
        n_samples=clean_iq.num_samples
    )

    db.add(capture_entry)
    db.commit()
    db.refresh(capture_entry)

    logger.info(f"Successfully uploaded and ingested capture ID {file_id}: {file.filename} ({clean_iq.source_format}, N={clean_iq.num_samples})")

    return capture_entry
