# DrishtiRF Standalone Windows Desktop App — Build Guide

This document provides instructions for building and packaging the **DrishtiRF** SIGINT Analysis Platform into a standalone Windows desktop executable (`DrishtiRF.exe`) and installer (`DrishtiRF-Setup.exe`).

---

## 📋 Prerequisites

To rebuild the desktop application installer, ensure the following are installed on your Windows system:

1. **Python 3.10+** (with `drishti_venv` virtual environment)
2. **Node.js (v18+) & npm** (for building the React frontend)
3. **Inno Setup 6** (optional, to compile `DrishtiRF-Setup.exe` installer)  
   *Download free from: [https://jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php)*

---

## 🚀 One-Command Build

To build the entire application and installer in a single command, open Command Prompt or PowerShell in the project root directory and run:

```cmd
.\build.bat
```

---

## 🛠️ Step-by-Step Rebuild Instructions

If you prefer executing the build steps individually:

### Step 1: Build the React Frontend
```cmd
cd frontend
npm install
npm run build
cd ..
```
*Output: `frontend/dist/` containing compiled static HTML/JS/CSS assets.*

### Step 2: Package Python Backend & PyWebView GUI
```cmd
.\drishti_venv\Scripts\pyinstaller.exe --noconfirm drishtirf.spec
```
*Output: Standalone application folder at `dist/DrishtiRF/` with `DrishtiRF.exe`.*

### Step 3: Compile Windows Setup Installer
```cmd
ISCC.exe DrishtiRF.iss
```
*Output: `DrishtiRF-Setup.exe` in the `Output/` folder.*

### Step 4: Verify SHA-256 Checksum
```powershell
Get-FileHash -Algorithm SHA256 Output\DrishtiRF-Setup.exe
```

---

## ✨ Features of the Standalone App

- **100% Zero Prerequisites**: End users do not need Python, Node.js, pip, or GNU Radio installed.
- **100% Offline**: All fonts, static UI assets, and DSP engines run locally without CDN links.
- **Dedicated Desktop Window**: Launches in a PyWebView native desktop window on a dynamic free port.
- **Clean Process Lifecycle**: Closing the desktop window automatically terminates the FastAPI backend process and uvicorn server.
- **Zero-Copy Local Ingestion**: `.IQ` and `.wav` files selected from disk open directly with no network transfer delay or duplicate file copies.
