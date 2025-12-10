"""
Utility Functions

Helper functions for the RSA+AES encryption project.
"""

import os
from rsa_module import generate_key_pair, save_key_pair


def ensure_directory(path: str):
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Directory path
    """
    os.makedirs(path, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def format_bytes(bytes_count: int) -> str:
    """
    Format bytes as human-readable string.
    
    Args:
        bytes_count: Number of bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} TB"


def create_key_pair_interactive(name: str = "key"):
    """
    Interactively create a new RSA key pair.
    
    Args:
        name: Prefix for key filenames
    
    Returns:
        tuple: (private_key_path, public_key_path)
    """
    print(f"Generating RSA-3072 key pair: {name}")
    print("This may take a few seconds...")
    
    private_key, public_key = generate_key_pair()
    private_path, public_path = save_key_pair(private_key, public_key, name)
    
    print(f"\n✅ Key pair generated successfully!")
    print(f"  Private key: {private_path}")
    print(f"  Public key: {public_path}")
    print(f"\n⚠️  IMPORTANT: Keep your private key secure and never share it!")
    print(f"    You can share the public key ({public_path}) with anyone.")
    
    return private_path, public_path


# Example usage
if __name__ == "__main__":
    print("Utility functions for RSA+AES encryption project")
    print("\nTo generate a key pair, run:")
    print("  from utils import create_key_pair_interactive")
    print("  create_key_pair_interactive('recipient')")

