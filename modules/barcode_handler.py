"""
BARCODE HANDLER - PYZXING VERSION (INTERNET-BASED)
Real-time camera preview dengan Pyzxing (online API)
Version: 6.0 - Internet-Based Scanner
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

# Scanner Method Detection - PYZXING ONLY
SCANNER_METHOD = None
SCANNER_ERROR = ""
SCANNER_LIB = None

print("\n[1/1] Checking Pyzxing (Internet-based)...")
try:
    from pyzxing import BarCodeReader
    reader = BarCodeReader()
    SCANNER_METHOD = "pyzxing"
    SCANNER_LIB = reader
    print("✅ Pyzxing: Available (ACTIVE METHOD)")
    print("ℹ️  Note: Requires internet connection")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Pyzxing: {error_msg}")
    SCANNER_ERROR = error_msg

# Final Status
WEBCAM_AVAILABLE = OPENCV_AVAILABLE and SCANNER_METHOD is not None

print("\n" + "=" * 60)
if WEBCAM_AVAILABLE:
    print(f"✅ SCANNER READY: {SCANNER_METHOD.upper()}")
    print("⚠️  Internet connection required for scanning")
else:
    print("❌ SCANNER NOT AVAILABLE")
print("=" * 60)
print()

# ==================== INTERNET CONNECTION CHECK ====================

def check_internet_connection():
    """Check if internet is available"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# ==================== ENHANCED SCANNING WITH PYZXING ====================

def scan_frame_pyzxing(frame, temp_path="temp_scan.jpg"):
    """
    Scan using pyzxing with OPTIMIZED preprocessing
    
    Strategy:
    1. Try grayscale enhanced (fastest, best for clean barcodes)
    2. Try original if step 1 fails
    3. Try high contrast if step 2 fails
    """
    try:
        # Try 1: Grayscale with enhancement (BEST for pyzxing)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Save with high quality
        cv2.imwrite(temp_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        results = reader.decode(temp_path)
        
        if results and len(results) > 0:
            barcode_data = results[0].get('parsed', None)
            if barcode_data:
                return barcode_data
        
        # Try 2: Original frame
        cv2.imwrite(temp_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        results = reader.decode(temp_path)
        
        if results and len(results) > 0:
            barcode_data = results[0].get('parsed', None)
            if barcode_data:
                return barcode_data
        
        # Try 3: High contrast
        enhanced_color = cv2.convertScaleAbs(frame, alpha=1.5, beta=20)
        cv2.imwrite(temp_path, enhanced_color, [cv2.IMWRITE_JPEG_QUALITY, 95])
        results = reader.decode(temp_path)
        
        if results and len(results) > 0:
            barcode_data = results[0].get('parsed', None)
            if barcode_data:
                return barcode_data
        
        return None
        
    except Exception as e:
        # Suppress common errors (404, network timeout)
        if "404" not in str(e) and "timeout" not in str(e).lower():
            print(f"Pyzxing error: {e}")
        return None
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

def scan_frame(frame):
    """Universal scanner - pyzxing only"""
    if SCANNER_METHOD == "pyzxing":
        return scan_frame_pyzxing(frame)
    return None

# ==================== ENHANCED OVERLAY ====================

def draw_scan_overlay(frame, status="scanning", barcode_data=None, internet_status=True):
    """Draw overlay with internet status indicator"""
    height, width = frame.shape[:2]
    frame_copy = frame.copy()
    
    # Color based on status
    if status == "detected":
        color = (0, 255, 0)  # Green
        status_text = "✓ SUCCESS"
    elif status == "error":
        color = (0, 0, 255)  # Red
        status_text = "✗ ERROR"
    elif not internet_status:
        color = (0, 165, 255)  # Orange
        status_text = "⚠ NO INTERNET"
    else:  # scanning
        color = (0, 255, 255)  # Yellow
        status_text = "⊙ SCANNING..."
    
    # SCAN AREA (80% x 60%)
    scan_w = int(width * 0.8)
    scan_h = int(height * 0.6)
    scan_x = (width - scan_w) // 2
    scan_y = (height - scan_h) // 2
    
    # Semi-transparent overlay outside scan area
    overlay = frame_copy.copy()
    cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
    
    # Create mask for scan area
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.rectangle(mask, (scan_x, scan_y), (scan_x + scan_w, scan_y + scan_h), 255, -1)
    
    # Apply overlay (30% transparency)
    frame_copy = cv2.addWeighted(overlay, 0.3, frame_copy, 0.7, 0)
    frame_copy = np.where(mask[:, :, np.newaxis] == 255, frame, frame_copy)
    
    # Draw scan area border
    cv2.rectangle(frame_copy, (scan_x, scan_y), (scan_x + scan_w, scan_y + scan_h), color, 4)
    
    # Corner markers
    corner_len = 50
    corner_thick = 5
    
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
    if status == "scanning" and internet_status:
        animation = int((scan_h // 2) + (scan_h * 0.3 * np.sin(time.time() * 4)))
        scan_line_y = scan_y + animation
        cv2.line(frame_copy, (scan_x, scan_line_y), (scan_x + scan_w, scan_line_y), color, 3)
    
    # Status bar at top
    bar_h = 70
    cv2.rectangle(frame_copy, (0, 0), (width, bar_h), (30, 30, 30), -1)
    
    # Status text
    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)[0]
    text_x = (width - text_size[0]) // 2
    cv2.putText(frame_copy, status_text, (text_x, 45), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
    
    # Internet indicator (top-right)
    internet_color = (0, 255, 0) if internet_status else (0, 0, 255)
    internet_text = "ONLINE" if internet_status else "OFFLINE"
    cv2.putText(frame_copy, internet_text, (width - 150, 45),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, internet_color, 2)
    
    # Barcode result (if detected)
    if status == "detected" and barcode_data:
        result_h = 80
        result_y = height - result_h
        cv2.rectangle(frame_copy, (0, result_y), (width, height), (0, 200, 0), -1)
        cv2.rectangle(frame_copy, (0, result_y), (width, height), (0, 255, 0), 4)
        
        text = f"BARCODE: {barcode_data}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)[0]
        text_x = (width - text_size[0]) // 2
        cv2.putText(frame_copy, text, (text_x, result_y + 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
    
    return frame_copy

# ==================== REAL-TIME SCANNER WITH INTERNET ====================

def scan_barcode_realtime():
    """
    PYZXING VERSION: Internet-based barcode scanning
    
    Features:
    - Real-time internet connection monitoring
    - Optimized scanning (every 3 frames)
    - Automatic retry on network issues
    - User-friendly error messages
    
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
            error_msg += "📦 Install Pyzxing:\n"
            error_msg += "   pip install pyzxing\n\n"
        
        error_msg += "💡 ALTERNATIF: Gunakan 'Input Manual'"
        
        st.error(error_msg)
        return {
            'success': False,
            'message': error_msg
        }
    
    # Check internet connection
    if not check_internet_connection():
        error_msg = "⚠️ **Tidak ada koneksi internet!**\n\n"
        error_msg += "Pyzxing memerlukan internet untuk scanning.\n\n"
        error_msg += "**Solusi:**\n"
        error_msg += "1. Cek koneksi internet Anda\n"
        error_msg += "2. Atau gunakan 'Input Manual' (tidak butuh internet)"
        
        st.error(error_msg)
        return {
            'success': False,
            'message': error_msg
        }
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        error_msg = "❌ Tidak dapat membuka kamera!"
        st.error(error_msg)
        return {
            'success': False,
            'message': error_msg
        }
    
    # Camera settings
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)
    
    # Streamlit UI
    st.markdown("### 📷 Live Camera Preview")
    st.info("💡 **TIPS DETEKSI:**\n- 🌐 Pastikan koneksi internet stabil\n- 📏 Pegang barcode 15-20cm dari kamera\n- 📐 Barcode harus rata (tidak miring)\n- 💡 Cahaya cukup terang\n- ⏱️ Tunggu 2-3 detik untuk processing")
    
    col_preview, col_status = st.columns([2, 1])
    
    with col_preview:
        camera_placeholder = st.empty()
    
    with col_status:
        status_placeholder = st.empty()
        internet_placeholder = st.empty()
        tips_placeholder = st.empty()
        result_placeholder = st.empty()
    
    # Scanner state - OPTIMIZED FOR INTERNET
    barcode_detected = None
    status = "scanning"
    frame_count = 0
    scan_interval = 3  # Scan every 3 frames (reduce API calls)
    max_frames = 1500  # 50 seconds timeout
    
    # Detection history
    detection_history = []
    required_confirmations = 1  # Only need 1 reading
    
    # Internet status
    last_internet_check = 0
    internet_check_interval = 5  # Check every 5 seconds
    internet_status = True
    
    progress_bar = st.progress(0)
    
    try:
        with status_placeholder:
            st.info("⊙ **SCANNING...**\n\n🌐 Connecting to API...")
        
        with tips_placeholder:
            st.markdown("""
            **Posisi Optimal:**
            - 📏 Jarak: 15-20cm
            - 📐 Sudut: Lurus (90°)
            - 💡 Cahaya: Terang merata
            - 🌐 Internet: Stabil
            """)
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                time.sleep(0.05)
                continue
            
            # Mirror frame
            frame = cv2.flip(frame, 1)
            
            # Check internet periodically
            current_time = time.time()
            if current_time - last_internet_check > internet_check_interval:
                internet_status = check_internet_connection()
                last_internet_check = current_time
                
                with internet_placeholder:
                    if internet_status:
                        st.success("🌐 Internet: **ONLINE**")
                    else:
                        st.error("🌐 Internet: **OFFLINE**")
            
            # SCAN LOGIC - Only if internet available
            if barcode_detected is None and frame_count % scan_interval == 0 and internet_status:
                with status_placeholder:
                    st.info("⊙ **PROCESSING...**\n\n📡 Uploading to API...")
                
                barcode_data = scan_frame(frame)
                
                if barcode_data:
                    detection_history.append(barcode_data)
                    
                    if len(detection_history) > 3:
                        detection_history.pop(0)
                    
                    if len(detection_history) >= required_confirmations:
                        if len(set(detection_history[-required_confirmations:])) == 1:
                            barcode_detected = barcode_data
                            status = "detected"
                            
                            with status_placeholder:
                                st.success(f"✅ **SUCCESS!**\n\nBarcode: `{barcode_data}`")
                            
                            with result_placeholder:
                                st.balloons()
                            
                            time.sleep(1)
                            break
                        else:
                            with tips_placeholder:
                                st.warning(f"📡 Mendeteksi... ({len(detection_history)}/{required_confirmations})\nPegang steady!")
            
            elif not internet_status:
                status = "error"
                with status_placeholder:
                    st.error("⚠️ **NO INTERNET**\n\nMenunggu koneksi...")
            
            # Draw overlay
            frame_with_overlay = draw_scan_overlay(frame, status, barcode_detected, internet_status)
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            with camera_placeholder:
                st.image(pil_image, use_container_width=True, caption="Live Preview")
            
            # Update progress
            progress = min(frame_count / max_frames, 1.0)
            progress_bar.progress(progress)
            
            frame_count += 1
            
            # Reduced delay for smoother preview
            time.sleep(0.03)  # ~33 FPS
        
        # Timeout
        if barcode_detected is None:
            status = "error"
            with status_placeholder:
                st.error("⏱️ **TIMEOUT**\n\nTidak ada barcode terdeteksi")
    
    except Exception as e:
        status = "error"
        with status_placeholder:
            st.error(f"❌ **ERROR**\n\n{str(e)}")
        
        import traceback
        traceback.print_exc()
    
    finally:
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
            'message': "⏱️ Scan gagal atau timeout.\n\n" +
                      "💡 Tips:\n" +
                      "- Pastikan internet stabil\n" +
                      "- Barcode harus jelas dan fokus\n" +
                      "- Pegang steady 2-3 detik\n" +
                      "- Cahaya cukup terang\n" +
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
    """Check scanner status including internet"""
    
    if WEBCAM_AVAILABLE:
        cap = cv2.VideoCapture(0)
        camera_ok = cap.isOpened()
        cap.release()
        
        if camera_ok:
            internet_ok = check_internet_connection()
            
            if internet_ok:
                message = f"✅ Scanner siap: {SCANNER_METHOD.upper()} (online)"
            else:
                message = "⚠️ Scanner OK, tapi tidak ada internet. Gunakan Input Manual."
        else:
            message = "⚠️ Library OK, tapi webcam tidak terdeteksi"
    else:
        message = "❌ Install: pip install opencv-python pyzxing"
    
    return {
        'available': WEBCAM_AVAILABLE,
        'message': message,
        'method': SCANNER_METHOD,
        'opencv': OPENCV_AVAILABLE,
        'internet': check_internet_connection() if WEBCAM_AVAILABLE else False
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

print("📦 Barcode Handler Module Loaded (PYZXING VERSION)")
print(f"   Scanner: {'✅ Ready' if WEBCAM_AVAILABLE else '❌ Not Available'}")
if WEBCAM_AVAILABLE:
    print(f"   Method: {SCANNER_METHOD} (Internet-based)")
    print(f"   Internet: {'✅ Connected' if check_internet_connection() else '❌ Not connected'}")
print()
