"""
QR Code Reader Module

This module handles:
- Reading QR codes from image files
- Extracting Base45 encoded data
- Supporting multiple QR code reading methods
"""

from PIL import Image
import cv2
import numpy as np

# Try to import pyzbar (primary method)
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("Warning: pyzbar not available. Using OpenCV QR decoder only.")


def read_qr_with_pyzbar(image_path: str) -> str:
    """
    Read QR code using pyzbar library.
    
    Args:
        image_path: Path to QR code image file
    
    Returns:
        Decoded string from QR code
    
    Raises:
        ValueError: If no QR code found or multiple QR codes found
    """
    if not PYZBAR_AVAILABLE:
        raise ImportError("pyzbar is not installed")
    
    # Open image
    img = Image.open(image_path)
    
    # Decode QR codes
    decoded_objects = pyzbar_decode(img)
    
    if len(decoded_objects) == 0:
        raise ValueError("No QR code found in image")
    
    if len(decoded_objects) > 1:
        raise ValueError(f"Multiple QR codes found ({len(decoded_objects)}). Please use an image with a single QR code.")
    
    # Extract data
    qr_data = decoded_objects[0].data.decode('utf-8')
    return qr_data


def read_qr_with_opencv(image_path: str) -> str:
    """
    Read QR code using OpenCV library (backup method).
    
    Args:
        image_path: Path to QR code image file
    
    Returns:
        Decoded string from QR code
    
    Raises:
        ValueError: If no QR code found
    """
    # Read image
    img = cv2.imread(image_path)
    
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Initialize QR code detector
    qr_detector = cv2.QRCodeDetector()
    
    # Detect and decode
    data, vertices, _ = qr_detector.detectAndDecode(img)
    
    if vertices is None or data == "":
        raise ValueError("No QR code found in image")
    
    return data


def read_qr_code(image_path: str) -> str:
    """
    Read QR code from image file using best available method.
    
    Tries pyzbar first (more reliable), falls back to OpenCV.
    
    Args:
        image_path: Path to QR code image file
    
    Returns:
        Decoded string from QR code (typically Base45 encoded data)
    
    Raises:
        ValueError: If no QR code found or image cannot be read
        ImportError: If no QR reading library is available
    """
    errors = []
    
    # Try pyzbar first (more reliable)
    if PYZBAR_AVAILABLE:
        try:
            return read_qr_with_pyzbar(image_path)
        except Exception as e:
            errors.append(f"pyzbar: {str(e)}")
    
    # Try OpenCV as backup
    try:
        return read_qr_with_opencv(image_path)
    except Exception as e:
        errors.append(f"opencv: {str(e)}")
    
    # Both methods failed
    error_msg = "Failed to read QR code. Errors:\n" + "\n".join(f"- {err}" for err in errors)
    raise ValueError(error_msg)


# Command-line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python qr_reader.py <qr_image_path>")
        print("\nExample:")
        print("  python qr_reader.py encrypted_qr.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        print(f"Reading QR code from: {image_path}")
        data = read_qr_code(image_path)
        print(f"\n✅ QR Code decoded successfully!")
        print(f"\nData length: {len(data)} characters")
        print(f"\nDecoded data:")
        print("-" * 50)
        print(data)
        print("-" * 50)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

