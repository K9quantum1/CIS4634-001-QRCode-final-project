"""
Main Encryption Orchestrator

This module orchestrates the complete encryption process:
1. Read input data (file or text)
2. Compress with zstd
3. Generate random AES-256 session key
4. Encrypt data with AES-256-GCM
5. Encrypt session key with RSA-3072-OAEP
6. Package in CBOR envelope
7. Encode with Base45
8. Output Base45 string (ready for QR code)

This is the main entry point for encryption operations.
"""

import os
import sys
from rsa_module import load_public_key, encrypt_with_rsa_oaep
from aes_module import encrypt_with_aes_gcm
from compression_module import compress_data
from cbor_module import create_envelope
from base45_module import encode_base45


def read_file_data(file_path: str) -> bytes:
    """
    Read data from a file.
    
    Args:
        file_path: Path to file
    
    Returns:
        File contents as bytes
    
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file can't be read
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'rb') as f:
        return f.read()


def encrypt_data(data: bytes, public_key_path: str) -> str:
    """
    Encrypt data using the hybrid RSA+AES system.
    
    Complete encryption flow:
    1. Compress data with zstd
    2. Generate random AES-256 session key
    3. Encrypt compressed data with AES-256-GCM
    4. Encrypt session key with RSA-3072-OAEP
    5. Package in CBOR envelope
    6. Encode with Base45
    
    Args:
        data: Data to encrypt (bytes)
        public_key_path: Path to recipient's public key PEM file
    
    Returns:
        Base45-encoded string (ready for QR code)
    
    Raises:
        ValueError: If encryption fails
        FileNotFoundError: If public key file doesn't exist
    """
    print("Starting encryption process...")
    
    # Step 1: Compress data
    print("Step 1: Compressing data with zstd...")
    try:
        compressed_data = compress_data(data)
        print(f"  Original size: {len(data)} bytes")
        print(f"  Compressed size: {len(compressed_data)} bytes")
        compression_ratio = len(compressed_data) / len(data) if len(data) > 0 else 0
        print(f"  Compression ratio: {compression_ratio:.2%}")
    except Exception as e:
        raise ValueError(f"Compression failed: {str(e)}")
    
    # Step 2 & 3: Encrypt with AES-256-GCM
    print("\nStep 2: Encrypting with AES-256-GCM...")
    try:
        ciphertext, tag, session_key, iv = encrypt_with_aes_gcm(compressed_data)
        print(f"  Generated 256-bit session key")
        print(f"  Generated 96-bit IV")
        print(f"  Ciphertext size: {len(ciphertext)} bytes")
        print(f"  Authentication tag: {len(tag)} bytes")
    except Exception as e:
        raise ValueError(f"AES encryption failed: {str(e)}")
    
    # Step 4: Load public key and encrypt session key
    print("\nStep 3: Encrypting session key with RSA-3072-OAEP...")
    try:
        public_key = load_public_key(public_key_path)
        print(f"  Loaded public key from: {public_key_path}")
        encrypted_session_key = encrypt_with_rsa_oaep(session_key, public_key)
        print(f"  Encrypted session key size: {len(encrypted_session_key)} bytes")
    except FileNotFoundError:
        raise FileNotFoundError(f"Public key file not found: {public_key_path}")
    except Exception as e:
        raise ValueError(f"RSA encryption failed: {str(e)}")
    
    # Step 5: Create CBOR envelope
    print("\nStep 4: Creating CBOR envelope...")
    try:
        cbor_envelope = create_envelope(
            encrypted_key=encrypted_session_key,
            iv=iv,
            tag=tag,
            ciphertext=ciphertext
        )
        print(f"  CBOR envelope size: {len(cbor_envelope)} bytes")
    except Exception as e:
        raise ValueError(f"CBOR envelope creation failed: {str(e)}")
    
    # Step 6: Encode with Base45
    print("\nStep 5: Encoding with Base45...")
    try:
        base45_string = encode_base45(cbor_envelope)
        print(f"  Base45 string length: {len(base45_string)} characters")
    except Exception as e:
        raise ValueError(f"Base45 encoding failed: {str(e)}")
    
    print("\n✅ Encryption completed successfully!")
    return base45_string


def encrypt_file(file_path: str, public_key_path: str) -> str:
    """
    Encrypt a file.
    
    Args:
        file_path: Path to file to encrypt
        public_key_path: Path to recipient's public key PEM file
    
    Returns:
        Base45-encoded string (ready for QR code)
    """
    print(f"Reading file: {file_path}")
    data = read_file_data(file_path)
    return encrypt_data(data, public_key_path)


def encrypt_text(text: str, public_key_path: str) -> str:
    """
    Encrypt text string.
    
    Args:
        text: Text string to encrypt
        public_key_path: Path to recipient's public key PEM file
    
    Returns:
        Base45-encoded string (ready for QR code)
    """
    data = text.encode('utf-8')
    return encrypt_data(data, public_key_path)


# Command-line interface
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python encrypt.py <file_path> <public_key_path>")
        print("  python encrypt.py --text \"<text>\" <public_key_path>")
        print("\nExample:")
        print("  python encrypt.py document.pdf recipient_public.pem")
        print("  python encrypt.py --text \"Hello, World!\" recipient_public.pem")
        sys.exit(1)
    
    try:
        if sys.argv[1] == "--text":
            # Encrypt text
            text = sys.argv[2]
            public_key_path = sys.argv[3]
            print(f"Encrypting text: {text[:50]}..." if len(text) > 50 else f"Encrypting text: {text}")
            result = encrypt_text(text, public_key_path)
        else:
            # Encrypt file
            file_path = sys.argv[1]
            public_key_path = sys.argv[2]
            result = encrypt_file(file_path, public_key_path)
        
        print("\n" + "="*60)
        print("ENCRYPTION RESULT (Base45 string):")
        print("="*60)
        print(result)
        print("="*60)
        print("\nThis string is ready to be encoded into a QR code.")
        print("Save it to a file or use qr_generator.py to create QR code(s).")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

