"""
BARCODE HANDLER - WITH STREAMLIT PREVIEW
Real-time camera preview di Streamlit (400x400px minimum)
Status: Success (hijau) / Error (merah)
Version: 4.0 - Streamlit Preview
"""

import barcode
from barcode.writer import ImageWriter
import os
import time
import cv2
import numpy as np
import streamlit as st
from PIL import Image

# ==================== SCANNER DETECTION ====================

print("=" * 60)
print("🔍 DETECTING SCANNER LIBRARIES...")
print("=" * 60)

# OpenCV Detection
OPENCV_AVAILABLE = False
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
    print(f"✅ OpenCV: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV: {e}")

# Scanner Method Detection - PRIORITAS INTERNET BASED
SCANNER_METHOD = None
SCANNER_ERROR = ""
SCANNER_LIB = None

# Method 1: Pyzxing (PRIORITY - Windows friendly, gunakan internet)
print("\n[1/3] Checking Pyzxing (Internet-based, Windows friendly)...")
try:
    from pyzxing import BarCodeReader
    reader = BarCodeReader()
    SCANNER_METHOD = "pyzxing"
    SCANNER_LIB = reader
    print("✅ Pyzxing: Available (ACTIVE METHOD)")
except Exception as e:
    error_msg = str(e)
    print(f"⚠️ Pyzxing: {error_msg}")
    SCANNER_ERROR = error_msg
    
    # Method 2: Pyzbar (Fallback 1 - butuh DLL)
    if SCANNER_METHOD is None:
        print("\n[2/3] Checking Pyzbar (Local library)...")
        try:
            from pyzbar.pyzbar import decode as pyzbar_decode
            SCANNER_METHOD = "pyzbar"
            SCANNER_LIB = pyzbar_decode
            print("✅ Pyzbar: Available (ACTIVE METHOD)")
        except Exception as e:
            print(f"⚠️ Pyzbar: {e}")
            
            # Method 3: OpenCV Barcode (Fallback 2 - built-in)
            if SCANNER_METHOD is None and OPENCV_AVAILABLE:
                print("\n[3/3] Checking OpenCV Barcode Detector...")
                try:
                    # OpenCV 4.5+ punya barcode module
                    if hasattr(cv2, 'barcode'):
                        detector = cv2.barcode.BarcodeDetector()
                        SCANNER_METHOD = "opencv_barcode"
                        SCANNER_LIB = detector
                        print("✅ OpenCV Barcode: Available (ACTIVE METHOD)")
                    else:
                        print("⚠️ OpenCV Barcode: Module not available (need opencv-contrib)")
                except Exception as e:
                    print(f"⚠️ OpenCV Barcode: {e}")

# Final Status
WEBCAM_AVAILABLE = OPENCV_AVAILABLE and SCANNER_METHOD is not None

print("\n" + "=" * 60)
if WEBCAM_AVAILABLE:
    print(f"✅ SCANNER READY: {SCANNER_METHOD.upper()}")
    if SCANNER_METHOD == "pyzxing":
        print("   📡 Menggunakan API online (butuh internet)")
        print("   🌐 Akan auto-download JAR file jika belum ada")
else:
    print("❌ SCANNER NOT AVAILABLE")
    if SCANNER_ERROR:
        print(f"   Error: {SCANNER_ERROR}")
    print("\n   📥 SOLUSI:")
    print("   1. Install pyzxing: pip install pyzxing")
    print("   2. Pastikan internet aktif (untuk download JAR)")
    print("   3. Atau install pyzbar: pip install pyzbar")
print("=" * 60)
print()

# ==================== SCANNING METHODS ====================

def scan_frame_pyzxing(frame, temp_path="temp_scan.jpg"):
    """Scan using pyzxing (Internet-based API)"""
    try:
        cv2.imwrite(temp_path, frame)
        results = reader.decode(temp_path)
        
        if results and len(results) > 0:
            barcode_data = results[0].get('parsed', None)
            if barcode_data:
                return barcode_data
        return None
        
    except Exception as e:
        if "404" not in str(e):
            print(f"Pyzxing error: {e}")
        return None
        
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

def scan_frame_pyzbar(frame):
    """Scan using pyzbar (Local library)"""
    try:
        decoded_objects = pyzbar_decode(frame)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        return None
    except Exception as e:
        print(f"Pyzbar error: {e}")
        return None

def scan_frame_opencv(frame):
    """Scan using OpenCV built-in barcode detector"""
    try:
        ok, decoded_info, decoded_type, points = SCANNER_LIB.detectAndDecode(frame)
        if ok and decoded_info:
            return decoded_info
        return None
    except Exception as e:
        print(f"OpenCV error: {e}")
        return None

def scan_frame(frame):
    """Universal scanner - auto-select best method"""
    if SCANNER_METHOD == "pyzxing":
        return scan_frame_pyzxing(frame)
    elif SCANNER_METHOD == "pyzbar":
        return scan_frame_pyzbar(frame)
    elif SCANNER_METHOD == "opencv_barcode":
        return scan_frame_opencv(frame)
    return None

# ==================== STREAMLIT PREVIEW SCANNER ====================

def draw_scan_overlay(frame, status="scanning", barcode_data=None):
    """
    Draw overlay on frame for Streamlit preview
    Status: scanning (kuning), detected (hijau), error (merah)
    """
    height, width = frame.shape[:2]
    frame_copy = frame.copy()
    
    # Color based on status
    if status == "detected":
        color = (0, 255, 0)  # Green
        status_text = "✓ SUCCESS"
    elif status == "error":
        color = (0, 0, 255)  # Red
        status_text = "✗ ERROR"
    else:  # scanning
        color = (0, 255, 255)  # Yellow
        status_text = "⊙ SCANNING..."
    
    # Scan area (center, 60% of frame)
    scan_w = int(width * 0.6)
    scan_h = int(height * 0.4)
    scan_x = (width - scan_w) // 2
    scan_y = (height - scan_h) // 2
    
    # Semi-transparent overlay outside scan area
    overlay = frame_copy.copy()
    cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
    
    # Create mask for scan area
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.rectangle(mask, (scan_x, scan_y), (scan_x + scan_w, scan_y + scan_h), 255, -1)
    
    # Apply overlay (50% transparency)
    frame_copy = cv2.addWeighted(overlay, 0.4, frame_copy, 0.6, 0)
    frame_copy = np.where(mask[:, :, np.newaxis] == 255, frame, frame_copy)
    
    # Draw scan area border
    cv2.rectangle(frame_copy, (scan_x, scan_y), (scan_x + scan_w, scan_y + scan_h), color, 3)
    
    # Corner markers
    corner_len = 40
    corner_thick = 4
    
    # Top-left
    cv2.line(frame_copy, (scan_x, scan_y), (scan_x + corner_len, scan_y), color, corner_thick)
    cv2.line(frame_copy, (scan_x, scan_y), (scan_x, scan_y + corner_len), color, corner_thick)
    # Top-right
    cv2.line(frame_copy, (scan_x + scan_w, scan_y), (scan_x + scan_w - corner_len, scan_y), color, corner_thick)
    cv2.line(frame_copy, (scan_x + scan_w, scan_y), (scan_x + scan_w, scan_y + corner_len), color, corner_thick)
    # Bottom-left
    cv2.line(frame_copy, (scan_x, scan_y + scan_h), (scan_x + corner_len, scan_y + scan_h), color, corner_thick)
    cv2.line(frame_copy, (scan_x, scan_y + scan_h), (scan_x, scan_y + scan_h - corner_len), color, corner_thick)
    # Bottom-right
    cv2.line(frame_copy, (scan_x + scan_w, scan_y + scan_h), (scan_x + scan_w - corner_len, scan_y + scan_h), color, corner_thick)
    cv2.line(frame_copy, (scan_x + scan_w, scan_y + scan_h), (scan_x + scan_w, scan_y + scan_h - corner_len), color, corner_thick)
    
    # Scanning line animation
    if status == "scanning":
        animation = int((scan_h // 2) + (scan_h * 0.3 * np.sin(time.time() * 4)))
        scan_line_y = scan_y + animation
        cv2.line(frame_copy, (scan_x, scan_line_y), (scan_x + scan_w, scan_line_y), color, 2)
    
    # Status bar at top
    bar_h = 60
    cv2.rectangle(frame_copy, (0, 0), (width, bar_h), (30, 30, 30), -1)
    
    # Status text
    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_x = (width - text_size[0]) // 2
    cv2.putText(frame_copy, status_text, (text_x, 38), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Barcode result (if detected)
    if status == "detected" and barcode_data:
        # Result box at bottom
        result_h = 70
        result_y = height - result_h
        cv2.rectangle(frame_copy, (0, result_y), (width, height), (0, 200, 0), -1)
        cv2.rectangle(frame_copy, (0, result_y), (width, height), (0, 255, 0), 3)
        
        # Barcode text
        text = f"BARCODE: {barcode_data}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        text_x = (width - text_size[0]) // 2
        cv2.putText(frame_copy, text, (text_x, result_y + 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    
    return frame_copy

def scan_barcode_realtime():
    """
    Real-time barcode scanner dengan Streamlit preview
    Minimum preview size: 400x400px
    Status colors: Success (hijau), Error (merah), Scanning (kuning)
    
    Returns:
        dict: {'success': bool, 'barcode_id': str, 'message': str}
    """
    
    # Check availability
    if not WEBCAM_AVAILABLE:
        error_msg = "⚠️ Webcam scanner tidak tersedia.\n\n"
        
        if not OPENCV_AVAILABLE:
            error_msg += "📦 Install OpenCV:\n"
            error_msg += "   pip install opencv-python\n\n"
        
        if not SCANNER_METHOD:
            error_msg += "📦 Install scanner library (pilih salah satu):\n\n"
            error_msg += "   RECOMMENDED (Windows + Internet):\n"
            error_msg += "   pip install pyzxing\n\n"
            error_msg += "   ALTERNATIVE (butuh ZBar DLL):\n"
            error_msg += "   pip install pyzbar\n\n"
        
        if "404" in SCANNER_ERROR or "download" in SCANNER_ERROR.lower():
            error_msg += "🔄 Pyzxing sedang download JAR file...\n"
            error_msg += "   Tunggu 2-5 menit, lalu restart app.\n\n"
        
        error_msg += "💡 ALTERNATIF: Gunakan 'Input Manual' (lebih cepat)"
        
        st.error(error_msg)
        return {
            'success': False,
            'message': error_msg
        }
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    # Fallback to camera 1
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        error_msg = "❌ Tidak dapat membuka kamera!\n\n" + \
                    "Pastikan:\n" + \
                    "1. Webcam terhubung dengan benar\n" + \
                    "2. Tidak ada aplikasi lain yang pakai webcam\n" + \
                    "3. Driver webcam terinstall\n" + \
                    "4. Permission webcam diizinkan"
        st.error(error_msg)
        return {
            'success': False,
            'message': error_msg
        }
    
    # Camera settings
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Streamlit UI
    st.markdown("### 📷 Live Camera Preview")
    
    # Create columns for layout
    col_preview, col_status = st.columns([2, 1])
    
    with col_preview:
        # Camera preview placeholder (minimum 400x400)
        camera_placeholder = st.empty()
    
    with col_status:
        status_placeholder = st.empty()
        result_placeholder = st.empty()
        button_placeholder = st.empty()
    
    # Scanner state
    barcode_detected = None
    status = "scanning"
    frame_count = 0
    scan_interval = 5
    last_scan_time = 0
    max_frames = 900  # 30 seconds at 30fps
    
    # Progress bar
    progress_bar = st.progress(0)
    
    try:
        # Initial status
        with status_placeholder:
            st.info("⊙ **SCANNING...**\n\nArahkan barcode ke area hijau")
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                time.sleep(0.05)
                continue
            
            # Mirror frame
            frame = cv2.flip(frame, 1)
            
            # Resize to at least 400x400 for preview
            frame_h, frame_w = frame.shape[:2]
            preview_size = max(400, max(frame_w, frame_h))
            
            # Scan logic (throttled)
            current_time = time.time()
            
            if barcode_detected is None and frame_count % scan_interval == 0:
                if current_time - last_scan_time >= 0.2:
                    barcode_data = scan_frame(frame)
                    last_scan_time = current_time
                    
                    if barcode_data:
                        barcode_detected = barcode_data
                        status = "detected"
                        
                        # Update status - GREEN for success
                        with status_placeholder:
                            st.success(f"✅ **SUCCESS!**\n\nBarcode: `{barcode_data}`")
                        
                        with result_placeholder:
                            st.balloons()
                        
                        # Wait 1 second before closing
                        time.sleep(1)
                        break
            
            # Draw overlay on frame
            frame_with_overlay = draw_scan_overlay(frame, status, barcode_detected)
            
            # Convert BGR to RGB for Streamlit
            frame_rgb = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            
            # Display in Streamlit (minimum 400x400)
            with camera_placeholder:
                st.image(pil_image, use_container_width=True, caption="Live Preview")
            
            # Update progress
            progress = min(frame_count / max_frames, 1.0)
            progress_bar.progress(progress)
            
            frame_count += 1
            
            # Small delay to prevent high CPU
            time.sleep(0.03)  # ~30 FPS
        
        # Timeout
        if barcode_detected is None:
            status = "error"
            with status_placeholder:
                st.error("⏱️ **TIMEOUT**\n\nScan dibatalkan setelah 30 detik")
    
    except Exception as e:
        status = "error"
        with status_placeholder:
            st.error(f"❌ **ERROR**\n\n{str(e)}")
        
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        cap.release()
        progress_bar.empty()
    
    # Return result
    if barcode_detected:
        return {
            'success': True,
            'barcode_id': barcode_detected,
            'message': f"✅ Scan berhasil: {barcode_detected}"
        }
    else:
        return {
            'success': False,
            'message': "⏱️ Scan dibatalkan atau timeout.\n\n" +
                      "💡 Tips:\n" +
                      "- Barcode harus jelas dan fokus\n" +
                      "- Pegang steady 2-3 detik\n" +
                      "- Pastikan lighting cukup terang\n" +
                      "- Atau gunakan Input Manual"
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
    
    if WEBCAM_AVAILABLE:
        # Test camera
        cap = cv2.VideoCapture(0)
        camera_ok = cap.isOpened()
        cap.release()
        
        if camera_ok:
            message = f"✅ Scanner siap: {SCANNER_METHOD.upper()}"
            if SCANNER_METHOD == "pyzxing":
                message += " (online)"
        else:
            message = "⚠️ Library OK, tapi webcam tidak terdeteksi"
    else:
        if "404" in SCANNER_ERROR or "download" in SCANNER_ERROR.lower():
            message = "🔄 Pyzxing download JAR - Tunggu & restart"
        elif not OPENCV_AVAILABLE:
            message = "❌ Install: pip install opencv-python"
        else:
            message = "❌ Install: pip install pyzxing"
    
    return {
        'available': WEBCAM_AVAILABLE,
        'message': message,
        'method': SCANNER_METHOD,
        'opencv': OPENCV_AVAILABLE
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
print(f"   Scanner: {'✅ Ready' if WEBCAM_AVAILABLE else '❌ Not Available'}")
if WEBCAM_AVAILABLE:
    print(f"   Method: {SCANNER_METHOD}")
    if SCANNER_METHOD == "pyzxing":
        print(f"   Mode: Online (butuh internet)")
    print(f"   Preview: Streamlit (400x400 minimum)")
print()