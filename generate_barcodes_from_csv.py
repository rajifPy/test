"""
Script untuk Generate Barcode Secara Batch dari CSV
Jalankan: python generate_barcodes_from_csv.py

Fitur:
- Generate barcode dari products.csv
- Skip barcode yang sudah ada
- Progress bar
- Summary report
"""

import pandas as pd
import os
import barcode
from barcode.writer import ImageWriter
from tqdm import tqdm

def generate_single_barcode(barcode_id, product_name):
    """
    Generate single barcode
    """
    try:
        # Buat folder barcodes jika belum ada
        os.makedirs("barcodes", exist_ok=True)
        
        # Generate barcode Code128
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_id, writer=ImageWriter())
        
        # Simpan barcode
        filename = f"barcodes/{barcode_id}"
        full_path = barcode_instance.save(filename)
        
        return {
            'success': True,
            'path': full_path
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def check_existing_barcode(barcode_id):
    """
    Check if barcode already exists
    """
    barcode_path = f"barcodes/{barcode_id}.png"
    return os.path.exists(barcode_path)

def generate_barcodes_from_csv(csv_path="data/products.csv", skip_existing=True):
    """
    Generate barcodes from CSV file
    
    Args:
        csv_path: Path to products CSV
        skip_existing: Skip if barcode already exists
    """
    print("=" * 60)
    print("🏷️  BATCH BARCODE GENERATOR")
    print("=" * 60)
    print()
    
    # Check if CSV exists
    if not os.path.exists(csv_path):
        print(f"❌ Error: File {csv_path} tidak ditemukan!")
        print(f"💡 Pastikan file CSV ada di lokasi: {os.path.abspath(csv_path)}")
        return
    
    # Load CSV
    print(f"📂 Membaca file: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Berhasil load {len(df)} produk\n")
    except Exception as e:
        print(f"❌ Error membaca CSV: {e}")
        return
    
    # Validate columns
    required_columns = ['barcode_id', 'nama_produk']
    if not all(col in df.columns for col in required_columns):
        print(f"❌ Error: CSV harus memiliki kolom: {required_columns}")
        print(f"📋 Kolom yang ada: {df.columns.tolist()}")
        return
    
    # Statistics
    total_products = len(df)
    existing_count = 0
    to_generate = []
    
    print("🔍 Checking existing barcodes...")
    for idx, row in df.iterrows():
        if check_existing_barcode(row['barcode_id']):
            existing_count += 1
        else:
            to_generate.append(row)
    
    print(f"\n📊 Status:")
    print(f"   Total Produk: {total_products}")
    print(f"   ✅ Sudah Ada: {existing_count}")
    print(f"   🏷️  Perlu Generate: {len(to_generate)}")
    print()
    
    # Skip if all exist
    if len(to_generate) == 0:
        print("✅ Semua barcode sudah ada!")
        print(f"📁 Lokasi: {os.path.abspath('barcodes/')}")
        return
    
    # Ask confirmation if not skipping existing
    if not skip_existing:
        response = input(f"\n⚠️  Generate ulang {existing_count} barcode yang sudah ada? (y/n): ")
        if response.lower() == 'y':
            to_generate = df.to_dict('records')
    
    # Generate barcodes
    print(f"\n🚀 Memulai generate {len(to_generate)} barcode...")
    print()
    
    success_count = 0
    failed_items = []
    
    # Progress bar
    for item in tqdm(to_generate, desc="Generating", unit="barcode"):
        result = generate_single_barcode(item['barcode_id'], item['nama_produk'])
        
        if result['success']:
            success_count += 1
        else:
            failed_items.append({
                'barcode_id': item['barcode_id'],
                'error': result['error']
            })
    
    # Summary
    print()
    print("=" * 60)
    print("📊 SUMMARY REPORT")
    print("=" * 60)
    print(f"✅ Berhasil: {success_count}")
    print(f"❌ Gagal: {len(failed_items)}")
    print(f"📁 Lokasi: {os.path.abspath('barcodes/')}")
    print()
    
    # Show failed items
    if failed_items:
        print("❌ Item yang Gagal:")
        for item in failed_items:
            print(f"   - {item['barcode_id']}: {item['error']}")
        print()
    
    # Success message
    if success_count > 0:
        print("🎉 Generate barcode selesai!")
        print()
        print("📋 Langkah selanjutnya:")
        print("   1. Cek folder 'barcodes/' untuk melihat hasil")
        print("   2. Print barcode yang dibutuhkan")
        print("   3. Tempelkan pada produk")
        print("   4. Scan di aplikasi untuk transaksi")
    
    print()
    print("=" * 60)

def main():
    """
    Main function
    """
    import sys
    
    # Check arguments
    csv_path = "data/products.csv"
    skip_existing = True
    
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        skip_existing = sys.argv[2].lower() != 'force'
    
    # Run generator
    generate_barcodes_from_csv(csv_path, skip_existing)
    
    # Wait for enter
    input("\nTekan Enter untuk keluar...")

if __name__ == "__main__":
    main()