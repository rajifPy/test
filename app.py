"""
APLIKASI PENGELOLAAN STOK KANTIN SEKOLAH
Dengan Cart System untuk Multiple Products
Version: 2.0 (Enhanced with Shopping Cart)
"""

import streamlit as st
import pandas as pd
import os
import sys
import time
from datetime import datetime, timedelta

# Import modul custom - FIXED IMPORTS
from modules.data_handler import (
    get_product_by_barcode, 
    add_transaction, 
    save_products_data, 
    load_products_data
)
from modules.barcode_handler import (
    scan_barcode_realtime,  # ← FIXED: dari barcode_handler, bukan barcode_handler_realtime
    check_scanner_availability
)
from modules.utils import format_currency, calculate_profit_margin
from modules.data_handler import *
from modules.chart_handler import *
from modules.utils import *

# Import barcode handler dengan error handling
try:
    from modules.barcode_handler import *
    BARCODE_MODULE_LOADED = True
except Exception as e:
    BARCODE_MODULE_LOADED = False
    print(f"⚠️ Warning: Barcode scanner tidak tersedia - {e}")
    
    # Define dummy functions
    def generate_barcode(barcode_id, product_name):
        return None
    
    def generate_batch_barcodes(products_df):
        return {
            'success': False,
            'message': 'Fitur generate barcode tidak tersedia. Install ZBar untuk mengaktifkan.'
        }
    
    def scan_barcode_from_camera():
        return {
            'success': False,
            'message': 'Webcam scanner tidak tersedia. Gunakan Input Manual.'
        }
    
    def check_scanner_availability():
        return {
            'available': False,
            'message': '⚠️ Webcam scanner tidak tersedia - Gunakan input manual'
        }

# Konfigurasi halaman
st.set_page_config(
    page_title="Kantin Sekolah Manager",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS CUSTOM ====================

def load_custom_css():
    st.markdown("""
        <style>
        /* Main Headers */
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            padding: 1rem;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Scan Page Styles */
        .scan-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .scan-method-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .scan-method-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }
        
        .product-preview {
            background: #f5f7fa;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        
        /* Cart Styles */
        .cart-badge {
            background: #f44336;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9rem;
            display: inline-block;
        }
        
        .cart-item {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .cart-summary {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-top: 1rem;
        }
        
        /* Metric Cards */
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        /* Alerts */
        .alert-danger {
            background: #fee;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #f44;
            margin: 1rem 0;
        }
        
        .alert-success {
            background: #efe;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #4f4;
            margin: 1rem 0;
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: scale(1.02);
        }
        </style>
    """, unsafe_allow_html=True)

# ==================== SESSION STATE ====================

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'last_scan' not in st.session_state:
        st.session_state.last_scan = None
    if 'cart' not in st.session_state:
        st.session_state.cart = []

# ==================== CART FUNCTIONS ====================

def add_to_cart(product, quantity):
    """Add product to cart or update quantity"""
    # Check if product already in cart
    existing_item = None
    existing_index = None
    
    for idx, item in enumerate(st.session_state.cart):
        if item['barcode_id'] == product['barcode_id']:
            existing_item = item
            existing_index = idx
            break
    
    # Get current stock
    current_product = get_product_by_barcode(product['barcode_id'])
    available_stock = int(current_product['stok'])
    
    # Calculate total quantity in cart
    cart_quantity = existing_item['quantity'] if existing_item else 0
    new_total = cart_quantity + quantity
    
    # Validate stock
    if new_total > available_stock:
        return {
            'success': False,
            'message': f"❌ Stok tidak cukup! Tersedia: {available_stock}, di cart: {cart_quantity}"
        }
    
    if existing_item:
        # Update quantity
        st.session_state.cart[existing_index]['quantity'] = new_total
        st.session_state.cart[existing_index]['subtotal'] = new_total * product['harga_jual']
        st.session_state.cart[existing_index]['profit'] = new_total * (product['harga_jual'] - product['harga_modal'])
        
        return {
            'success': True,
            'message': f"✅ Updated! {product['nama_produk']} sekarang {new_total} pcs di cart"
        }
    else:
        # Add new item
        cart_item = {
            'barcode_id': product['barcode_id'],
            'nama_produk': product['nama_produk'],
            'kategori': product['kategori'],
            'quantity': quantity,
            'harga_satuan': int(product['harga_jual']),
            'harga_modal': int(product['harga_modal']),
            'subtotal': quantity * product['harga_jual'],
            'profit': quantity * (product['harga_jual'] - product['harga_modal'])
        }
        
        st.session_state.cart.append(cart_item)
        
        return {
            'success': True,
            'message': f"✅ {product['nama_produk']} ({quantity} pcs) ditambahkan ke cart!"
        }

def remove_from_cart(index):
    """Remove item from cart"""
    if 0 <= index < len(st.session_state.cart):
        removed_item = st.session_state.cart.pop(index)
        return {
            'success': True,
            'message': f"✅ {removed_item['nama_produk']} dihapus dari cart"
        }
    return {
        'success': False,
        'message': "❌ Item tidak ditemukan"
    }

def clear_cart():
    """Clear all items in cart"""
    st.session_state.cart = []
    return {
        'success': True,
        'message': "🗑️ Cart dikosongkan"
    }

def calculate_cart_totals():
    """Calculate cart totals"""
    if not st.session_state.cart:
        return {
            'total_items': 0,
            'total_quantity': 0,
            'total_price': 0,
            'total_profit': 0
        }
    
    total_items = len(st.session_state.cart)
    total_quantity = sum(item['quantity'] for item in st.session_state.cart)
    total_price = sum(item['subtotal'] for item in st.session_state.cart)
    total_profit = sum(item['profit'] for item in st.session_state.cart)
    
    return {
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'total_profit': total_profit
    }

def process_checkout():
    """Process checkout for all items in cart"""
    if not st.session_state.cart:
        return {
            'success': False,
            'message': "❌ Cart kosong! Tambahkan produk terlebih dahulu."
        }
    
    # Load products data
    products_df = load_products_data()
    
    # Validate stock for all items
    for item in st.session_state.cart:
        current_product = products_df[products_df['barcode_id'] == item['barcode_id']]
        
        if current_product.empty:
            return {
                'success': False,
                'message': f"❌ Produk {item['nama_produk']} tidak ditemukan!"
            }
        
        current_stock = int(current_product.iloc[0]['stok'])
        
        if current_stock < item['quantity']:
            return {
                'success': False,
                'message': f"❌ Stok {item['nama_produk']} tidak cukup! Tersedia: {current_stock}, diminta: {item['quantity']}"
            }
    
    # Process each item
    transactions_created = []
    
    for item in st.session_state.cart:
        # Update stock
        products_df.loc[products_df['barcode_id'] == item['barcode_id'], 'stok'] -= item['quantity']
        
        # Create transaction
        trans_result = add_transaction(
            item['barcode_id'],
            item['nama_produk'],
            item['quantity'],
            item['harga_satuan'],
            item['harga_modal']
        )
        
        if trans_result['success']:
            transactions_created.append(trans_result)
        else:
            return {
                'success': False,
                'message': f"❌ Gagal create transaksi untuk {item['nama_produk']}"
            }
    
    # Save updated products data
    if save_products_data(products_df):
        totals = calculate_cart_totals()
        
        # Clear cart after success
        clear_cart()
        
        return {
            'success': True,
            'transactions_count': len(transactions_created),
            'total_items': totals['total_items'],
            'total_quantity': totals['total_quantity'],
            'total_price': totals['total_price'],
            'total_profit': totals['total_profit'],
            'message': f"✅ Checkout berhasil! {totals['total_items']} produk, {totals['total_quantity']} pcs terjual"
        }
    else:
        return {
            'success': False,
            'message': "❌ Gagal menyimpan data produk!"
        }

# ==================== LOGIN PAGE ====================

def login_page():
    """Login page"""
    st.markdown("<h1 class='main-header'>🏪 Login Kantin Sekolah</h1>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ Tentang Aplikasi", expanded=False):
        st.markdown("""
        ### Aplikasi Pengelolaan Stok Kantin Sekolah
        
        **Fitur Utama:**
        - 📦 CRUD Data Produk dengan Barcode
        - 🛒 Shopping Cart (Multiple Products)
        - 📷 Scan Barcode Real-time
        - 📊 Dashboard Real-time
        - 💰 Laporan Penjualan & Keuntungan
        - 💾 Backup & Export Data
        
        **Teknologi:**
        - Python + Streamlit
        - CSV Storage (Offline)
        - Barcode Code128
        - Real-time Scanner
        
        **Version:** 2.0 (Enhanced with Cart System)
        """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Silakan Login")
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        
        if st.button("🔐 Login", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Login berhasil!")
                st.balloons()
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Username atau password salah!")
        
        st.markdown("---")
        st.info("💡 **Demo Login:**\n- Username: `admin`\n- Password: `admin123`")

# ==================== DASHBOARD PAGE ====================

def dashboard_page():
    """Dashboard page"""
    st.markdown("<h1 class='main-header'>📊 Dashboard Kantin Sekolah</h1>", unsafe_allow_html=True)
    
    products_df = load_products_data()
    transactions_df = load_transactions_data()
    stats = calculate_statistics(products_df, transactions_df)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Produk", stats['total_products'])
    with col2:
        st.metric("Total Stok", stats['total_stock'])
    with col3:
        st.metric("Transaksi Hari Ini", stats['today_transactions'])
    with col4:
        st.metric("Keuntungan Hari Ini", format_currency(stats['today_profit']))
    
    st.markdown("---")
    
    # Low stock alert
    if not products_df.empty:
        low_stock = products_df[products_df['stok'] < 10]
        if not low_stock.empty:
            st.warning(f"⚠️ **PERINGATAN:** Ada {len(low_stock)} produk dengan stok menipis (< 10)!")
            with st.expander("Lihat Detail"):
                for idx, row in low_stock.iterrows():
                    st.write(f"- **{row['nama_produk']}**: Stok tersisa {row['stok']}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Stok Produk (Top 10)")
        if not products_df.empty:
            fig = create_stock_chart(products_df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data produk")
    
    with col2:
        st.subheader("💰 Keuntungan Harian")
        if not transactions_df.empty:
            fig = create_profit_chart(transactions_df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data transaksi")
    
    if not transactions_df.empty:
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("📊 Penjualan Harian")
            fig = create_sales_chart(transactions_df)
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            st.subheader("🏆 Produk Terlaris")
            fig = create_product_sales_chart(transactions_df)
            st.plotly_chart(fig, use_container_width=True)

# ==================== DATA MASTER PAGE ====================
def data_master_page():
    """Halaman Data Master - FIXED Clean Version"""
    st.markdown("<h1 class='main-header'>📦 Data Master Produk</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "➕ Tambah", "📋 Lihat Data", "✏️ Edit", 
        "➕📦 Tambah Stok", "🗑️ Hapus", "🏷️ Generate Barcode"
    ])
    
    # TAB 1: TAMBAH PRODUK
    with tab1:
        st.subheader("Tambah Produk Baru")
        with st.form("form_tambah"):
            c1, c2 = st.columns(2)
            barcode_id = c1.text_input("Barcode ID *", placeholder="BRK001")
            nama_produk = c1.text_input("Nama Produk *", placeholder="Contoh: Aqua Botol")
            kategori = c1.selectbox("Kategori", ["Makanan", "Minuman", "Snack", "Alat Tulis", "Lainnya"])
            
            stok = c2.number_input("Stok Awal", min_value=0, value=0)
            harga_modal = c2.number_input("Harga Modal", min_value=0, step=100)
            harga_jual = c2.number_input("Harga Jual", min_value=0, step=100)
            
            if st.form_submit_button("Simpan Produk", use_container_width=True):
                if barcode_id and nama_produk:
                    if harga_jual > harga_modal:
                        res = add_product(barcode_id, nama_produk, kategori, stok, harga_modal, harga_jual)
                        if res['success']:
                            st.success(res['message'])
                            generate_barcode(barcode_id, nama_produk)
                        else:
                            st.error(res['message'])
                    else:
                        st.error("Harga jual harus lebih besar dari modal!")
                else:
                    st.error("Barcode ID dan Nama Produk wajib diisi!")

    # TAB 2: LIHAT DATA
    with tab2:
        st.subheader("Daftar Produk")
        df = load_products_data()
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data produk.")

    # TAB 3: EDIT PRODUK
    with tab3:
        st.subheader("Edit Produk")
        df = load_products_data()
        if not df.empty:
            pilih = st.selectbox("Pilih Produk Edit", df['barcode_id'].tolist())
            row = df[df['barcode_id'] == pilih].iloc[0]
            with st.form("edit_form"):
                n_nama = st.text_input("Nama", value=row['nama_produk'])
                n_kat = st.selectbox("Kategori", ["Makanan", "Minuman", "Snack", "Alat Tulis", "Lainnya"], index=["Makanan", "Minuman", "Snack", "Alat Tulis", "Lainnya"].index(row['kategori']))
                n_stok = st.number_input("Stok", value=int(row['stok']))
                n_modal = st.number_input("Modal", value=int(row['harga_modal']))
                n_jual = st.number_input("Jual", value=int(row['harga_jual']))
                
                if st.form_submit_button("Update Data"):
                    res = update_product(pilih, n_nama, n_kat, n_stok, n_modal, n_jual)
                    if res['success']:
                        st.success("Data berhasil diupdate!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(res['message'])

    # TAB 4: TAMBAH STOK
    with tab4:
        st.subheader("Tambah Stok Cepat")
        df = load_products_data()
        if not df.empty:
            pilih_stok = st.selectbox("Pilih Produk", df['barcode_id'].tolist(), key="stock_select")
            curr_row = df[df['barcode_id'] == pilih_stok].iloc[0]
            st.info(f"Stok saat ini: {curr_row['stok']}")
            tambah = st.number_input("Jumlah Tambah", min_value=1, value=10)
            if st.button("➕ Tambah Stok"):
                res = add_stock(pilih_stok, tambah)
                if res['success']:
                    st.success("Stok berhasil ditambah!")
                    time.sleep(1)
                    st.rerun()

    # TAB 5: HAPUS
    with tab5:
        st.subheader("Hapus Produk")
        df = load_products_data()
        if not df.empty:
            del_id = st.selectbox("Pilih Produk Hapus", df['barcode_id'].tolist(), key="del_select")
            if st.button(f"🗑️ Hapus {del_id}", type="primary"):
                res = delete_product(del_id)
                if res['success']:
                    st.success("Produk dihapus!")
                    time.sleep(1)
                    st.rerun()

    # TAB 6: GENERATE BARCODE (FIXED)
    with tab6:
        st.subheader("🏷️ Generate Barcode")
        df = load_products_data()
        
        if not df.empty:
            # 1. Hitung Barcode
            existing = 0
            missing_ids = []
            for idx, row in df.iterrows():
                if os.path.exists(f"barcodes/{row['barcode_id']}.png"):
                    existing += 1
                else:
                    missing_ids.append(row['barcode_id'])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Produk", len(df))
            c2.metric("Barcode Ada", existing)
            c3.metric("Belum Ada", len(missing_ids))
            
            st.markdown("---")
            
            # 2. Pilihan Mode (DILUAR LOOP - AMAN)
            mode = st.radio("Mode Generate:", ["Semua Produk", "Hanya yang Belum Ada"], key="barcode_mode_unique")
            
            # 3. Tombol Action
            if st.button("🚀 Generate Barcode", type="primary"):
                with st.spinner("Memproses..."):
                    target_df = df if mode == "Semua Produk" else df[df['barcode_id'].isin(missing_ids)]
                    if not target_df.empty:
                        res = generate_batch_barcodes(target_df)
                        if res['success']:
                            st.success(res['message'])
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(res['message'])
                    else:
                        st.info("Tidak ada data yang perlu diproses.")

            # 4. Gallery Barcode
            st.markdown("### 📂 Galeri Barcode")
            if os.path.exists("barcodes"):
                files = [f for f in os.listdir("barcodes") if f.endswith(".png")]
                if files:
                    # Tampilkan max 8 barcode terbaru agar tidak berat
                    cols = st.columns(4)
                    for i, f in enumerate(files[:8]): 
                        with cols[i % 4]:
                            st.image(f"barcodes/{f}", caption=f.replace('.png',''))
                    
                    if st.button("📥 Download ZIP Semua Barcode"):
                         res = export_barcodes_zip()
                         if res['success']:
                             with open(res['zip_path'], "rb") as fp:
                                 st.download_button("Klik Download ZIP", fp, "barcodes.zip", "application/zip")

def initialize_cart():
    """Initialize cart in session state if not exists"""
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'last_scan' not in st.session_state:
        st.session_state.last_scan = None
        
# Scan Barcode page
# Scan Barcode page - FIXED VERSION
def scan_page():
    """
    Halaman Scan dengan CART SYSTEM
    User bisa scan multiple produk sebelum checkout
    """
    initialize_cart()
    
    # Custom CSS
    st.markdown("""
        <style>
        .scan-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .cart-badge {
            background: #f44336;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9rem;
            display: inline-block;
        }
        
        .cart-item {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .cart-summary {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-top: 1rem;
        }
        
        .scan-method-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .scan-method-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }
        
        .product-preview {
            background: #f5f7fa;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header with cart badge
    cart_totals = calculate_cart_totals()
    
    col_title, col_cart_badge = st.columns([4, 1])
    
    with col_title:
        st.markdown("""
            <div class="scan-header">
                <h1>🛒 Scan Multiple Products</h1>
                <p style="font-size: 1.1rem; margin-top: 0.5rem;">
                    Scan/input produk → Tambah ke cart → Checkout sekali
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_cart_badge:
        if cart_totals['total_items'] > 0:
            st.markdown(f"""
                <div style="text-align: center; padding-top: 1rem;">
                    <div style="font-size: 2rem;">🛒</div>
                    <span class="cart-badge">{cart_totals['total_items']} items</span>
                </div>
            """, unsafe_allow_html=True)
    
    # Check scanner
    availability = check_scanner_availability()
    
    # === SCANNING SECTION ===
    st.markdown("## 📷 Scan / Input Produk")
    
    col_method1, col_method2 = st.columns(2)
    
    # Real-Time Scanner
    with col_method1:
        st.markdown("""
            <div class="scan-method-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📷</div>
                <h3 style="color: #667eea;">Real-Time Scanner</h3>
                <p style="color: #666; font-size: 0.9rem;">
                    Live preview, auto-detect
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if availability['available']:
            if st.button("🚀 Buka Scanner", 
                        type="primary", 
                        use_container_width=True,
                        key="btn_scanner"):
                with st.spinner("📷 Membuka scanner..."):
                    result = scan_barcode_realtime()
                
                if result['success']:
                    st.session_state.last_scan = result['barcode_id']
                    st.success(f"✅ Scan berhasil: {result['barcode_id']}")
                    st.rerun()
                else:
                    st.error(result['message'])
        else:
            st.warning("⚠️ Scanner tidak tersedia")
    
    # Manual Input
    with col_method2:
        st.markdown("""
            <div class="scan-method-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⌨️</div>
                <h3 style="color: #764ba2;">Input Manual</h3>
                <p style="color: #666; font-size: 0.9rem;">
                    Ketik barcode ID langsung
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        barcode_input = st.text_input(
            "Barcode ID",
            placeholder="BRK001, BRK002, ...",
            key="manual_input",
            label_visibility="collapsed"
        )
        
        if st.button("🔍 Cari", 
                    type="primary", 
                    use_container_width=True,
                    key="btn_search"):
            if barcode_input.strip():
                st.session_state.last_scan = barcode_input.strip()
                st.rerun()
            else:
                st.warning("⚠️ Masukkan Barcode ID!")
    
    # === PRODUCT PREVIEW & ADD TO CART ===
    if st.session_state.last_scan:
        st.markdown("---")
        st.markdown("## 📦 Detail Produk")
        
        product = get_product_by_barcode(st.session_state.last_scan)
        
        if product is not None:
            col_preview, col_action = st.columns([2, 1])
            
            with col_preview:
                st.markdown(f"""
                    <div class="product-preview">
                        <h3 style="margin-bottom: 0.5rem;">{product['nama_produk']}</h3>
                        <p style="color: #666; margin-bottom: 1rem;">
                            <strong>Barcode:</strong> {product['barcode_id']} | 
                            <strong>Kategori:</strong> {product['kategori']} | 
                            <strong>Stok:</strong> {product['stok']} pcs
                        </p>
                        <p style="font-size: 1.2rem; color: #4CAF50; font-weight: bold;">
                            {format_currency(product['harga_jual'])} / pcs
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_action:
                max_stock = int(product['stok'])
                
                # Check cart quantity
                cart_qty = 0
                for item in st.session_state.cart:
                    if item['barcode_id'] == product['barcode_id']:
                        cart_qty = item['quantity']
                        break
                
                available = max_stock - cart_qty
                
                if available > 0:
                    qty = st.number_input(
                        "Jumlah",
                        min_value=1,
                        max_value=available,
                        value=1,
                        key="qty_add",
                        help=f"Tersedia: {available} pcs"
                    )
                    
                    if st.button("➕ Tambah ke Cart", 
                                type="primary",
                                use_container_width=True,
                                key="btn_add_cart"):
                        result = add_to_cart(product, qty)
                        
                        if result['success']:
                            st.success(result['message'])
                            st.session_state.last_scan = None
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(result['message'])
                else:
                    st.error(f"❌ Stok habis!\n({cart_qty} sudah di cart)")
                    if st.button("🔄 Cari Produk Lain", use_container_width=True):
                        st.session_state.last_scan = None
                        st.rerun()
        else:
            st.error(f"❌ Produk tidak ditemukan: {st.session_state.last_scan}")
            if st.button("🔄 Coba Lagi", use_container_width=True):
                st.session_state.last_scan = None
                st.rerun()
    
    # === SHOPPING CART ===
    st.markdown("---")
    st.markdown("## 🛒 Shopping Cart")
    
    if st.session_state.cart:
        # Display cart items
        for idx, item in enumerate(st.session_state.cart):
            col_item, col_remove = st.columns([5, 1])
            
            with col_item:
                st.markdown(f"""
                    <div class="cart-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 1.1rem;">{item['nama_produk']}</strong>
                                <p style="color: #666; margin: 0.3rem 0;">
                                    {item['quantity']} pcs × {format_currency(item['harga_satuan'])}
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <strong style="font-size: 1.2rem; color: #4CAF50;">
                                    {format_currency(item['subtotal'])}
                                </strong>
                                <p style="color: #888; font-size: 0.85rem; margin: 0;">
                                    Profit: {format_currency(item['profit'])}
                                </p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_remove:
                if st.button("🗑️", key=f"remove_{idx}", help="Hapus item"):
                    result = remove_from_cart(idx)
                    if result['success']:
                        st.success(result['message'])
                        time.sleep(0.3)
                        st.rerun()
        
        # Cart Summary
        st.markdown(f"""
            <div class="cart-summary">
                <h3 style="margin-bottom: 1rem;">💰 Ringkasan Cart</h3>
                <table style="width: 100%; color: white;">
                    <tr>
                        <td><strong>Total Items:</strong></td>
                        <td style="text-align: right;">{cart_totals['total_items']} produk</td>
                    </tr>
                    <tr>
                        <td><strong>Total Quantity:</strong></td>
                        <td style="text-align: right;">{cart_totals['total_quantity']} pcs</td>
                    </tr>
                    <tr style="border-top: 2px solid rgba(255,255,255,0.3);">
                        <td><strong style="font-size: 1.2rem;">TOTAL HARGA:</strong></td>
                        <td style="text-align: right; font-size: 1.3rem;">
                            <strong>{format_currency(cart_totals['total_price'])}</strong>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Keuntungan:</strong></td>
                        <td style="text-align: right; font-size: 1.1rem;">
                            {format_currency(cart_totals['total_profit'])}
                        </td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("<br>", unsafe_allow_html=True)
        col_clear, col_checkout = st.columns(2)
        
        with col_clear:
            if st.button("🗑️ Kosongkan Cart", 
                        use_container_width=True,
                        key="btn_clear"):
                result = clear_cart()
                st.info(result['message'])
                time.sleep(0.5)
                st.rerun()
        
        with col_checkout:
            if st.button("💳 CHECKOUT", 
                        type="primary",
                        use_container_width=True,
                        key="btn_checkout"):
                with st.spinner("💳 Processing checkout..."):
                    result = process_checkout()
                
                if result['success']:
                    st.success("### ✅ CHECKOUT BERHASIL!")
                    
                    # Show summary
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    
                    with col_s1:
                        st.metric("Items", result['total_items'])
                    with col_s2:
                        st.metric("Quantity", f"{result['total_quantity']} pcs")
                    with col_s3:
                        st.metric("Total", format_currency(result['total_price']))
                    with col_s4:
                        st.metric("Profit", format_currency(result['total_profit']))
                    
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(result['message'])
    
    else:
        st.info("""
            ### 🛒 Cart Kosong
            
            Scan atau input produk untuk mulai berbelanja!
            
            **Cara Kerja:**
            1. Scan/input barcode produk
            2. Pilih jumlah
            3. Klik "Tambah ke Cart"
            4. Ulangi untuk produk lain
            5. Review cart
            6. Klik "CHECKOUT" untuk proses semua transaksi
        """)

# Laporan page
def laporan_page():
    st.markdown("<h1 class='main-header'>📊 Laporan & Statistik</h1>", unsafe_allow_html=True)
    
    transactions_df = load_transactions_data()
    products_df = load_products_data()
    
    if not transactions_df.empty:
        # Filter tanggal
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Dari Tanggal", value=datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("Sampai Tanggal", value=datetime.now())
        with col3:
            st.write("")
            st.write("")
            if st.button("🔍 Filter", use_container_width=True):
                st.rerun()
        
        # Filter data
        transactions_df['tanggal'] = pd.to_datetime(transactions_df['waktu']).dt.date
        mask = (transactions_df['tanggal'] >= start_date) & (transactions_df['tanggal'] <= end_date)
        filtered_df = transactions_df[mask]
        
        if not filtered_df.empty:
            # Summary Statistics
            st.subheader("📈 Ringkasan Periode")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Transaksi", len(filtered_df))
            with col2:
                st.metric("Total Pendapatan", format_currency(filtered_df['total_harga'].sum()))
            with col3:
                st.metric("Total Keuntungan", format_currency(filtered_df['keuntungan'].sum()))
            with col4:
                avg_transaction = filtered_df['total_harga'].mean()
                st.metric("Rata-rata Transaksi", format_currency(avg_transaction))
            
            st.markdown("---")
            
            # Grafik
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Penjualan", "💰 Keuntungan", "🏆 Produk Terlaris", "📋 Detail Transaksi"])
            
            with tab1:
                fig = create_sales_chart(filtered_df)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = create_profit_chart(filtered_df)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                fig = create_product_sales_chart(filtered_df)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.dataframe(filtered_df.sort_values('waktu', ascending=False), 
                           use_container_width=True, hide_index=True)
            
            # Export
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("📥 Export ke Excel", use_container_width=True):
                    path = export_to_excel(filtered_df, "laporan_transaksi")
                    if path:
                        st.success(f"✅ Export berhasil: {path}")
        else:
            st.warning("⚠️ Tidak ada transaksi pada periode yang dipilih")
    else:
        st.info("📝 Belum ada transaksi. Lakukan transaksi pertama untuk melihat laporan.")

# Settings page
def settings_page():
    st.markdown("<h1 class='main-header'>⚙️ Pengaturan & Utilitas</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💾 Backup", "📤 Export Data", "ℹ️ Info Aplikasi"])
    
    # Tab Backup
    with tab1:
        st.subheader("Backup & Restore Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Backup Manual")
            if st.button("💾 Backup Sekarang", use_container_width=True):
                result = auto_backup_all()
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])
        
        with col2:
            st.markdown("### Bersihkan Backup Lama")
            days = st.number_input("Hapus backup lebih dari (hari)", min_value=1, value=7)
            if st.button("🧹 Bersihkan", use_container_width=True):
                result = clean_old_backups(days)
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])
        
        # List backup files
        st.markdown("---")
        st.subheader("Daftar Backup")
        backup_folder = "data/backup"
        if os.path.exists(backup_folder):
            files = os.listdir(backup_folder)
            if files:
                for file in sorted(files, reverse=True):
                    file_path = os.path.join(backup_folder, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    st.text(f"📄 {file} - {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.info("Belum ada backup")
        else:
            st.info("Folder backup belum ada")
    
    # Tab Export
    with tab2:
        st.subheader("Export Data ke Excel/CSV")
        
        products_df = load_products_data()
        transactions_df = load_transactions_data()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Data Produk")
            if not products_df.empty:
                st.write(f"Total: {len(products_df)} produk")
                if st.button("📥 Export Produk (Excel)", use_container_width=True):
                    path = export_to_excel(products_df, "products")
                    if path:
                        st.success(f"✅ Export berhasil: {path}")
        
        with col2:
            st.markdown("### Data Transaksi")
            if not transactions_df.empty:
                st.write(f"Total: {len(transactions_df)} transaksi")
                if st.button("📥 Export Transaksi (Excel)", use_container_width=True):
                    path = export_to_excel(transactions_df, "transactions")
                    if path:
                        st.success(f"✅ Export berhasil: {path}")
    
    # Tab Info
    with tab3:
        st.subheader("Informasi Aplikasi")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📱 Aplikasi
            - **Nama:** Kantin Sekolah Manager
            - **Versi:** 1.0.0 Enhanced
            - **Framework:** Streamlit
            - **Database:** CSV (Offline)
            
            ### 🎯 Fitur Utama
            - ✅ CRUD Data Produk
            - ✅ Generate & Scan Barcode
            - ✅ Dashboard Real-time
            - ✅ Laporan & Statistik
            - ✅ Backup & Export Data
            - ✅ Alert Stok Menipis
            """)
        
        with col2:
            st.markdown("""
            ### 🛠️ Teknologi
            - Python 3.8+
            - Streamlit 1.31
            - Pandas 2.1
            - Plotly 5.18
            - Python-barcode 0.15
            - OpenCV & Pyzbar (optional)
            
            ### 📊 Statistik Aplikasi
            """)
            
            products_df = load_products_data()
            transactions_df = load_transactions_data()
            
            st.metric("Total Produk Terdaftar", len(products_df))
            st.metric("Total Transaksi", len(transactions_df))
            
            if not transactions_df.empty:
                total_revenue = transactions_df['total_harga'].sum()
                st.metric("Total Pendapatan All Time", format_currency(total_revenue))
        
        st.markdown("---")
        
        # System info
        st.subheader("💻 Informasi Sistem")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Python Version:**\n{sys.version.split()[0]}")
        with col2:
            st.info(f"**Streamlit Version:**\n{st.__version__}")
        with col3:
            availability = check_scanner_availability()
            status = "✅ Available" if availability['available'] else "❌ Not Available"
            st.info(f"**Barcode Scanner:**\n{status}")
        
        # Credits
        st.markdown("---")
        st.markdown("""
        ### 👥 Credits
        **Dibuat untuk:**
        - Tugas Pemrograman Terstruktur
        - Solusi digitalisasi kantin sekolah
        
        **Dikembangkan dengan:**
        - ❤️ Python & Streamlit
        - 📚 Paradigma Pemrograman Terstruktur
        - 🎯 100% Offline & CSV-based
        
        ---
        *© 2024 Kantin Sekolah Manager - All Rights Reserved*
        """)

# Main application
def main():
    load_custom_css()
    init_session_state()
    
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Sidebar
    with st.sidebar:
        st.title("🏪 Kantin Manager")
        st.write(f"👤 User: **{st.session_state.username}**")
        
        # Quick stats
        products_df = load_products_data()
        transactions_df = load_transactions_data()
        
        if not products_df.empty:
            st.metric("Produk", len(products_df), delta=None)
            low_stock = len(products_df[products_df['stok'] < 10])
            if low_stock > 0:
                st.warning(f"⚠️ {low_stock} stok menipis")
        
        st.markdown("---")
        
        menu = st.radio(
            "📍 Menu Navigasi",
            [
                "📊 Dashboard", 
                "📦 Data Master", 
                "📷 Scan Barcode", 
                "📊 Laporan", 
                "⚙️ Pengaturan"
            ]
        )
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("💾 Backup Data", use_container_width=True):
            result = auto_backup_all()
            if result['success']:
                st.success("✅ Backup berhasil!")
            else:
                st.error("❌ Backup gagal!")
        
        st.markdown("---")
        
        # Info
        st.info("💡 **Tips:**\nGunakan shortcut keyboard untuk navigasi lebih cepat!")
        
        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.last_scan = None
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.caption("v1.0.0 Enhanced")
        st.caption("© 2024 Kantin Manager")
    
    # Routing
    if menu == "📊 Dashboard":
        dashboard_page()
    elif menu == "📦 Data Master":
        data_master_page()
    elif menu == "📷 Scan Barcode":
        scan_page()
    elif menu == "📊 Laporan":
        laporan_page()
    elif menu == "⚙️ Pengaturan":
        settings_page()

if __name__ == "__main__":
    import sys
    main()