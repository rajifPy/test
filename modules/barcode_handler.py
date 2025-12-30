"""
BARCODE HANDLER - FIXED RECURSION ERROR
Scanner dengan preview 400x400 dan color feedback
Version: 10.0 - No Recursion Loop
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
    print("   Preview: 400x400 with visual feedback")
else:
    print("❌ SCANNER NOT AVAILABLE")
    print("   📥 Install: pip install streamlit-qrcode-scanner==0.1.2")
print("=" * 60)
print()

# ==================== QRCODE SCANNER FUNCTION ====================

if SCANNER_READY:
    def scan_barcode_realtime():
        """
        Enhanced barcode scanner dengan visual feedback
        FIXED: No recursion - return barcode_data instead of rerun
        
        Returns:
            str or None: barcode data if detected, None otherwise
        """
        # Custom CSS untuk scanner area dengan visual feedback
        st.markdown("""
            <style>
            /* Scanner Container */
            .stApp [data-testid="stVerticalBlock"] iframe {
                min-height: 400px !important;
                min-width: 400px !important;
                border-radius: 15px;
            }
            
            /* Scanner Frame - Scanning State (Yellow) */
            .scanner-frame-scanning {
                border: 5px solid #FFC107;
                border-radius: 15px;
                padding: 10px;
                background: linear-gradient(135deg, #FFF9C4 0%, #FFEB3B 100%);
                box-shadow: 0 0 20px rgba(255, 193, 7, 0.5);
                animation: pulse-yellow 1.5s infinite;
            }
            
            /* Scanner Frame - Success State (Green) */
            .scanner-frame-success {
                border: 5px solid #4CAF50;
                border-radius: 15px;
                padding: 10px;
                background: linear-gradient(135deg, #C8E6C9 0%, #4CAF50 100%);
                box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
                animation: pulse-green 0.5s;
            }
            
            /* Scanner Frame - Default State */
            .scanner-frame-default {
                border: 3px solid #667eea;
                border-radius: 15px;
                padding: 10px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            
            @keyframes pulse-yellow {
                0%, 100% { 
                    box-shadow: 0 0 20px rgba(255, 193, 7, 0.5);
                    transform: scale(1);
                }
                50% { 
                    box-shadow: 0 0 40px rgba(255, 193, 7, 0.8);
                    transform: scale(1.02);
                }
            }
            
            @keyframes pulse-green {
                0% { 
                    box-shadow: 0 0 0px rgba(76, 175, 80, 0);
                    transform: scale(1);
                }
                50% { 
                    box-shadow: 0 0 60px rgba(76, 175, 80, 1);
                    transform: scale(1.05);
                }
                100% { 
                    box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
                    transform: scale(1);
                }
            }
            
            /* Status Indicator */
            .scan-status {
                text-align: center;
                font-size: 1.2rem;
                font-weight: bold;
                padding: 0.5rem;
                border-radius: 10px;
                margin-bottom: 1rem;
            }
            
            .scan-status-scanning {
                background: #FFF9C4;
                color: #F57F17;
                border: 2px solid #FFC107;
            }
            
            .scan-status-success {
                background: #C8E6C9;
                color: #2E7D32;
                border: 2px solid #4CAF50;
            }
            
            .scan-status-waiting {
                background: #E3F2FD;
                color: #1565C0;
                border: 2px solid #2196F3;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize scan state
        if 'scanner_state' not in st.session_state:
            st.session_state.scanner_state = 'waiting'
        
        # Initialize last detected barcode
        if 'last_detected_barcode' not in st.session_state:
            st.session_state.last_detected_barcode = None
        
        # Determine frame class based on state
        if st.session_state.scanner_state == 'scanning':
            frame_class = "scanner-frame-scanning"
            status_class = "scan-status-scanning"
            status_icon = "🟡"
            status_text = "SCANNING..."
        elif st.session_state.scanner_state == 'success':
            frame_class = "scanner-frame-success"
            status_class = "scan-status-success"
            status_icon = "🟢"
            status_text = "BERHASIL!"
        else:
            frame_class = "scanner-frame-default"
            status_class = "scan-status-waiting"
            status_icon = "🔵"
            status_text = "READY"
        
        # Status indicator
        st.markdown(f"""
            <div class="scan-status {status_class}">
                <div style="font-size: 2rem; margin-bottom: 0.3rem;">{status_icon}</div>
                <div>{status_text}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Scanner container with visual feedback
        st.markdown(f'<div class="{frame_class}">', unsafe_allow_html=True)
        
        # Call scanner - Library akan tampilkan button dan camera
        barcode_data = qrcode_scanner(key='barcode-scanner')
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # FIXED: Return barcode data instead of calling st.rerun()
        if barcode_data:
            # Only process if it's a NEW barcode (prevent duplicates)
            if barcode_data != st.session_state.last_detected_barcode:
                st.session_state.scanner_state = 'success'
                st.session_state.last_detected_barcode = barcode_data
                
                # Success feedback
                st.success(f"✅ **SCAN BERHASIL!**")
                st.code(barcode_data, language="text")
                
                # Return the barcode data
                return barcode_data
            else:
                # Same barcode, don't process again
                st.session_state.scanner_state = 'scanning'
                return None
        else:
            # Set state to scanning when camera active
            if st.session_state.scanner_state != 'success':
                st.session_state.scanner_state = 'scanning'
            return None
else:
    # Fallback jika library tidak tersedia
    def scan_barcode_realtime():
        """Fallback function"""
        st.error("""
            ⚠️ **Scanner tidak tersedia**
            
            📦 Install library:
            ```bash
            pip install streamlit-qrcode-scanner==0.1.2
            ```
            
            💡 **ALTERNATIF:** Gunakan 'Input Manual'
        """)
        return None

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
        message = "✅ Scanner siap: 400x400 preview dengan visual feedback\n" + \
                 "   🟡 Kuning = Scanning | 🟢 Hijau = Berhasil"
    else:
        message = "❌ Install: pip install streamlit-qrcode-scanner==0.1.2"
    
    return {
        'available': SCANNER_READY,
        'message': message,
        'method': 'qrcode-scanner-js' if SCANNER_READY else None,
        'requires_https': True
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
    print(f"   Preview: 400x400 with visual feedback")
    print(f"   Visual: 🟡 Yellow (scanning) | 🟢 Green (success)")
    print(f"   FIXED: No recursion loop")
else:
    print(f"   Install: pip install streamlit-qrcode-scanner==0.1.2")
print()
