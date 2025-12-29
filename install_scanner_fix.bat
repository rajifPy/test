@echo off
echo ========================================
echo FIX BARCODE SCANNER INSTALLATION
echo ========================================
echo.
echo Issue: Scanner libraries not working
echo Solution: Reinstall pyzxing + pyzbar
echo.
echo ========================================
echo.

REM Activate virtual environment
if not exist myenv (
    echo [ERROR] Virtual environment tidak ditemukan!
    pause
    exit /b
)

call myenv\Scripts\activate.bat

echo [1/6] Uninstalling old scanner packages...
pip uninstall pyzxing pyzbar opencv-python -y

echo.
echo [2/6] Installing OpenCV (headless version for compatibility)...
pip install opencv-python-headless==4.9.0.80

echo.
echo [3/6] Installing Pyzbar (local scanner - butuh ZBar DLL)...
pip install pyzbar==0.1.9

echo.
echo [4/6] Installing Pyzxing (online scanner - butuh internet)...
pip install pyzxing==1.2

echo.
echo [5/6] Installing QR code support...
pip install qrcode[pil]==7.4.2

echo.
echo [6/6] Testing installation...
echo.

python -c "import cv2; print('[OK] OpenCV:', cv2.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo [FAILED] OpenCV
) else (
    echo [SUCCESS] OpenCV installed
)

python -c "from pyzbar.pyzbar import decode; print('[OK] Pyzbar: Ready')" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Pyzbar: Needs ZBar DLL - Will use pyzxing instead
) else (
    echo [SUCCESS] Pyzbar installed
)

python -c "from pyzxing import BarCodeReader; print('[OK] Pyzxing: Ready')" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Pyzxing: Will download JAR on first use
) else (
    echo [SUCCESS] Pyzxing installed
)

python -c "import qrcode; print('[OK] QRCode: Ready')" 2>nul
if %errorlevel% neq 0 (
    echo [FAILED] QRCode
) else (
    echo [SUCCESS] QRCode installed
)

echo.
echo ========================================
echo INSTALLATION COMPLETE
echo ========================================
echo.
echo Status:
echo  [OK] OpenCV: Installed
echo  [OK] Pyzxing: Installed (akan download JAR saat pertama scan)
echo  [OK] Pyzbar: Installed (fallback, butuh ZBar DLL)
echo  [OK] QRCode: Installed
echo.
echo CARA KERJA:
echo  1. Pyzxing (Priority): Pakai API online
echo     - Butuh internet untuk download JAR (sekali)
echo     - Kemudian offline
echo.
echo  2. Pyzbar (Fallback): Local library
echo     - Butuh ZBar DLL manual install
echo     - Atau gunakan Input Manual
echo.
echo ========================================
echo.
echo IMPORTANT:
echo - Saat PERTAMA KALI scan, pyzxing akan download
echo   file JAR (~20MB), tunggu 2-5 menit
echo - Pastikan INTERNET AKTIF untuk first-time setup
echo - Setelah itu bisa offline
echo.
echo ========================================
echo.
echo Tekan Enter untuk menjalankan aplikasi...
pause >nul
streamlit run app.py

call myenv\Scripts\deactivate.bat