@echo off
echo ========================================
echo APLIKASI KANTIN SEKOLAH
echo ========================================
echo.

REM Check if virtual environment exists
if not exist myenv (
    echo [ERROR] Virtual environment tidak ditemukan!
    echo.
    echo Silakan jalankan install_windows.bat terlebih dahulu
    echo.
    pause
    exit /b
)

REM Activate virtual environment
echo [*] Aktivasi virtual environment...
call myenv\Scripts\activate.bat
echo.

REM Run Streamlit
echo [*] Menjalankan aplikasi...
echo.
echo ========================================
echo APLIKASI BERJALAN
echo ========================================
echo.
echo Browser akan terbuka otomatis di:
echo http://localhost:8501
echo.
echo Login:
echo   Username: admin
echo   Password: admin123
echo.
echo Tekan Ctrl+C untuk stop aplikasi
echo ========================================
echo.

streamlit run app.py

REM Deactivate when done
call myenv\Scripts\deactivate.bat