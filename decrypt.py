"""
Main Decryption Orchestrator

This module orchestrates the complete decryption process:
1. Decode Base45 string
2. Parse CBOR envelope
3. Decrypt session key with RSA-3072-OAEP
4. Decrypt ciphertext with AES-256-GCM
5. Decompress with zstd
6. Output original data

This is the main entry point for decryption operations.
"""

import os
import sys
from rsa_module import load_private_key, decrypt_with_rsa_oaep
from aes_module import decrypt_with_aes_gcm
from compression_module import decompress_data
from cbor_module import parse_envelope
from base45_module import decode_base45


def write_file_data(file_path: str, data: bytes):
    """
    Write data to a file.
    
    Args:
        file_path: Path to output file
        data: Data to write (bytes)
    
    Raises:
        IOError: If file can't be written
    """
    with open(file_path, 'wb') as f:
        f.write(data)


def decrypt_data(base45_string: str, private_key_path: str) -> bytes:
    """
    Decrypt data from Base45 string.
    
    Complete decryption flow:
    1. Decode Base45 string
    2. Parse CBOR envelope
    3. Decrypt session key with RSA-3072-OAEP
    4. Decrypt ciphertext with AES-256-GCM
    5. Decompress with zstd
    
    Args:
        base45_string: Base45-encoded encrypted data
        private_key_path: Path to recipient's private key PEM file
    
    Returns:
        Decrypted original data (bytes)
    
    Raises:
        ValueError: If decryption fails (wrong key, tampered data, etc.)
        FileNotFoundError: If private key file doesn't exist
    """
    print("Starting decryption process...")
    
    # Step 1: Decode Base45
    print("Step 1: Decoding Base45 string...")
    try:
        cbor_data = decode_base45(base45_string)
        print(f"  CBOR data size: {len(cbor_data)} bytes")
    except Exception as e:
        raise ValueError(f"Base45 decoding failed: {str(e)}")
    
    # Step 2: Parse CBOR envelope
    print("\nStep 2: Parsing CBOR envelope...")
    try:
        envelope = parse_envelope(cbor_data)
        print(f"  Version: {envelope['version']}")
        print(f"  Algorithm: {envelope['algorithm']}")
        print(f"  Compression: {envelope['compression']}")
        print(f"  Encrypted key size: {len(envelope['encrypted_key'])} bytes")
        print(f"  IV size: {len(envelope['iv'])} bytes")
        print(f"  Tag size: {len(envelope['tag'])} bytes")
        print(f"  Ciphertext size: {len(envelope['ciphertext'])} bytes")
    except Exception as e:
        raise ValueError(f"CBOR envelope parsing failed: {str(e)}")
    
    # Step 3: Decrypt session key
    print("\nStep 3: Decrypting session key with RSA-3072-OAEP...")
    try:
        private_key = load_private_key(private_key_path)
        print(f"  Loaded private key from: {private_key_path}")
        session_key = decrypt_with_rsa_oaep(envelope['encrypted_key'], private_key)
        print(f"  Decrypted session key size: {len(session_key)} bytes")
    except FileNotFoundError:
        raise FileNotFoundError(f"Private key file not found: {private_key_path}")
    except Exception as e:
        raise ValueError(f"RSA decryption failed: {str(e)}")
    
    # Step 4: Decrypt ciphertext with AES-256-GCM
    print("\nStep 4: Decrypting with AES-256-GCM...")
    try:
        compressed_data = decrypt_with_aes_gcm(
            envelope['ciphertext'],
            envelope['tag'],
            session_key,
            envelope['iv']
        )
        print(f"  Decrypted (compressed) data size: {len(compressed_data)} bytes")
    except Exception as e:
        raise ValueError(f"AES decryption failed: {str(e)}")
    
    # Step 5: Decompress
    print("\nStep 5: Decompressing with zstd...")
    try:
        original_data = decompress_data(compressed_data)
        print(f"  Decompressed data size: {len(original_data)} bytes")
    except Exception as e:
        raise ValueError(f"Decompression failed: {str(e)}")
    
    print("\n✅ Decryption completed successfully!")
    return original_data


def decrypt_to_file(base45_string: str, private_key_path: str, output_path: str):
    """
    Decrypt Base45 string and save to file.
    
    Args:
        base45_string: Base45-encoded encrypted data
        private_key_path: Path to recipient's private key PEM file
        output_path: Path to output file
    """
    data = decrypt_data(base45_string, private_key_path)
    write_file_data(output_path, data)
    print(f"\nDecrypted data saved to: {output_path}")


def decrypt_to_text(base45_string: str, private_key_path: str) -> str:
    """
    Decrypt Base45 string and return as text.
    
    Args:
        base45_string: Base45-encoded encrypted data
        private_key_path: Path to recipient's private key PEM file
    
    Returns:
        Decrypted text string
    """
    data = decrypt_data(base45_string, private_key_path)
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Decrypted data is not valid UTF-8 text. Use decrypt_to_file() for binary data.")


# Command-line interface
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python decrypt.py <base45_string> <private_key_path> [output_file]")
        print("  python decrypt.py --file <base45_file> <private_key_path> [output_file]")
        print("\nExample:")
        print("  python decrypt.py \"%69 VD92EX...\" recipient_private.pem output.pdf")
        print("  python decrypt.py --file encrypted.txt recipient_private.pem output.pdf")
        sys.exit(1)
    
    try:
        if sys.argv[1] == "--file":
            # Read Base45 string from file
            base45_file = sys.argv[2]
            private_key_path = sys.argv[3]
            output_path = sys.argv[4] if len(sys.argv) > 4 else "decrypted_output"
            
            with open(base45_file, 'r') as f:
                base45_string = f.read().strip()
        else:
            # Base45 string from command line
            base45_string = sys.argv[1]
            private_key_path = sys.argv[2]
            output_path = sys.argv[3] if len(sys.argv) > 3 else "decrypted_output"
        
        # Decrypt
        data = decrypt_data(base45_string, private_key_path)
        
        # Try to determine if it's text or binary
        try:
            text = data.decode('utf-8')
            # If it decodes successfully, check if it looks like text
            if all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in text[:1000]):
                print("\n" + "="*60)
                print("DECRYPTED TEXT:")
                print("="*60)
                print(text)
                print("="*60)
            else:
                # Binary data that happens to be valid UTF-8
                write_file_data(output_path, data)
                print(f"\nDecrypted data saved to: {output_path}")
        except UnicodeDecodeError:
            # Binary data
            write_file_data(output_path, data)
            print(f"\nDecrypted data saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

