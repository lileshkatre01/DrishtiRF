# DrishtiRF (SIGNAL-IQ)

Automated Analysis of `.IQ` and `.WAV` Files with Signal Parameter Extraction  
**SIH 2026 Problem Statement ID**: PS 26147 (NTRO)

## Overview
DrishtiRF is an end-to-end, automated, explainable signals intelligence (SIGINT) analysis platform built to process raw off-air RF recordings without metadata. It performs parameter estimation ($f_s$, bandwidth, center frequency, SNR, symbol rate), automatic modulation classification (FSK/PSK/QAM), demodulation, joint de-interleaving and FEC decoding, bitstream correlation, and interactive dark-mode dashboard visualization.

## Repository Structure
```
drishti-rf/
├── backend/                  # FastAPI + Celery + SQLAlchemy Backend
│   ├── api/                  # REST & WebSocket Routers
│   ├── core/                 # App Settings, Confidence Scoring, Explainability Engine
│   ├── db/                   # Database Models & Session Management
│   ├── dsp/                  # Core Signal Processing & Decoding Engine
│   ├── workers/              # Celery Async Worker Tasks
│   ├── tests/                # Pytest Suite
│   └── main.py               # FastAPI Entrypoint
├── ml_training/              # Synthetic Dataset Generator & CNN Training Scripts
├── frontend/                 # React + Vite + Tailwind + Plotly SIGINT Dashboard
├── sample_data/              # Pre-validated Synthetic & Real Captured Waveforms
├── docker-compose.yml        # Multi-container orchestration
└── README.md
```

## Quick Start (Phase 2 Scaffold)
1. Setup Python Environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run Backend Server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

3. Access Health Endpoint:
   `http://localhost:8000/api/health`
