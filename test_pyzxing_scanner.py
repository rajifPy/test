# File: test_quick.py
import cv2
from pyzxing import BarCodeReader
import socket

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

print("Testing...")
print(f"Internet: {'✅ OK' if check_internet() else '❌ NO'}")

cap = cv2.VideoCapture(0)
ret, _ = cap.read()
cap.release()
print(f"Webcam: {'✅ OK' if ret else '❌ NO'}")

reader = BarCodeReader()
print("Pyzxing: ✅ OK")
print("\nSiap digunakan!")