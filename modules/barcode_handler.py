"""
BARCODE HANDLER - FIXED VERSION
Real-time camera preview dengan IMPROVED DETECTION
Version: 5.0 - Enhanced Detection
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
                    if hasattr(cv2, 'barcode'):
                        detector = cv2.barcode.BarcodeDetector()
                        SCANNER_METHOD = "opencv_barcode"
                        SCANNER_LIB = detector
                        print("✅ OpenCV Barcode: Available (ACTIVE METHOD)")
                    else:
                        print("⚠️ OpenCV Barcode: Module not available")
                except Exception as e:
                    print(f"⚠️ OpenCV Barcode: {e}")

# Final Status
WEBCAM_AVAILABLE = OPENCV_AVAILABLE and SCANNER_METHOD is not None

print("\n" + "=" * 60)
if WEBCAM_AVAILABLE:
    print(f"✅ SCANNER READY: {SCANNER_METHOD.upper()}")
else:
    print("❌ SCANNER NOT AVAILABLE")
print("=" * 60)
print()

# ==================== ENHANCED SCANNING METHODS ====================

def scan_frame_pyzxing(frame, temp_path="temp_scan.jpg"):
    """Scan using pyzxing - ENHANCED with preprocessing"""
    try:
        # Try 1: Original frame
        cv2.imwrite(temp_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        results = reader.decode(temp_path)
        if results and len(results) > 0:
            barcode_data = results[0].get('parsed', None)
            if barcode_data:
                return barcode_data
        
        # Try 2: Grayscale with high contrast
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=20)
        cv2.imwrite(temp_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])
        results = reader.decode(temp_path)
        if results and len(results) > 0:
            barcode_data = results[0].get('parsed', None)
            if barcode_data:
                return barcode_data
        
        # Try 3: Denoised
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        cv2.imwrite(temp_path, denoised, [cv2.IMWRITE_JPEG_QUALITY, 95])
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
    """Scan using pyzbar - ULTRA ENHANCED with multiple preprocessing"""
    try:
        # 1. Try original frame
        decoded_objects = pyzbar_decode(frame)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        
        # 2. Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = pyzbar_decode(gray)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        
        # 3. Adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        decoded_objects = pyzbar_decode(thresh)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        
        # 4. OTSU threshold
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        decoded_objects = pyzbar_decode(otsu)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        
        # 5. Enhanced contrast
        enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=30)
        decoded_objects = pyzbar_decode(enhanced)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        
        # 6. Denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        decoded_objects = pyzbar_decode(denoised)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        
        # 7. Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        decoded_objects = pyzbar_decode(sharpened)
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

# ==================== ENHANCED OVERLAY ====================

def draw_scan_overlay(frame, status="scanning", barcode_data=None):
    """Draw overlay - LARGER SCAN AREA"""
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
    
    # LARGER SCAN AREA (80% x 60% instead of 60% x 40%)
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
    
    # Apply overlay (30% transparency - lighter)
    frame_copy = cv2.addWeighted(overlay, 0.3, frame_copy, 0.7, 0)
    frame_copy = np.where(mask[:, :, np.newaxis] == 255, frame, frame_copy)
    
    # Draw scan area border (thicker)
    cv2.rectangle(frame_copy, (scan_x, scan_y), (scan_x + scan_w, scan_y + scan_h), color, 4)
    
    # Corner markers (larger)
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
    if status == "scanning":
        animation = int((scan_h // 2) + (scan_h * 0.3 * np.sin(time.time() * 4)))
        scan_line_y = scan_y + animation
        cv2.line(frame_copy, (scan_x, scan_line_y), (scan_x + scan_w, scan_line_y), color, 3)
    
    # Status bar at top
    bar_h = 70
    cv2.rectangle(frame_copy, (0, 0), (width, bar_h), (30, 30, 30), -1)
    
    # Status text (larger)
    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)[0]
    text_x = (width - text_size[0]) // 2
    cv2.putText(frame_copy, status_text, (text_x, 45), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
    
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

# ==================== FIXED REAL-TIME SCANNER ====================

def scan_barcode_realtime():
    """
    FIXED VERSION: More responsive and sensitive barcode detection
    
    IMPROVEMENTS:
    - Scan every 2 frames (instead of 5)
    - No delay between scans
    - Larger scan area (80% x 60%)
    - Preprocessing for better detection
    - Higher frame rate
    
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
        
        error_msg += "💡 ALTERNATIF: Gunakan 'Input Manual'"
        
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
    
    # Camera settings - OPTIMIZED
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)  # Optimal brightness
    
    # Streamlit UI
    st.markdown("### 📷 Live Camera Preview")
    st.info("💡 **TIPS DETEKSI:**\n- Pegang barcode 15-20cm dari kamera\n- Pastikan barcode rata (tidak miring)\n- Cahaya cukup terang\n- Tunggu fokus kamera (2-3 detik)")
    
    col_preview, col_status = st.columns([2, 1])
    
    with col_preview:
        camera_placeholder = st.empty()
    
    with col_status:
        status_placeholder = st.empty()
        tips_placeholder = st.empty()
        result_placeholder = st.empty()
    
    # Scanner state - ULTRA AGGRESSIVE
    barcode_detected = None
    status = "scanning"
    frame_count = 0
    scan_interval = 1  # SCAN EVERY FRAME for maximum detection
    max_frames = 1500  # 50 seconds at 30fps (increased timeout)
    
    # Detection history for stability
    detection_history = []
    required_confirmations = 1  # Only need 1 reading (faster response)
    
    progress_bar = st.progress(0)
    
    try:
        with status_placeholder:
            st.info("⊙ **SCANNING...**\n\nSiapkan barcode Anda")
        
        with tips_placeholder:
            st.markdown("""
            **Posisi Optimal:**
            - 📏 Jarak: 15-20cm
            - 📐 Sudut: Lurus (90°)
            - 💡 Cahaya: Terang merata
            """)
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                time.sleep(0.05)
                continue
            
            # Mirror frame
            frame = cv2.flip(frame, 1)
            
            # SCAN LOGIC - MORE AGGRESSIVE
            if barcode_detected is None and frame_count % scan_interval == 0:
                barcode_data = scan_frame(frame)
                
                if barcode_data:
                    # Add to history
                    detection_history.append(barcode_data)
                    
                    # Keep only last 3 detections
                    if len(detection_history) > 3:
                        detection_history.pop(0)
                    
                    # Check if we have consistent readings
                    if len(detection_history) >= required_confirmations:
                        # Check if last N readings are the same
                        if len(set(detection_history[-required_confirmations:])) == 1:
                            barcode_detected = barcode_data
                            status = "detected"
                            
                            with status_placeholder:
                                st.success(f"✅ **SUCCESS!**\n\nBarcode: `{barcode_data}`")
                            
                            with result_placeholder:
                                st.balloons()
                            
                            # Wait 1 second before closing
                            time.sleep(1)
                            break
                        else:
                            with tips_placeholder:
                                st.warning(f"📡 Mendeteksi... ({len(detection_history)}/{required_confirmations})\nPegang steady!")
            
            # Draw overlay
            frame_with_overlay = draw_scan_overlay(frame, status, barcode_detected)
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            with camera_placeholder:
                st.image(pil_image, use_container_width=True, caption="Live Preview")
            
            # Update progress
            progress = min(frame_count / max_frames, 1.0)
            progress_bar.progress(progress)
            
            frame_count += 1
            
            # REDUCED DELAY for higher FPS
            time.sleep(0.02)  # ~50 FPS (reduced from 0.03)
        
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
                      "- Barcode harus jelas dan fokus\n" +
                      "- Pegang steady 2-3 detik\n" +
                      "- Cahaya cukup terang\n" +
                      "- Coba atur jarak 15-20cm\n" +
                      "- Atau gunakan Input Manual"
        }

# ==================== BARCODE GENERATION (unchanged) ====================

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

print("📦 Barcode Handler Module Loaded (FIXED VERSION)")
print(f"   Scanner: {'✅ Ready' if WEBCAM_AVAILABLE else '❌ Not Available'}")
if WEBCAM_AVAILABLE:
    print(f"   Method: {SCANNER_METHOD}")
    print(f"   Detection: ENHANCED (every 2 frames, larger area)")
print()