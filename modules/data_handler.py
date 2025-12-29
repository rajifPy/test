"""
Module untuk menangani operasi CRUD data produk dan transaksi
Semua fungsi menggunakan pendekatan pemrograman terstruktur (tanpa OOP)
"""

import pandas as pd
import os
from datetime import datetime

# Path file data
PRODUCTS_FILE = "data/products.csv"
TRANSACTIONS_FILE = "data/transactions.csv"

# ==================== FUNGSI LOAD DATA ====================

def load_products_data():
    """
    Fungsi untuk memuat data produk dari CSV
    
    Returns:
        DataFrame: Data produk
    """
    try:
        if os.path.exists(PRODUCTS_FILE):
            df = pd.read_csv(PRODUCTS_FILE)
            return df
        else:
            # Buat file baru jika belum ada
            df = pd.DataFrame(columns=[
                'barcode_id', 'nama_produk', 'kategori', 
                'stok', 'harga_modal', 'harga_jual', 
                'tanggal_input'
            ])
            # Buat folder data jika belum ada
            os.makedirs("data", exist_ok=True)
            df.to_csv(PRODUCTS_FILE, index=False)
            return df
    except Exception as e:
        print(f"Error loading products: {e}")
        return pd.DataFrame()

def load_transactions_data():
    """
    Fungsi untuk memuat data transaksi dari CSV
    
    Returns:
        DataFrame: Data transaksi
    """
    try:
        if os.path.exists(TRANSACTIONS_FILE):
            df = pd.read_csv(TRANSACTIONS_FILE)
            return df
        else:
            # Buat file baru jika belum ada
            df = pd.DataFrame(columns=[
                'transaksi_id', 'waktu', 'barcode_id', 
                'nama_produk', 'jumlah', 'harga_satuan', 
                'total_harga', 'keuntungan'
            ])
            os.makedirs("data", exist_ok=True)
            df.to_csv(TRANSACTIONS_FILE, index=False)
            return df
    except Exception as e:
        print(f"Error loading transactions: {e}")
        return pd.DataFrame()

# ==================== FUNGSI SAVE DATA ====================

def save_products_data(df):
    """
    Fungsi untuk menyimpan data produk ke CSV
    
    Args:
        df: DataFrame yang akan disimpan
        
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        os.makedirs("data", exist_ok=True)
        df.to_csv(PRODUCTS_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving products: {e}")
        return False

def save_transactions_data(df):
    """
    Fungsi untuk menyimpan data transaksi ke CSV
    
    Args:
        df: DataFrame yang akan disimpan
        
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        os.makedirs("data", exist_ok=True)
        df.to_csv(TRANSACTIONS_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving transactions: {e}")
        return False

# ==================== FUNGSI CREATE ====================

def add_product(barcode_id, nama_produk, kategori, stok, harga_modal, harga_jual):
    """
    Fungsi untuk menambah produk baru
    
    Args:
        barcode_id: ID barcode produk
        nama_produk: Nama produk
        kategori: Kategori produk
        stok: Jumlah stok
        harga_modal: Harga modal
        harga_jual: Harga jual
        
    Returns:
        dict: Status dan pesan
    """
    try:
        df = load_products_data()
        
        # Cek apakah barcode sudah ada
        if barcode_id in df['barcode_id'].values:
            return {
                'success': False,
                'message': f"Barcode {barcode_id} sudah ada!"
            }
        
        # Tambah data baru
        new_data = {
            'barcode_id': barcode_id,
            'nama_produk': nama_produk,
            'kategori': kategori,
            'stok': stok,
            'harga_modal': harga_modal,
            'harga_jual': harga_jual,
            'tanggal_input': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        
        if save_products_data(df):
            return {
                'success': True,
                'message': f"Produk {nama_produk} berhasil ditambahkan!"
            }
        else:
            return {
                'success': False,
                'message': "Gagal menyimpan data!"
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

def add_transaction(barcode_id, nama_produk, jumlah, harga_satuan, harga_modal):
    """
    Fungsi untuk menambah transaksi baru
    
    Args:
        barcode_id: ID barcode produk
        nama_produk: Nama produk
        jumlah: Jumlah yang dibeli
        harga_satuan: Harga per item
        harga_modal: Harga modal per item
        
    Returns:
        dict: Status dan pesan
    """
    try:
        df = load_transactions_data()
        
        # Generate ID transaksi
        if len(df) == 0:
            transaksi_id = "TRX00001"
        else:
            last_id = df['transaksi_id'].iloc[-1]
            num = int(last_id.replace("TRX", "")) + 1
            transaksi_id = f"TRX{num:05d}"
        
        # Hitung total dan keuntungan
        total_harga = jumlah * harga_satuan
        keuntungan = jumlah * (harga_satuan - harga_modal)
        
        # Tambah data transaksi
        new_trans = {
            'transaksi_id': transaksi_id,
            'waktu': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'barcode_id': barcode_id,
            'nama_produk': nama_produk,
            'jumlah': jumlah,
            'harga_satuan': harga_satuan,
            'total_harga': total_harga,
            'keuntungan': keuntungan
        }
        
        df = pd.concat([df, pd.DataFrame([new_trans])], ignore_index=True)
        
        if save_transactions_data(df):
            return {
                'success': True,
                'message': f"Transaksi {transaksi_id} berhasil dicatat!"
            }
        else:
            return {
                'success': False,
                'message': "Gagal menyimpan transaksi!"
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

# ==================== FUNGSI READ ====================

def get_product_by_barcode(barcode_id):
    """
    Fungsi untuk mendapatkan data produk berdasarkan barcode
    
    Args:
        barcode_id: ID barcode yang dicari
        
    Returns:
        Series atau None: Data produk atau None jika tidak ditemukan
    """
    try:
        df = load_products_data()
        
        if barcode_id in df['barcode_id'].values:
            return df[df['barcode_id'] == barcode_id].iloc[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error getting product: {e}")
        return None

def search_product(keyword):
    """
    Fungsi untuk mencari produk berdasarkan keyword
    
    Args:
        keyword: Kata kunci pencarian
        
    Returns:
        DataFrame: Data produk yang cocok
    """
    try:
        df = load_products_data()
        
        if not df.empty and keyword:
            mask = df['nama_produk'].str.contains(keyword, case=False, na=False) | \
                   df['barcode_id'].str.contains(keyword, case=False, na=False)
            return df[mask]
        else:
            return df
            
    except Exception as e:
        print(f"Error searching product: {e}")
        return pd.DataFrame()

# ==================== FUNGSI UPDATE ====================

def update_product(barcode_id, nama_produk, kategori, stok, harga_modal, harga_jual):
    """
    Fungsi untuk mengupdate data produk
    
    Args:
        barcode_id: ID barcode produk
        nama_produk: Nama produk baru
        kategori: Kategori baru
        stok: Stok baru
        harga_modal: Harga modal baru
        harga_jual: Harga jual baru
        
    Returns:
        dict: Status dan pesan
    """
    try:
        df = load_products_data()
        
        if barcode_id not in df['barcode_id'].values:
            return {
                'success': False,
                'message': f"Produk dengan barcode {barcode_id} tidak ditemukan!"
            }
        
        # Update data
        df.loc[df['barcode_id'] == barcode_id, 'nama_produk'] = nama_produk
        df.loc[df['barcode_id'] == barcode_id, 'kategori'] = kategori
        df.loc[df['barcode_id'] == barcode_id, 'stok'] = stok
        df.loc[df['barcode_id'] == barcode_id, 'harga_modal'] = harga_modal
        df.loc[df['barcode_id'] == barcode_id, 'harga_jual'] = harga_jual
        
        if save_products_data(df):
            return {
                'success': True,
                'message': f"Produk {nama_produk} berhasil diupdate!"
            }
        else:
            return {
                'success': False,
                'message': "Gagal menyimpan perubahan!"
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

def reduce_stock(barcode_id, jumlah, nama_produk, harga_jual):
    """
    Fungsi untuk mengurangi stok (saat penjualan)
    
    Args:
        barcode_id: ID barcode produk
        jumlah: Jumlah yang dijual
        nama_produk: Nama produk
        harga_jual: Harga jual per item
        
    Returns:
        dict: Status dan pesan
    """
    try:
        df = load_products_data()
        
        if barcode_id not in df['barcode_id'].values:
            return {
                'success': False,
                'message': "Produk tidak ditemukan!"
            }
        
        # Ambil stok dan harga modal
        current_stock = df.loc[df['barcode_id'] == barcode_id, 'stok'].values[0]
        harga_modal = df.loc[df['barcode_id'] == barcode_id, 'harga_modal'].values[0]
        
        if current_stock < jumlah:
            return {
                'success': False,
                'message': f"Stok tidak cukup! Stok tersedia: {current_stock}"
            }
        
        # Kurangi stok
        new_stock = current_stock - jumlah
        df.loc[df['barcode_id'] == barcode_id, 'stok'] = new_stock
        
        # Simpan perubahan
        if save_products_data(df):
            # Catat transaksi
            trans_result = add_transaction(barcode_id, nama_produk, jumlah, harga_jual, harga_modal)
            
            if trans_result['success']:
                return {
                    'success': True,
                    'message': f"Berhasil! {jumlah} {nama_produk} terjual. Stok tersisa: {new_stock}"
                }
            else:
                return {
                    'success': False,
                    'message': "Stok berkurang tapi transaksi gagal dicatat!"
                }
        else:
            return {
                'success': False,
                'message': "Gagal mengurangi stok!"
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

def add_stock(barcode_id, jumlah):
    """
    Fungsi untuk menambah stok produk
    
    Args:
        barcode_id: ID barcode produk
        jumlah: Jumlah yang ditambah
        
    Returns:
        dict: Status dan pesan
    """
    try:
        df = load_products_data()
        
        if barcode_id not in df['barcode_id'].values:
            return {
                'success': False,
                'message': "Produk tidak ditemukan!"
            }
        
        # Tambah stok
        current_stock = df.loc[df['barcode_id'] == barcode_id, 'stok'].values[0]
        new_stock = current_stock + jumlah
        df.loc[df['barcode_id'] == barcode_id, 'stok'] = new_stock
        
        if save_products_data(df):
            return {
                'success': True,
                'message': f"Berhasil menambah {jumlah} item. Stok sekarang: {new_stock}"
            }
        else:
            return {
                'success': False,
                'message': "Gagal menambah stok!"
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

# ==================== FUNGSI DELETE ====================

def delete_product(barcode_id):
    """
    Fungsi untuk menghapus produk
    
    Args:
        barcode_id: ID barcode produk yang akan dihapus
        
    Returns:
        dict: Status dan pesan
    """
    try:
        df = load_products_data()
        
        if barcode_id not in df['barcode_id'].values:
            return {
                'success': False,
                'message': f"Produk dengan barcode {barcode_id} tidak ditemukan!"
            }
        
        # Hapus baris
        df = df[df['barcode_id'] != barcode_id]
        
        if save_products_data(df):
            # Hapus file barcode jika ada
            barcode_file = f"barcodes/{barcode_id}.png"
            if os.path.exists(barcode_file):
                os.remove(barcode_file)
            
            return {
                'success': True,
                'message': f"Produk berhasil dihapus!"
            }
        else:
            return {
                'success': False,
                'message': "Gagal menghapus produk!"
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }