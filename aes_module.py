"""
AES-256-GCM Encryption Module

This module handles:
- Random session key generation (256-bit)
- Random IV generation (96-bit for GCM)
- AES-256-GCM encryption
- AES-256-GCM decryption with authentication tag verification

Uses PyCryptodome (pure Python) - no DLL issues!
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os


def generate_session_key():
    """
    Generate a random 256-bit (32-byte) session key for AES-256.
    
    Returns:
        32-byte random key as bytes
    """
    return get_random_bytes(32)


def generate_iv():
    """
    Generate a random 96-bit (12-byte) IV for AES-GCM.
    
    Returns:
        12-byte random IV as bytes
    """
    return get_random_bytes(12)


def encrypt_with_aes_gcm(plaintext, key=None, iv=None):
    """
    Encrypt data using AES-256-GCM.
    
    Args:
        plaintext: Data to encrypt (bytes)
        key: AES key (32 bytes). If None, generates a new one.
        iv: Initialization vector (12 bytes). If None, generates a new one.
    
    Returns:
        tuple: (ciphertext, tag, key, iv)
    """
    # Generate key and IV if not provided
    if key is None:
        key = generate_session_key()
    if iv is None:
        iv = generate_iv()
    
    # Validate key size
    if len(key) != 32:
        raise ValueError(f"AES-256 requires 32-byte key, got {len(key)} bytes")
    
    # Validate IV size
    if len(iv) != 12:
        raise ValueError(f"AES-GCM requires 12-byte IV, got {len(iv)} bytes")
    
    # Create AES-GCM cipher
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    
    # Encrypt and generate tag
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    return ciphertext, tag, key, iv


def decrypt_with_aes_gcm(ciphertext, tag, key, iv):
    """
    Decrypt data using AES-256-GCM with authentication tag verification.
    
    Args:
        ciphertext: Encrypted data (bytes)
        tag: Authentication tag (16 bytes)
        key: AES key (32 bytes)
        iv: Initialization vector (12 bytes)
    
    Returns:
        Decrypted plaintext (bytes)
    
    Raises:
        ValueError: If authentication fails (tag mismatch, wrong key, etc.)
    """
    # Validate inputs
    if len(key) != 32:
        raise ValueError(f"AES-256 requires 32-byte key, got {len(key)} bytes")
    if len(iv) != 12:
        raise ValueError(f"AES-GCM requires 12-byte IV, got {len(iv)} bytes")
    if len(tag) != 16:
        raise ValueError(f"AES-GCM tag must be 16 bytes, got {len(tag)} bytes")
    
    try:
        # Create AES-GCM cipher
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        
        # Decrypt and verify tag
        # If tag is invalid, this will raise an exception
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext
    except Exception as e:
        raise ValueError(f"AES-GCM decryption failed (authentication tag mismatch or wrong key): {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    print("Testing AES-256-GCM encryption/decryption (using PyCryptodome)...")
    
    # Test data
    test_data = b"This is a test message that will be encrypted with AES-256-GCM."
    print(f"\nOriginal data: {test_data}")
    print(f"Data length: {len(test_data)} bytes")
    
    # Encrypt
    print("\nEncrypting with AES-256-GCM...")
    ciphertext, tag, key, iv = encrypt_with_aes_gcm(test_data)
    print(f"Ciphertext length: {len(ciphertext)} bytes")
    print(f"Tag length: {len(tag)} bytes")
    print(f"Key length: {len(key)} bytes")
    print(f"IV length: {len(iv)} bytes")
    
    # Decrypt
    print("\nDecrypting with AES-256-GCM...")
    decrypted = decrypt_with_aes_gcm(ciphertext, tag, key, iv)
    print(f"Decrypted data: {decrypted}")
    
    if test_data == decrypted:
        print("\n✅ AES-256-GCM encryption/decryption test PASSED")
    else:
        print("\n❌ AES-256-GCM encryption/decryption test FAILED")
    
    # Test authentication failure
    print("\nTesting authentication tag verification...")
    try:
        # Try to decrypt with wrong tag
        wrong_tag = b'\x00' * 16
        decrypt_with_aes_gcm(ciphertext, wrong_tag, key, iv)
        print("❌ Authentication test FAILED (should have raised exception)")
    except ValueError as e:
        print(f"✅ Authentication test PASSED (correctly rejected tampered data): {e}")

