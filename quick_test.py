"""
QUICK TEST - Individual Component Testing
Cek satu per satu: Generate, Scan, Display
"""

import os
import sys

def test_generate_barcode():
    """Test 1: Generate Barcode"""
    print("\n" + "=" * 60)
    print("TEST 1: GENERATE BARCODE")
    print("=" * 60)
    
    try:
        from barcode import Code128
        from barcode.writer import ImageWriter
        
        os.makedirs("barcodes", exist_ok=True)
        
        # Generate 3 test barcodes
        test_codes = ["TEST001", "TEST002", "BRK001"]
        
        for code in test_codes:
            barcode_obj = Code128(code, writer=ImageWriter())
            filepath = barcode_obj.save(f"barcodes/{code}")
            
            if os.path.exists(f"barcodes/{code}.png"):
                size = os.path.getsize(f"barcodes/{code}.png")
                print(f"✅ {code}.png - {size} bytes")
            else:
                print(f"❌ {code}.png - FAILED")
                return False
        
        print("\n✅ BARCODE GENERATION: WORKING")
        return True
        
    except Exception as e:
        print(f"\n❌ BARCODE GENERATION: FAILED")
        print(f"Error: {e}")
        return False

def test_qrcode_scanner():
    """Test 2: QRCode Scanner Import"""
    print("\n" + "=" * 60)
    print("TEST 2: QRCODE SCANNER")
    print("=" * 60)
    
    try:
        from streamlit_qrcode_scanner import qrcode_scanner
        print("✅ streamlit-qrcode-scanner: IMPORTED")
        print("\nFeatures:")
        print("  - Browser-based (HTML5 getUserMedia)")
        print("  - No OpenCV needed")
        print("  - Supports: QR, Code128, EAN, UPC, Code39, etc")
        print("\n✅ SCANNER LIBRARY: READY")
        return True
        
    except ImportError as e:
        print(f"❌ streamlit-qrcode-scanner: NOT FOUND")
        print(f"Error: {e}")
        print("\nInstall dengan:")
        print("  pip install streamlit-qrcode-scanner==0.1.2")
        return False

def test_streamlit():
    """Test 3: Streamlit"""
    print("\n" + "=" * 60)
    print("TEST 3: STREAMLIT")
    print("=" * 60)
    
    try:
        import streamlit as st
        print(f"✅ Streamlit: {st.__version__}")
        return True
    except ImportError:
        print("❌ Streamlit: NOT FOUND")
        print("Install: pip install streamlit")
        return False

def test_project_structure():
    """Test 4: Project Files"""
    print("\n" + "=" * 60)
    print("TEST 4: PROJECT STRUCTURE")
    print("=" * 60)
    
    files = {
        'app.py': False,
        'modules/__init__.py': False,
        'modules/barcode_handler.py': False,
        'modules/data_handler.py': False,
    }
    
    all_ok = True
    
    for filepath in files:
        if os.path.exists(filepath):
            print(f"✅ {filepath}")
            files[filepath] = True
        else:
            print(f"❌ {filepath} - MISSING")
            all_ok = False
    
    if all_ok:
        print("\n✅ PROJECT STRUCTURE: OK")
    else:
        print("\n❌ PROJECT STRUCTURE: INCOMPLETE")
    
    return all_ok

def main():
    print("=" * 60)
    print("QUICK COMPONENT TEST")
    print("Testing individual components...")
    print("=" * 60)
    
    results = {
        'Generate Barcode': test_generate_barcode(),
        'QRCode Scanner': test_qrcode_scanner(),
        'Streamlit': test_streamlit(),
        'Project Files': test_project_structure(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {test_name}")
    
    print("\n" + "=" * 60)
    
    # Conclusion
    all_pass = all(results.values())
    
    if all_pass:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("Your system is ready. Run the app:")
        print("  streamlit run app.py")
        print()
        print("Then test scanning:")
        print("  1. Generate some products in 'Data Master'")
        print("  2. Generate barcodes")
        print("  3. Open generated barcode image")
        print("  4. Go to 'Scan Barcode' page")
        print("  5. Click 'Start Scanning'")
        print("  6. Point camera at barcode on screen")
        
    else:
        print("⚠️ SOME TESTS FAILED")
        print()
        print("Quick fixes:")
        print()
        
        if not results['Generate Barcode']:
            print("Fix barcode generation:")
            print("  pip install python-barcode pillow")
            print()
        
        if not results['QRCode Scanner']:
            print("Fix scanner:")
            print("  pip install streamlit-qrcode-scanner==0.1.2")
            print()
        
        if not results['Streamlit']:
            print("Fix Streamlit:")
            print("  pip install streamlit")
            print()
        
        if not results['Project Files']:
            print("Fix project files:")
            print("  Pastikan semua file source code ada")
            print()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\nTekan Enter untuk keluar...")