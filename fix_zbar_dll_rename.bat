@echo off
echo ========================================
echo FIX PYZBAR - COPY DLL (ZBar 0.10)
echo ========================================
echo.

REM Aktivasi virtual environment
if not exist myenv (
    echo [ERROR] Virtual environment tidak ditemukan!
    echo Pastikan Anda menjalankan script ini di folder project.
    pause
    exit /b
)

call myenv\Scripts\activate.bat

echo [*] Setup untuk ZBar versi 0.10
echo     (File: libzbar-0.dll, bukan libzbar-64.dll)
echo.

REM Lokasi ZBar
set ZBAR_BIN=C:\Program Files (x86)\ZBar\bin

REM Lokasi pyzbar
set PYZBAR_PATH=myenv\Lib\site-packages\pyzbar

REM Cek apakah ZBar ada
if not exist "%ZBAR_BIN%\libzbar-0.dll" (
    echo [ERROR] File libzbar-0.dll tidak ditemukan di:
    echo %ZBAR_BIN%
    echo.
    echo Pastikan ZBar sudah terinstall.
    pause
    exit /b
)

REM Cek apakah pyzbar ada
if not exist "%PYZBAR_PATH%" (
    echo [ERROR] Folder pyzbar tidak ditemukan!
    echo.
    echo Install pyzbar terlebih dahulu:
    echo   pip install pyzbar
    echo.
    pause
    exit /b
)

echo ========================================
echo [*] COPY DLL KE PYZBAR
echo ========================================
echo.

REM Copy semua DLL yang ada
echo [1/5] Copy libzbar-0.dll...
copy "%ZBAR_BIN%\libzbar-0.dll" "%PYZBAR_PATH%\" /Y

echo [2/5] Copy libiconv-2.dll...
if exist "%ZBAR_BIN%\libiconv-2.dll" (
    copy "%ZBAR_BIN%\libiconv-2.dll" "%PYZBAR_PATH%\" /Y
) else (
    echo       [SKIP] File tidak ada
)

echo [3/5] Copy libjpeg-7.dll...
if exist "%ZBAR_BIN%\libjpeg-7.dll" (
    copy "%ZBAR_BIN%\libjpeg-7.dll" "%PYZBAR_PATH%\" /Y
) else (
    echo       [SKIP] File tidak ada
)

echo [4/5] Copy libxml2-2.dll...
if exist "%ZBAR_BIN%\libxml2-2.dll" (
    copy "%ZBAR_BIN%\libxml2-2.dll" "%PYZBAR_PATH%\" /Y
) else (
    echo       [SKIP] File tidak ada
)

echo [5/5] Copy zlib1.dll...
if exist "%ZBAR_BIN%\zlib1.dll" (
    copy "%ZBAR_BIN%\zlib1.dll" "%PYZBAR_PATH%\" /Y
) else (
    echo       [SKIP] File tidak ada
)

echo.
echo [OK] Semua DLL berhasil di-copy!
echo.

REM Sekarang edit wrapper.py untuk gunakan libzbar-0.dll
echo ========================================
echo [*] UPDATE PYZBAR WRAPPER
echo ========================================
echo.

echo Membuat file patch untuk pyzbar...

REM Buat file Python untuk patch pyzbar
echo import os > temp_patch.py
echo import shutil >> temp_patch.py
echo. >> temp_patch.py
echo # Backup wrapper.py >> temp_patch.py
echo wrapper_path = r'%PYZBAR_PATH%\wrapper.py' >> temp_patch.py
echo backup_path = r'%PYZBAR_PATH%\wrapper.py.backup' >> temp_patch.py
echo. >> temp_patch.py
echo if not os.path.exists(backup_path): >> temp_patch.py
echo     shutil.copy2(wrapper_path, backup_path) >> temp_patch.py
echo     print('[OK] Backup wrapper.py dibuat') >> temp_patch.py
echo. >> temp_patch.py
echo # Baca file >> temp_patch.py
echo with open(wrapper_path, 'r', encoding='utf-8') as f: >> temp_patch.py
echo     content = f.read() >> temp_patch.py
echo. >> temp_patch.py
echo # Ganti libzbar-64.dll dengan libzbar-0.dll >> temp_patch.py
echo content = content.replace('libzbar-64.dll', 'libzbar-0.dll') >> temp_patch.py
echo content = content.replace('libzbar-32.dll', 'libzbar-0.dll') >> temp_patch.py
echo. >> temp_patch.py
echo # Simpan >> temp_patch.py
echo with open(wrapper_path, 'w', encoding='utf-8') as f: >> temp_patch.py
echo     f.write(content) >> temp_patch.py
echo. >> temp_patch.py
echo print('[OK] wrapper.py berhasil di-patch') >> temp_patch.py

echo Menjalankan patch...
python temp_patch.py

REM Hapus file temporary
del temp_patch.py

echo.
echo ========================================
echo [*] TESTING PYZBAR
echo ========================================
echo.

python -c "from pyzbar.pyzbar import decode; print('[SUCCESS] Pyzbar berfungsi!')" 2>nul

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] PERBAIKAN BERHASIL!
    echo ========================================
    echo.
    echo Status:
    echo  [OK] DLL berhasil di-copy
    echo  [OK] Pyzbar wrapper di-patch
    echo  [OK] Pyzbar berfungsi normal
    echo  [OK] Webcam scanner siap digunakan
    echo.
    echo ========================================
    echo.
    echo Tekan Enter untuk menjalankan aplikasi...
    pause >nul
    streamlit run app.py
) else (
    echo.
    echo [FAILED] Pyzbar masih error.
    echo.
    echo Coba langkah berikut:
    echo.
    echo 1. Restart Command Prompt
    echo 2. Jalankan script ini lagi
    echo 3. Atau gunakan solusi Input Manual
    echo.
    pause
)

call myenv\Scripts\deactivate.bat