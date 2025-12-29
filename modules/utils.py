"""
Module utilitas untuk fungsi-fungsi pembantu
UPDATED: Menambahkan fungsi export barcode dan QR code
"""

import pandas as pd
import os
from datetime import datetime
import shutil
import zipfile
import json

# Try import qrcode
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    print("⚠️ qrcode not installed. Run: pip install qrcode[pil]")

# ==================== FUNGSI VALIDASI ====================

def validate_number(value):
    """
    Fungsi untuk validasi apakah value adalah angka valid
    
    Args:
        value: Nilai yang akan divalidasi
        
    Returns:
        bool: True jika valid, False jika tidak
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def validate_not_empty(value):
    """
    Fungsi untuk validasi apakah value tidak kosong
    
    Args:
        value: Nilai yang akan divalidasi
        
    Returns:
        bool: True jika tidak kosong, False jika kosong
    """
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) > 0
    return True

def validate_positive_number(value):
    """
    Fungsi untuk validasi apakah value adalah angka positif
    
    Args:
        value: Nilai yang akan divalidasi
        
    Returns:
        bool: True jika valid, False jika tidak
    """
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False

def validate_date_format(date_str, format="%Y-%m-%d"):
    """
    Fungsi untuk validasi format tanggal
    
    Args:
        date_str: String tanggal
        format: Format tanggal yang diharapkan
        
    Returns:
        bool: True jika valid, False jika tidak
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

# ==================== FUNGSI FORMATTING ====================

def format_currency(amount):
    """
    Fungsi untuk format angka menjadi format mata uang Rupiah
    
    Args:
        amount: Jumlah uang
        
    Returns:
        str: Format Rupiah
    """
    try:
        return f"Rp {amount:,.0f}".replace(",", ".")
    except:
        return "Rp 0"

def format_date(date_obj, format="%d-%m-%Y"):
    """
    Fungsi untuk format tanggal
    
    Args:
        date_obj: Object datetime
        format: Format output
        
    Returns:
        str: Tanggal terformat
    """
    try:
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime(format)
    except:
        return str(date_obj)

def format_datetime(datetime_str):
    """
    Fungsi untuk format datetime ke format yang lebih readable
    
    Args:
        datetime_str: String datetime
        
    Returns:
        str: Datetime terformat
    """
    try:
        dt = pd.to_datetime(datetime_str)
        return dt.strftime("%d %B %Y, %H:%M")
    except:
        return datetime_str

# ==================== FUNGSI FILE MANAGEMENT ====================

def create_backup(file_path):
    """
    Fungsi untuk membuat backup file
    
    Args:
        file_path: Path file yang akan di-backup
        
    Returns:
        dict: Status dan path backup
    """
    try:
        # Buat folder backup jika belum ada
        backup_folder = "data/backup"
        os.makedirs(backup_folder, exist_ok=True)
        
        # Generate nama file backup dengan timestamp
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{timestamp}_{filename}"
        backup_path = os.path.join(backup_folder, backup_filename)
        
        # Copy file
        shutil.copy2(file_path, backup_path)
        
        return {
            'success': True,
            'backup_path': backup_path,
            'message': f"Backup berhasil: {backup_filename}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Gagal membuat backup: {str(e)}"
        }

def auto_backup_all():
    """
    Fungsi untuk backup semua file data secara otomatis
    
    Returns:
        dict: Status backup
    """
    try:
        results = []
        
        # Backup products
        if os.path.exists("data/products.csv"):
            result = create_backup("data/products.csv")
            results.append(result)
        
        # Backup transactions
        if os.path.exists("data/transactions.csv"):
            result = create_backup("data/transactions.csv")
            results.append(result)
        
        success_count = sum(1 for r in results if r['success'])
        
        return {
            'success': True,
            'total': len(results),
            'success_count': success_count,
            'message': f"Backup berhasil untuk {success_count} file"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

def clean_old_backups(days=7):
    """
    Fungsi untuk menghapus backup lama
    
    Args:
        days: Jumlah hari untuk menyimpan backup
        
    Returns:
        dict: Status pembersihan
    """
    try:
        backup_folder = "data/backup"
        if not os.path.exists(backup_folder):
            return {
                'success': True,
                'message': "Tidak ada folder backup"
            }
        
        deleted_count = 0
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        for filename in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_time < cutoff_date:
                os.remove(file_path)
                deleted_count += 1
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'message': f"Berhasil menghapus {deleted_count} backup lama"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

# ==================== FUNGSI EXPORT ====================

def export_to_excel(df, filename_prefix):
    """
    Fungsi untuk export DataFrame ke Excel
    
    Args:
        df: DataFrame yang akan di-export
        filename_prefix: Prefix nama file
        
    Returns:
        str: Path file Excel atau None jika gagal
    """
    try:
        # Buat folder exports jika belum ada
        os.makedirs("data/exports", exist_ok=True)
        
        # Generate nama file dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        filepath = os.path.join("data/exports", filename)
        
        # Export ke Excel
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        return filepath
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return None

def export_to_csv(df, filename_prefix):
    """
    Fungsi untuk export DataFrame ke CSV
    
    Args:
        df: DataFrame yang akan di-export
        filename_prefix: Prefix nama file
        
    Returns:
        str: Path file CSV atau None jika gagal
    """
    try:
        # Buat folder exports jika belum ada
        os.makedirs("data/exports", exist_ok=True)
        
        # Generate nama file dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join("data/exports", filename)
        
        # Export ke CSV
        df.to_csv(filepath, index=False)
        
        return filepath
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

# ==================== FUNGSI EXPORT BARCODE ====================

def copy_barcodes_to_folder(folder_name):
    """
    Copy semua barcode ke folder baru
    
    Args:
        folder_name: Nama folder tujuan
        
    Returns:
        dict: Status dan path export
    """
    try:
        # Create export base folder
        export_base = "data/barcode_exports"
        os.makedirs(export_base, exist_ok=True)
        
        # Create target folder
        export_path = os.path.join(export_base, folder_name)
        
        # Remove if exists
        if os.path.exists(export_path):
            shutil.rmtree(export_path)
        
        os.makedirs(export_path)
        
        # Source folder
        barcode_folder = "barcodes"
        
        if not os.path.exists(barcode_folder):
            return {
                'success': False,
                'message': "Folder barcodes tidak ditemukan!"
            }
        
        # Copy all PNG files
        barcode_files = [f for f in os.listdir(barcode_folder) if f.endswith('.png')]
        
        if not barcode_files:
            return {
                'success': False,
                'message': "Tidak ada barcode untuk di-copy!"
            }
        
        copied_count = 0
        for filename in barcode_files:
            src = os.path.join(barcode_folder, filename)
            dst = os.path.join(export_path, filename)
            shutil.copy2(src, dst)
            copied_count += 1
        
        return {
            'success': True,
            'message': f"✅ Berhasil copy {copied_count} barcode ke folder baru!",
            'export_path': os.path.abspath(export_path),
            'file_count': copied_count
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

def create_barcode_zip(zip_filename):
    """
    Compress semua barcode ke file ZIP
    
    Args:
        zip_filename: Nama file ZIP
        
    Returns:
        dict: Status dan path ZIP
    """
    try:
        # Create export base folder
        export_base = "data/barcode_exports"
        os.makedirs(export_base, exist_ok=True)
        
        # ZIP path
        zip_path = os.path.join(export_base, zip_filename)
        
        # Source folder
        barcode_folder = "barcodes"
        
        if not os.path.exists(barcode_folder):
            return {
                'success': False,
                'message': "Folder barcodes tidak ditemukan!"
            }
        
        # Get barcode files
        barcode_files = [f for f in os.listdir(barcode_folder) if f.endswith('.png')]
        
        if not barcode_files:
            return {
                'success': False,
                'message': "Tidak ada barcode untuk di-zip!"
            }
        
        # Create ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in barcode_files:
                file_path = os.path.join(barcode_folder, filename)
                zipf.write(file_path, arcname=filename)
        
        # Get ZIP size
        zip_size = os.path.getsize(zip_path)
        zip_size_mb = zip_size / (1024 * 1024)
        
        return {
            'success': True,
            'message': f"✅ Berhasil membuat ZIP dengan {len(barcode_files)} barcode!",
            'zip_path': os.path.abspath(zip_path),
            'file_count': len(barcode_files),
            'zip_size_mb': zip_size_mb
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

def create_barcode_package(package_name):
    """
    Create package lengkap: Excel info produk + semua barcode images
    
    Args:
        package_name: Nama package folder
        
    Returns:
        dict: Status dan path package
    """
    try:
        # Create export base folder
        export_base = "data/barcode_exports"
        os.makedirs(export_base, exist_ok=True)
        
        # Create package folder
        package_path = os.path.join(export_base, package_name)
        
        # Remove if exists
        if os.path.exists(package_path):
            shutil.rmtree(package_path)
        
        os.makedirs(package_path)
        
        # Create subfolder for images
        images_folder = os.path.join(package_path, "barcode_images")
        os.makedirs(images_folder)
        
        # Source folders
        barcode_folder = "barcodes"
        
        if not os.path.exists(barcode_folder):
            return {
                'success': False,
                'message': "Folder barcodes tidak ditemukan!"
            }
        
        # Copy barcode images
        barcode_files = [f for f in os.listdir(barcode_folder) if f.endswith('.png')]
        
        if not barcode_files:
            return {
                'success': False,
                'message': "Tidak ada barcode untuk di-export!"
            }
        
        for filename in barcode_files:
            src = os.path.join(barcode_folder, filename)
            dst = os.path.join(images_folder, filename)
            shutil.copy2(src, dst)
        
        # Create Excel with product info + barcode mapping
        from modules.data_handler import load_products_data
        
        products_df = load_products_data()
        
        if not products_df.empty:
            # Add column for barcode image filename
            products_df['barcode_image_file'] = products_df['barcode_id'] + '.png'
            
            # Add column for barcode availability
            products_df['barcode_available'] = products_df['barcode_id'].apply(
                lambda x: 'Yes' if os.path.exists(os.path.join(images_folder, f"{x}.png")) else 'No'
            )
            
            # Calculate profit margin
            products_df['profit_margin_%'] = products_df.apply(
                lambda row: calculate_profit_margin(row['harga_jual'], row['harga_modal']),
                axis=1
            ).round(2)
            
            # Save to Excel
            excel_path = os.path.join(package_path, "product_list_with_barcodes.xlsx")
            products_df.to_excel(excel_path, index=False, engine='openpyxl')
        else:
            excel_path = None
        
        # Create README file
        readme_path = os.path.join(package_path, "README.txt")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""
═══════════════════════════════════════════════════════
    BARCODE PACKAGE - {package_name}
═══════════════════════════════════════════════════════

📦 PACKAGE CONTENTS:
├── product_list_with_barcodes.xlsx    # Daftar produk lengkap
├── barcode_images/                    # Folder berisi semua barcode
│   ├── BRK001.png
│   ├── BRK002.png
│   └── ... ({len(barcode_files)} files)
└── README.txt                         # File ini

📊 STATISTICS:
- Total Products: {len(products_df) if not products_df.empty else 0}
- Total Barcodes: {len(barcode_files)}
- Created: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💡 CARA MENGGUNAKAN:
1. Buka file Excel untuk melihat daftar produk
2. Kolom 'barcode_image_file' menunjukkan nama file barcode
3. Kolom 'barcode_available' menunjukkan status barcode (Yes/No)
4. Print barcode dari folder 'barcode_images/'
5. Tempelkan barcode sesuai dengan produk

🖨️ TIPS PRINTING:
- Gunakan printer berkualitas baik
- Kertas sticker untuk hasil terbaik
- Test scan sebelum menempel ke produk
- Simpan backup digital package ini

═══════════════════════════════════════════════════════
Generated by: Kantin Sekolah Manager v1.0
═══════════════════════════════════════════════════════
            """)
        
        # Calculate total size
        total_size = 0
        for root, dirs, files in os.walk(package_path):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        
        total_size_mb = total_size / (1024 * 1024)
        
        return {
            'success': True,
            'message': f"✅ Package berhasil dibuat dengan {len(barcode_files)} barcode + Excel info!",
            'package_path': os.path.abspath(package_path),
            'image_count': len(barcode_files),
            'total_size_mb': total_size_mb,
            'excel_created': excel_path is not None
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

# ==================== FUNGSI STATISTIK HELPER ====================

def calculate_percentage(part, total):
    """
    Fungsi untuk menghitung persentase
    
    Args:
        part: Bagian
        total: Total
        
    Returns:
        float: Persentase
    """
    try:
        if total == 0:
            return 0
        return (part / total) * 100
    except:
        return 0

def calculate_profit_margin(harga_jual, harga_modal):
    """
    Fungsi untuk menghitung margin keuntungan
    
    Args:
        harga_jual: Harga jual
        harga_modal: Harga modal
        
    Returns:
        float: Margin dalam persen
    """
    try:
        if harga_jual == 0:
            return 0
        keuntungan = harga_jual - harga_modal
        return (keuntungan / harga_jual) * 100
    except:
        return 0

# ==================== FUNGSI DATA CLEANING ====================

def clean_dataframe(df):
    """
    Fungsi untuk membersihkan DataFrame dari nilai null dan duplikat
    
    Args:
        df: DataFrame yang akan dibersihkan
        
    Returns:
        DataFrame: DataFrame yang sudah dibersihkan
    """
    try:
        # Hapus duplikat
        df = df.drop_duplicates()
        
        # Fill NaN dengan 0 untuk kolom numerik
        numeric_columns = df.select_dtypes(include=['number']).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Fill NaN dengan string kosong untuk kolom string
        string_columns = df.select_dtypes(include=['object']).columns
        df[string_columns] = df[string_columns].fillna('')
        
        return df
        
    except Exception as e:
        print(f"Error cleaning dataframe: {e}")
        return df

def remove_duplicates(df, subset=None):
    """
    Fungsi untuk menghapus duplikat berdasarkan kolom tertentu
    
    Args:
        df: DataFrame
        subset: Kolom yang dijadikan acuan
        
    Returns:
        DataFrame: DataFrame tanpa duplikat
    """
    try:
        if subset:
            return df.drop_duplicates(subset=subset, keep='first')
        else:
            return df.drop_duplicates(keep='first')
    except:
        return df

# ==================== FUNGSI LOGGING ====================

def log_activity(activity_type, description, user="admin"):
    """
    Fungsi untuk mencatat aktivitas sistem
    
    Args:
        activity_type: Tipe aktivitas (CREATE, UPDATE, DELETE, etc)
        description: Deskripsi aktivitas
        user: User yang melakukan aktivitas
        
    Returns:
        bool: True jika berhasil
    """
    try:
        log_file = "data/activity_log.csv"
        
        # Buat log entry
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': user,
            'activity_type': activity_type,
            'description': description
        }
        
        # Load atau buat log file
        if os.path.exists(log_file):
            log_df = pd.read_csv(log_file)
        else:
            log_df = pd.DataFrame(columns=['timestamp', 'user', 'activity_type', 'description'])
        
        # Append log
        log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
        
        # Simpan
        log_df.to_csv(log_file, index=False)
        
        return True
        
    except Exception as e:
        print(f"Error logging activity: {e}")
        return False

def get_recent_logs(limit=10):
    """
    Fungsi untuk mengambil log aktivitas terbaru
    
    Args:
        limit: Jumlah log yang akan diambil
        
    Returns:
        DataFrame: Log terbaru
    """
    try:
        log_file = "data/activity_log.csv"
        
        if os.path.exists(log_file):
            log_df = pd.read_csv(log_file)
            return log_df.tail(limit)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error getting logs: {e}")
        return pd.DataFrame()

# ==================== FUNGSI QR CODE ====================

def generate_qrcode(barcode_id, product_data):
    """
    Generate QR code untuk produk
    QR berisi data JSON lengkap produk
    
    Args:
        barcode_id: ID barcode produk
        product_data: Dictionary data produk
        
    Returns:
        str: Path file QR code atau None jika gagal
    """
    if not QRCODE_AVAILABLE:
        return None
    
    try:
        # Create qrcodes folder
        qr_folder = "qrcodes"
        os.makedirs(qr_folder, exist_ok=True)
        
        # Create QR data (JSON)
        qr_data = {
            "barcode_id": barcode_id,
            "nama_produk": product_data.get('nama_produk', ''),
            "kategori": product_data.get('kategori', ''),
            "harga_jual": int(product_data.get('harga_jual', 0)),
            "stok": int(product_data.get('stok', 0))
        }
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save
        qr_path = os.path.join(qr_folder, f"{barcode_id}_qr.png")
        img.save(qr_path)
        
        return qr_path
        
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

def generate_batch_qrcodes(products_df):
    """
    Generate QR codes untuk batch produk
    
    Args:
        products_df: DataFrame produk
        
    Returns:
        dict: Status dan hasil
    """
    if not QRCODE_AVAILABLE:
        return {
            'success': False,
            'message': '❌ Library qrcode tidak tersedia. Install: pip install qrcode[pil]'
        }
    
    try:
        success_count = 0
        failed_items = []
        
        for index, row in products_df.iterrows():
            product_data = {
                'nama_produk': row['nama_produk'],
                'kategori': row['kategori'],
                'harga_jual': row['harga_jual'],
                'stok': row['stok']
            }
            
            result = generate_qrcode(row['barcode_id'], product_data)
            
            if result:
                success_count += 1
            else:
                failed_items.append(row['barcode_id'])
        
        return {
            'success': True,
            'total': len(products_df),
            'success_count': success_count,
            'failed_items': failed_items,
            'message': f"✅ Berhasil generate {success_count} dari {len(products_df)} QR code"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}"
        }

def export_barcodes_zip():
    """
    Export semua barcode ke ZIP
    
    Returns:
        dict: Status dan path ZIP
    """
    try:
        barcode_folder = "barcodes"
        
        if not os.path.exists(barcode_folder):
            return {
                'success': False,
                'message': '❌ Folder barcodes tidak ditemukan'
            }
        
        barcode_files = [f for f in os.listdir(barcode_folder) if f.endswith('.png')]
        
        if not barcode_files:
            return {
                'success': False,
                'message': '❌ Tidak ada barcode untuk di-export'
            }
        
        # Create export folder
        export_folder = "data/exports"
        os.makedirs(export_folder, exist_ok=True)
        
        # Create ZIP
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"barcodes_{timestamp}.zip"
        zip_path = os.path.join(export_folder, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in barcode_files:
                file_path = os.path.join(barcode_folder, filename)
                zipf.write(file_path, arcname=filename)
        
        return {
            'success': True,
            'zip_path': zip_path,
            'file_count': len(barcode_files),
            'message': f"✅ Export {len(barcode_files)} barcode berhasil!"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}"
        }

def export_qrcodes_zip():
    """
    Export semua QR code ke ZIP
    
    Returns:
        dict: Status dan path ZIP
    """
    try:
        qr_folder = "qrcodes"
        
        if not os.path.exists(qr_folder):
            return {
                'success': False,
                'message': '❌ Folder qrcodes tidak ditemukan'
            }
        
        qr_files = [f for f in os.listdir(qr_folder) if f.endswith('_qr.png')]
        
        if not qr_files:
            return {
                'success': False,
                'message': '❌ Tidak ada QR code untuk di-export'
            }
        
        # Create export folder
        export_folder = "data/exports"
        os.makedirs(export_folder, exist_ok=True)
        
        # Create ZIP
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"qrcodes_{timestamp}.zip"
        zip_path = os.path.join(export_folder, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in qr_files:
                file_path = os.path.join(qr_folder, filename)
                zipf.write(file_path, arcname=filename)
        
        return {
            'success': True,
            'zip_path': zip_path,
            'file_count': len(qr_files),
            'message': f"✅ Export {len(qr_files)} QR code berhasil!"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}"
        }

def export_both_codes_zip():
    """
    Export barcode DAN QR code ke satu ZIP package
    
    Returns:
        dict: Status dan path ZIP
    """
    try:
        barcode_folder = "barcodes"
        qr_folder = "qrcodes"
        
        barcode_files = []
        qr_files = []
        
        if os.path.exists(barcode_folder):
            barcode_files = [f for f in os.listdir(barcode_folder) if f.endswith('.png')]
        
        if os.path.exists(qr_folder):
            qr_files = [f for f in os.listdir(qr_folder) if f.endswith('_qr.png')]
        
        if not barcode_files and not qr_files:
            return {
                'success': False,
                'message': '❌ Tidak ada barcode atau QR code untuk di-export'
            }
        
        # Create export folder
        export_folder = "data/exports"
        os.makedirs(export_folder, exist_ok=True)
        
        # Create ZIP with subfolder structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"complete_codes_{timestamp}.zip"
        zip_path = os.path.join(export_folder, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add barcodes
            for filename in barcode_files:
                file_path = os.path.join(barcode_folder, filename)
                zipf.write(file_path, arcname=f"barcodes/{filename}")
            
            # Add QR codes
            for filename in qr_files:
                file_path = os.path.join(qr_folder, filename)
                zipf.write(file_path, arcname=f"qrcodes/{filename}")
            
            # Add README
            readme_content = f"""
═══════════════════════════════════════════════
    COMPLETE CODES PACKAGE
═══════════════════════════════════════════════

📦 PACKAGE CONTENTS:
├── barcodes/          ({len(barcode_files)} files)
│   └── Code128 format barcodes
│
└── qrcodes/           ({len(qr_files)} files)
    └── QR codes with JSON product data

📊 STATISTICS:
- Total Barcodes: {len(barcode_files)}
- Total QR Codes: {len(qr_files)}
- Created: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💡 USAGE:
- Barcodes: For scanning with barcode scanners
- QR Codes: Scan with smartphone for product info

═══════════════════════════════════════════════
Generated by: Kantin Sekolah Manager v1.0
═══════════════════════════════════════════════
            """
            
            zipf.writestr("README.txt", readme_content)
        
        return {
            'success': True,
            'zip_path': zip_path,
            'barcode_count': len(barcode_files),
            'qr_count': len(qr_files),
            'message': f"✅ Export {len(barcode_files)} barcode + {len(qr_files)} QR code berhasil!"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}"
        }