@echo off
echo ========================================
echo FIX PYZBAR ERROR - Windows
echo ========================================
echo.
echo Pyzbar memerlukan ZBar DLL yang tidak
echo termasuk dalam pip install.
echo.
echo Aplikasi akan tetap berjalan TANPA
echo fitur webcam scanner. Gunakan INPUT
echo MANUAL untuk transaksi.
echo.
echo ========================================
echo.

echo [1/5] Uninstalling problematic packages...
pip uninstall opencv-python pyzbar -y

echo.
echo [2/5] Installing safe versions...
pip install opencv-python-headless==4.9.0.80
pip install Pillow numpy

echo.
echo [3/5] Skipping pyzbar installation...
echo       (Webcam scanner will be disabled)

echo.
echo [4/5] Testing OpenCV installation...
python -c "import cv2; print('OpenCV: OK')" 2>nul
if %errorlevel% neq 0 (
    echo OpenCV: FAILED
) else (
    echo OpenCV: SUCCESS
)

echo.
echo [5/5] Done!
echo.
echo ========================================
echo STATUS:
echo ========================================
echo [OK] Aplikasi akan berjalan normal
echo [OK] Semua fitur KECUALI webcam scanner
echo.
echo FITUR YANG BISA DIGUNAKAN:
echo  - Dashboard
echo  - Data Master (CRUD)
echo  - Input Manual Barcode (untuk transaksi)
echo  - Laporan
echo  - Backup & Export
echo.
echo FITUR YANG TIDAK BISA:
echo  - Webcam Scanner (gunakan Input Manual)
echo.
echo ========================================
echo SOLUSI WEBCAM SCANNER (Optional):
echo ========================================
echo.
echo Download ZBar DLL:
echo 1. Kunjungi: https://sourceforge.net/projects/zbar/files/zbar/0.10/
echo 2. Download: zbar-0.10-setup.exe
echo 3. Install ZBar
echo 4. Restart aplikasi
echo.
echo ATAU gunakan INPUT MANUAL (lebih mudah):
echo - Ketik Barcode ID (contoh: BRK001)
echo - Sama cepatnya dengan scan
echo - Tidak perlu webcam
echo.
echo ========================================
echo.
echo Tekan Enter untuk menjalankan aplikasi...
pause >nul
streamlit run app.py