"""
RSA-3072 Key Generation and OAEP Encryption Module

This module handles:
- RSA-3072 key pair generation
- Key storage and loading (PEM format)
- RSA-OAEP encryption (using public key)
- RSA-OAEP decryption (using private key)

Uses PyCryptodome (pure Python) - no DLL issues!
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import os


def generate_key_pair(key_size=3072):
    """
    Generate an RSA key pair using PyCryptodome.
    
    Args:
        key_size: Key size in bits (default: 3072 for RSA-3072)
    
    Returns:
        tuple: (private_key, public_key) as PyCryptodome key objects
    """
    # Generate private key
    private_key = RSA.generate(key_size)
    
    # Derive public key from private key
    public_key = private_key.publickey()
    
    return private_key, public_key


def save_key_pair(private_key, public_key, name_prefix="key"):
    """
    Save RSA key pair to PEM files.
    
    Args:
        private_key: Private key object
        public_key: Public key object
        name_prefix: Prefix for key filenames (default: "key")
    
    Returns:
        tuple: (private_key_path, public_key_path)
    """
    # Export private key to PEM format
    private_pem = private_key.export_key('PEM')
    
    # Export public key to PEM format
    public_pem = public_key.export_key('PEM')
    
    # Write to files
    private_path = f"{name_prefix}_private.pem"
    public_path = f"{name_prefix}_public.pem"
    
    with open(private_path, 'wb') as f:
        f.write(private_pem)
    
    with open(public_path, 'wb') as f:
        f.write(public_pem)
    
    return private_path, public_path


def load_private_key(file_path):
    """
    Load private key from PEM file.
    
    Args:
        file_path: Path to private key PEM file
    
    Returns:
        Private key object
    """
    with open(file_path, 'rb') as f:
        private_key = RSA.import_key(f.read())
    return private_key


def load_public_key(file_path):
    """
    Load public key from PEM file.
    
    Args:
        file_path: Path to public key PEM file
    
    Returns:
        Public key object
    """
    with open(file_path, 'rb') as f:
        public_key = RSA.import_key(f.read())
    return public_key


def encrypt_with_rsa_oaep(data, public_key):
    """
    Encrypt data using RSA-OAEP with SHA-256.
    
    Args:
        data: Bytes to encrypt (must be <= 318 bytes for RSA-3072)
        public_key: Public key object
    
    Returns:
        Encrypted data as bytes
    
    Raises:
        ValueError: If data is too large for RSA encryption
    """
    # RSA-3072 can encrypt up to (key_size/8 - 2*hash_size/8 - 2) bytes
    # For RSA-3072 with SHA-256: 384 - 64 - 2 = 318 bytes max
    max_size = (public_key.size_in_bytes()) - 66
    
    if len(data) > max_size:
        raise ValueError(f"Data too large for RSA encryption. Max size: {max_size} bytes, got: {len(data)} bytes")
    
    # Create OAEP cipher with SHA-256
    cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
    
    # Encrypt
    ciphertext = cipher.encrypt(data)
    
    return ciphertext


def decrypt_with_rsa_oaep(encrypted_data, private_key):
    """
    Decrypt data using RSA-OAEP with SHA-256.
    
    Args:
        encrypted_data: Encrypted bytes
        private_key: Private key object
    
    Returns:
        Decrypted data as bytes
    
    Raises:
        ValueError: If decryption fails (wrong key, corrupted data, etc.)
    """
    try:
        # Create OAEP cipher with SHA-256
        cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
        
        # Decrypt
        plaintext = cipher.decrypt(encrypted_data)
        return plaintext
    except Exception as e:
        raise ValueError(f"RSA decryption failed: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    print("Generating RSA-3072 key pair...")
    private_key, public_key = generate_key_pair()
    
    print("Saving key pair...")
    private_path, public_path = save_key_pair(private_key, public_key, "test_key")
    print(f"Private key saved to: {private_path}")
    print(f"Public key saved to: {public_path}")
    
    # Test encryption/decryption
    test_data = b"This is a test session key (32 bytes)"
    print(f"\nOriginal data: {test_data}")
    print(f"Data length: {len(test_data)} bytes")
    
    print("\nEncrypting with RSA-OAEP...")
    encrypted = encrypt_with_rsa_oaep(test_data, public_key)
    print(f"Encrypted length: {len(encrypted)} bytes")
    
    print("\nDecrypting with RSA-OAEP...")
    decrypted = decrypt_with_rsa_oaep(encrypted, private_key)
    print(f"Decrypted data: {decrypted}")
    
    if test_data == decrypted:
        print("\n✅ RSA-OAEP encryption/decryption test PASSED")
    else:
        print("\n❌ RSA-OAEP encryption/decryption test FAILED")

