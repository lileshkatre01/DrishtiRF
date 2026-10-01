@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   DrishtiRF - Building Standalone Windows Desktop App
echo ========================================================
echo.

:: 1. Build React Frontend Static Assets
echo [1/4] Building React Frontend with Vite...
cd frontend
call npm run build
if errorlevel 1 (
    echo [ERROR] Frontend build failed!
    exit /b 1
)
cd ..
echo [OK] Frontend built successfully.
echo.

:: 2. Package App with PyInstaller
echo [2/4] Packaging Desktop App with PyInstaller (--onedir)...
call .\drishti_venv\Scripts\pyinstaller.exe --noconfirm drishtirf.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed!
    exit /b 1
)
echo [OK] PyInstaller package created at dist\DrishtiRF
echo.

:: 3. Build Windows Installer with Inno Setup
echo [3/4] Compiling Windows Installer (DrishtiRF-Setup.exe)...

set "ISCC_EXE="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC_EXE (
    "%ISCC_EXE%" DrishtiRF.iss
    if errorlevel 1 (
        echo [WARNING] Inno Setup compilation returned non-zero code.
    ) else (
        echo [OK] DrishtiRF-Setup.exe built successfully in Output directory.
    )
) else (
    echo [NOTICE] Inno Setup ^(ISCC.exe^) was not found in standard Program Files paths.
    echo [NOTICE] The standalone executable folder is fully ready at: dist\DrishtiRF\DrishtiRF.exe
    echo [NOTICE] To build DrishtiRF-Setup.exe, download and install Inno Setup 6 from: https://jrsoftware.org/isdl.php
)
echo.

:: 4. Calculate SHA-256 Checksum
echo [4/4] Generating SHA-256 Checksum...
powershell -Command "if (Test-Path 'Output\DrishtiRF-Setup.exe') { Get-FileHash -Algorithm SHA256 Output\DrishtiRF-Setup.exe | Format-List } else { Write-Host 'Standalone executable SHA-256:'; Get-FileHash -Algorithm SHA256 dist\DrishtiRF\DrishtiRF.exe | Format-List }"

echo.
echo ========================================================
echo   BUILD PROCESS COMPLETED SUCCESSFULLY!
echo ========================================================
