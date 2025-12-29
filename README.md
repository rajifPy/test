
## 📥 Instalasi

### Prerequisites
- Python 3.8 atau lebih baru
- Webcam (optional, untuk scan barcode)
- Windows/Linux/MacOS

### Langkah Instalasi

#### **Windows**

1. **Clone atau download repository**
   ```bash
   git clone <repository-url>
   cd kantin-sekolah
   ```

2. **Jalankan installer**
   ```bash
   install_windows.bat
   ```
   
   Installer akan:
   - ✅ Membuat virtual environment
   - ✅ Install semua dependencies
   - ✅ Setup folders
   - ✅ Test installation

3. **Jalankan aplikasi**
   ```bash
   run.bat
   ```
   
   Atau manual:
   ```bash
   myenv\Scripts\activate
   streamlit run app.py
   ```

#### **Linux/Mac**

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd kantin-sekolah
   ```

2. **Buat virtual environment**
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Cara Penggunaan

### 1. Login
- **Username**: `admin`
- **Password**: `admin123`
