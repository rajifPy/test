# Buat file: test_pyzbar.py
import cv2
from pyzbar.pyzbar import decode
import numpy as np

# Buka kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Mirror
    frame = cv2.flip(frame, 1)
    
    # Try detect
    results = decode(frame)
    
    if results:
        for result in results:
            print(f"DETECTED: {result.data.decode('utf-8')}")
            barcode_data = result.data.decode('utf-8')
            
            # Draw rectangle
            points = result.polygon
            if points:
                pts = np.array(points, dtype=np.int32)
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
            
            # Show text
            cv2.putText(frame, barcode_data, (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Display
    cv2.imshow('Barcode Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()