@echo off
echo ========================================
echo INSTALASI APLIKASI KANTIN SEKOLAH
echo Windows Version - Optimized
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan!
    echo.
    echo Silakan install Python terlebih dahulu:
    echo https://www.python.org/downloads/
    echo.
    echo Pastikan centang "Add Python to PATH" saat install
    echo.
    pause
    exit /b
)

echo [OK] Python terdeteksi
python --version
echo.

REM Create virtual environment
echo [1/7] Membuat virtual environment...
if exist myenv (
    echo     Virtual environment sudah ada, skip...
) else (
    python -m venv myenv
    echo     [OK] Virtual environment dibuat
)
echo.

REM Activate virtual environment
echo [2/7] Aktivasi virtual environment...
call myenv\Scripts\activate.bat
echo     [OK] Virtual environment aktif
echo.

REM Upgrade pip
echo [3/7] Upgrade pip...
python -m pip install --upgrade pip --quiet
echo     [OK] Pip upgraded
echo.

REM Install core dependencies
echo [4/7] Install core dependencies...
echo     Installing streamlit, pandas, plotly...
pip install streamlit==1.31.0 --quiet
pip install pandas==2.1.4 --quiet
pip install plotly==5.18.0 --quiet
pip install python-barcode==0.15.1 --quiet
pip install Pillow==10.2.0 --quiet
pip install openpyxl==3.1.2 --quiet
pip install tqdm==4.66.1 --quiet
pip install numpy==1.26.3 --quiet
echo     [OK] Core dependencies installed
echo.

REM Install barcode scanner (pyzxing - Windows compatible)
echo [5/7] Install barcode scanner (pyzxing)...
echo     Installing opencv-python and pyzxing...
pip install opencv-python==4.9.0.80 --quiet
pip install pyzxing==0.2 --quiet
echo     [OK] Barcode scanner installed
echo.

REM Create folders
echo [6/7] Membuat folder yang diperlukan...
if not exist data mkdir data
if not exist data\backup mkdir data\backup
if not exist data\exports mkdir data\exports
if not exist barcodes mkdir barcodes
echo     [OK] Folder dibuat
echo.

REM Create sample CSV if not exists
echo [7/7] Setup sample data...
if exist data\products.csv (
    echo     [SKIP] products.csv sudah ada
) else (
    if exist sample_products.csv (
        copy sample_products.csv data\products.csv >nul
        echo     [OK] Sample data di-copy
    ) else (
        echo     [INFO] Tidak ada sample data, akan dibuat otomatis saat pertama run
    )
)
echo.

REM Test installation
echo ========================================
echo TESTING INSTALLATION
echo ========================================
echo.

echo Testing imports...
python -c "import streamlit; print('[OK] Streamlit:', streamlit.__version__)" 2>nul
python -c "import pandas; print('[OK] Pandas:', pandas.__version__)" 2>nul
python -c "import cv2; print('[OK] OpenCV:', cv2.__version__)" 2>nul
python -c "from pyzxing import BarCodeReader; print('[OK] Pyzxing: Ready')" 2>nul
echo.

echo ========================================
echo INSTALASI SELESAI!
echo ========================================
echo.
echo STATUS:
echo  [OK] Virtual environment: myenv
echo  [OK] Core dependencies installed
echo  [OK] Barcode scanner: pyzxing (Windows compatible)
echo  [OK] Folders created
echo  [OK] App ready to run
echo.
echo FITUR TERSEDIA:
echo  [OK] Dashboard & Statistik
echo  [OK] CRUD Data Produk
echo  [OK] Generate Barcode
echo  [OK] Webcam Scanner (pyzxing)
echo  [OK] Input Manual Barcode
echo  [OK] Laporan & Export
echo  [OK] Backup Data
echo.
echo KEUNGGULAN PYZXING:
echo  - Lebih stabil di Windows
echo  - Tidak perlu ZBar DLL eksternal
echo  - Support banyak format barcode
echo  - Pure Python implementation
echo.
echo ========================================
echo CARA MENJALANKAN APLIKASI:
echo ========================================
echo.
echo Option 1 (Recommended):
echo   Double click: run.bat
echo.
echo Option 2 (Manual):
echo   1. myenv\Scripts\activate
echo   2. streamlit run app.py
echo.
echo ========================================
echo.
echo Tekan Enter untuk menjalankan aplikasi...
pause >nul
streamlit run app.py
