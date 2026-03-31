@echo off
echo ============================================================
echo   SOVEREIGN V10 — BUILDING DLL (sovereign.dll)
echo ============================================================
echo.

call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

cd /d "c:\Users\sumit\Downloads\infra refine\engine"

echo [1/2] Compiling DLL (/openmp = multi-threaded)...
cl /LD /EHsc /O2 /openmp /DBUILD_DLL sovereign_v10_titan.cpp /Fe:sovereign.dll

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: sovereign.dll compiled.
    echo.
    echo The DLL will auto-load vocab.txt and master_brain.bin.
) else (
    echo.
    echo ERROR: Compilation failed.
)
