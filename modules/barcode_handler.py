"""
BARCODE HANDLER - STREAMLIT-QRCODE-SCANNER VERSION
Ultra simple barcode scanning menggunakan JavaScript-based scanner
NO OpenCV, NO dependencies, Works in browser!
Version: 7.0 - QRCode Scanner Implementation
"""

import barcode
from barcode.writer import ImageWriter
import os
import streamlit as st

# ==================== LIBRARY DETECTION ====================

print("=" * 60)
print("🔍 DETECTING SCANNER LIBRARIES...")
print("=" * 60)

# QRCode Scanner Detection
QRCODE_SCANNER_AVAILABLE = False
try:
    from streamlit_qrcode_scanner import qrcode_scanner
    QRCODE_SCANNER_AVAILABLE = True
    print(f"✅ Streamlit-QRCode-Scanner: Available")
    print(f"   Method: JavaScript-based (HTML5 getUserMedia)")
except ImportError as e:
    print(f"❌ Streamlit-QRCode-Scanner: {e}")
    print(f"   Install: pip install streamlit-qrcode-scanner==0.1.2")

# Final Status
SCANNER_READY = QRCODE_SCANNER_AVAILABLE

print("\n" + "=" * 60)
if SCANNER_READY:
    print("✅ SCANNER READY: JavaScript-based QRCode Scanner")
    print("   Method: HTML5 getUserMedia API")
    print("   Formats: QR Code, Code128, EAN, UPC, dan lainnya")
    print("   Platform: Browser-based (Chrome, Firefox, Safari)")
else:
    print("❌ SCANNER NOT AVAILABLE")
    print("   📥 Install: pip install streamlit-qrcode-scanner==0.1.2")
print("=" * 60)
print()

# ==================== QRCODE SCANNER FUNCTION ====================

if SCANNER_READY:
    def scan_barcode_realtime():
        """
        Real-time barcode scanner menggunakan streamlit-qrcode-scanner
        Ultra simple - hanya 3 baris code!
        
        Returns:
            dict: {'success': bool, 'barcode_id': str, 'message': str}
        """
        # Info
        st.markdown("### 📷 JavaScript Barcode Scanner")
        
        # Scan barcode
        st.markdown("#### 🎯 Scan Barcode")
        
        # Call scanner (3 baris aja!)
        barcode_data = qrcode_scanner(key='barcode-scanner')
        
        # Handle result
        if barcode_data:
            st.success(f"✅ **BARCODE DETECTED!**")
            st.code(barcode_data, language="text")
            
            # Return result
            return {
                'success': True,
                'barcode_id': barcode_data,
                'message': f"✅ Scan berhasil: {barcode_data}"
            }
        else:
            st.warning("⊙ **WAITING FOR SCAN...**\n\nKlik tombol 'Start Scanning' untuk mulai")
            
            return {
                'success': False,
                'message': "Scan belum dilakukan atau dibatalkan"
            }
else:
    # Fallback jika library tidak tersedia
    def scan_barcode_realtime():
        """Fallback function"""
        error_msg = "⚠️ Scanner tidak tersedia.\n\n" + \
                   "📦 Install library:\n" + \
                   "   pip install streamlit-qrcode-scanner==0.1.2\n\n" + \
                   "💡 ALTERNATIF: Gunakan 'Input Manual'"
        
        st.error(error_msg)
        return {
            'success': False,
            'message': error_msg
        }

# ==================== BARCODE GENERATION ====================

def generate_barcode(barcode_id, product_name):
    """Generate barcode Code128 PNG"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        barcodes_folder = os.path.join(project_root, "barcodes")
        os.makedirs(barcodes_folder, exist_ok=True)
        
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_id, writer=ImageWriter())
        
        filename = os.path.join(barcodes_folder, barcode_id)
        full_path = barcode_instance.save(filename)
        
        return full_path
    except Exception as e:
        print(f"Generate barcode error: {e}")
        return None

def generate_batch_barcodes(products_df):
    """Batch generate barcodes"""
    try:
        success_count = 0
        failed_items = []
        
        for index, row in products_df.iterrows():
            result = generate_barcode(row['barcode_id'], row['nama_produk'])
            if result:
                success_count += 1
            else:
                failed_items.append(row['barcode_id'])
        
        return {
            'success': True,
            'total': len(products_df),
            'success_count': success_count,
            'failed_items': failed_items,
            'message': f"Generate {success_count}/{len(products_df)} berhasil"
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

# ==================== UTILITY ====================

def check_scanner_availability():
    """Check and return scanner status"""
    
    if SCANNER_READY:
        message = "✅ Scanner siap: JavaScript-based QRCode Scanner\n" + \
                 "   Works in browser, no OpenCV needed!"
    else:
        message = "❌ Install: pip install streamlit-qrcode-scanner==0.1.2"
    
    return {
        'available': SCANNER_READY,
        'message': message,
        'method': 'qrcode-scanner-js' if SCANNER_READY else None,
        'requires_https': True  # For production
    }

def validate_barcode_format(barcode_id):
    """Validate barcode format"""
    try:
        if not barcode_id or len(barcode_id) < 3:
            return False
        if ' ' in barcode_id:
            return False
        return True
    except:
        return False

# ==================== MODULE INFO ====================

print("📦 Barcode Handler Module Loaded")
print(f"   Scanner: {'✅ Ready' if SCANNER_READY else '❌ Not Available'}")
if SCANNER_READY:
    print(f"   Method: JavaScript-based (streamlit-qrcode-scanner)")
    print(f"   Platform: Browser HTML5 API")
    print(f"   Formats: QR, Code128, EAN, UPC, Code39, Code93, ITF")
    print(f"   Note: Requires HTTPS for production deployment")
else:
    print(f"   Install: pip install streamlit-qrcode-scanner==0.1.2")
print()
