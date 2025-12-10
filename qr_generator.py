"""
QR Code Generator Module

This module handles:
- Generating QR codes from Base45 strings
- Handling large data by splitting into multiple QR codes
- Saving QR codes as images

QR Code Limitations:
- Version 40 (largest): ~2,953 bytes (alphanumeric mode)
- Version 10 (common): ~366 bytes
- For larger data, split into multiple QR codes
"""

import qrcode
from qrcode.constants import ERROR_CORRECT_L
from PIL import Image
import os


# QR code capacity (alphanumeric mode, error correction level L)
# These are approximate values
QR_CAPACITIES = {
    1: 25,    # Version 1
    10: 366,  # Version 10
    20: 1468, # Version 20
    30: 2501, # Version 30
    40: 2953  # Version 40 (maximum)
}


def estimate_qr_version(data_length: int) -> int:
    """
    Estimate the minimum QR code version needed for data.
    
    Args:
        data_length: Length of data in characters
    
    Returns:
        QR code version (1-40)
    """
    for version in sorted(QR_CAPACITIES.keys()):
        if data_length <= QR_CAPACITIES[version]:
            return version
    
    # Data is too large for a single QR code
    return 40  # Maximum version


def generate_qr_code(data: str, output_path: str = None, version: int = None, 
                     box_size: int = 10, border: int = 4) -> Image.Image:
    """
    Generate a single QR code from data string.
    
    Args:
        data: Data string to encode (Base45 string)
        output_path: Optional path to save QR code image
        version: QR code version (1-40). If None, auto-detect.
        box_size: Size of each box in pixels (default: 10)
        border: Border thickness in boxes (default: 4)
    
    Returns:
        PIL Image object of the QR code
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=version,
        error_correction=ERROR_CORRECT_L,  # Low error correction for more capacity
        box_size=box_size,
        border=border,
    )
    
    # Add data
    qr.add_data(data)
    
    # Make QR code
    if version is None:
        qr.make(fit=True)  # Auto-fit to data size
    else:
        qr.make()
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save if path provided
    if output_path:
        img.save(output_path)
        print(f"QR code saved to: {output_path}")
    
    return img


def split_data_for_qr(data: str, max_chunk_size: int = 2500) -> list:
    """
    Split data into chunks that fit in QR codes.
    
    Args:
        data: Data string to split
        max_chunk_size: Maximum characters per chunk (default: 2500, safe for version 30)
    
    Returns:
        List of data chunks
    """
    chunks = []
    for i in range(0, len(data), max_chunk_size):
        chunk = data[i:i + max_chunk_size]
        chunks.append(chunk)
    return chunks


def generate_multiple_qr_codes(data: str, output_prefix: str = "qr_code", 
                               max_chunk_size: int = 2500) -> list:
    """
    Generate multiple QR codes for large data.
    
    Args:
        data: Data string to encode
        output_prefix: Prefix for output filenames (e.g., "qr_code" -> "qr_code_1.png", "qr_code_2.png")
        max_chunk_size: Maximum characters per QR code
    
    Returns:
        List of (chunk_number, image_path) tuples
    """
    chunks = split_data_for_qr(data, max_chunk_size)
    
    if len(chunks) == 1:
        # Single QR code
        output_path = f"{output_prefix}.png"
        img = generate_qr_code(data, output_path)
        return [(1, output_path)]
    
    # Multiple QR codes
    print(f"Splitting data into {len(chunks)} QR codes...")
    results = []
    
    for i, chunk in enumerate(chunks, 1):
        output_path = f"{output_prefix}_{i}.png"
        img = generate_qr_code(chunk, output_path)
        results.append((i, output_path))
        print(f"  Generated QR code {i}/{len(chunks)}: {output_path} ({len(chunk)} chars)")
    
    return results


def generate_qr_from_base45(base45_string: str, output_path: str = "encrypted_qr.png"):
    """
    Generate QR code from Base45 string.
    
    Convenience function that handles single or multiple QR codes.
    
    Args:
        base45_string: Base45-encoded string
        output_path: Output file path (or prefix for multiple files)
    
    Returns:
        List of generated QR code file paths
    """
    print(f"Generating QR code(s) from Base45 string...")
    print(f"Base45 string length: {len(base45_string)} characters")
    
    # Estimate if we need multiple QR codes
    estimated_version = estimate_qr_version(len(base45_string))
    
    if estimated_version <= 40:
        # Can fit in single QR code
        print(f"Estimated QR version needed: {estimated_version}")
        results = generate_multiple_qr_codes(base45_string, output_path.replace('.png', ''), max_chunk_size=2500)
        return [path for _, path in results]
    else:
        # Need multiple QR codes
        print(f"Data is too large for a single QR code. Splitting...")
        results = generate_multiple_qr_codes(base45_string, output_path.replace('.png', ''), max_chunk_size=2500)
        return [path for _, path in results]


# Command-line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python qr_generator.py <base45_string> [output_path]")
        print("  python qr_generator.py --file <base45_file> [output_path]")
        print("\nExample:")
        print("  python qr_generator.py \"%69 VD92EX...\" encrypted_qr.png")
        print("  python qr_generator.py --file encrypted.txt encrypted_qr.png")
        sys.exit(1)
    
    try:
        if sys.argv[1] == "--file":
            # Read from file
            base45_file = sys.argv[2]
            output_path = sys.argv[3] if len(sys.argv) > 3 else "encrypted_qr.png"
            
            with open(base45_file, 'r') as f:
                base45_string = f.read().strip()
        else:
            # From command line
            base45_string = sys.argv[1]
            output_path = sys.argv[2] if len(sys.argv) > 2 else "encrypted_qr.png"
        
        # Generate QR code(s)
        paths = generate_qr_from_base45(base45_string, output_path)
        
        print(f"\n✅ Generated {len(paths)} QR code(s):")
        for path in paths:
            print(f"  - {path}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

