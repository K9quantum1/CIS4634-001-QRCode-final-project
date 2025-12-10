"""
CBOR Envelope Module

This module handles:
- Creating CBOR envelopes from encryption components
- Parsing CBOR envelopes to extract components
- Validating envelope structure

CBOR (Concise Binary Object Representation) is used to package:
- Encrypted session key (RSA-OAEP encrypted)
- IV (Initialization Vector for AES-GCM)
- Authentication tag (from AES-GCM)
- Ciphertext (AES-GCM encrypted data)
- Metadata (version, algorithms, etc.)
"""

import cbor2
from typing import Dict, Any, Tuple


# Protocol version
ENVELOPE_VERSION = 1

# Algorithm identifiers
ALGORITHM_RSA3072_OAEP_AES256_GCM = "RSA3072-OAEP+AES256-GCM"
COMPRESSION_ZSTD = "zstd"


def create_envelope(encrypted_key: bytes, iv: bytes, tag: bytes, 
                   ciphertext: bytes, compression: str = COMPRESSION_ZSTD) -> bytes:
    """
    Create a CBOR envelope containing all encryption components.
    
    The envelope structure:
    {
        "version": 1,
        "algorithm": "RSA3072-OAEP+AES256-GCM",
        "compression": "zstd",
        "encrypted_key": <bytes>,  # RSA-encrypted session key
        "iv": <bytes>,             # 12-byte IV for AES-GCM
        "tag": <bytes>,            # 16-byte authentication tag
        "ciphertext": <bytes>      # Encrypted data
    }
    
    Args:
        encrypted_key: RSA-OAEP encrypted session key (bytes)
        iv: Initialization vector for AES-GCM (12 bytes)
        tag: Authentication tag from AES-GCM (16 bytes)
        ciphertext: Encrypted data (bytes)
        compression: Compression algorithm used (default: "zstd")
    
    Returns:
        CBOR-encoded envelope as bytes
    
    Raises:
        ValueError: If input validation fails
    """
    # Validate inputs
    if not isinstance(encrypted_key, bytes) or len(encrypted_key) == 0:
        raise ValueError("encrypted_key must be non-empty bytes")
    if not isinstance(iv, bytes) or len(iv) != 12:
        raise ValueError(f"iv must be 12 bytes, got {len(iv) if isinstance(iv, bytes) else 'non-bytes'}")
    if not isinstance(tag, bytes) or len(tag) != 16:
        raise ValueError(f"tag must be 16 bytes, got {len(tag) if isinstance(tag, bytes) else 'non-bytes'}")
    if not isinstance(ciphertext, bytes):
        raise ValueError("ciphertext must be bytes")
    
    # Create envelope dictionary
    envelope = {
        "version": ENVELOPE_VERSION,
        "algorithm": ALGORITHM_RSA3072_OAEP_AES256_GCM,
        "compression": compression,
        "encrypted_key": encrypted_key,
        "iv": iv,
        "tag": tag,
        "ciphertext": ciphertext
    }
    
    # Encode to CBOR
    try:
        cbor_data = cbor2.dumps(envelope)
        return cbor_data
    except Exception as e:
        raise ValueError(f"Failed to encode envelope to CBOR: {str(e)}")


def parse_envelope(cbor_data: bytes) -> Dict[str, Any]:
    """
    Parse a CBOR envelope to extract encryption components.
    
    Args:
        cbor_data: CBOR-encoded envelope (bytes)
    
    Returns:
        Dictionary containing envelope fields:
        {
            "version": int,
            "algorithm": str,
            "compression": str,
            "encrypted_key": bytes,
            "iv": bytes,
            "tag": bytes,
            "ciphertext": bytes
        }
    
    Raises:
        ValueError: If parsing fails or envelope is invalid
    """
    if not isinstance(cbor_data, bytes):
        raise ValueError("cbor_data must be bytes")
    
    try:
        envelope = cbor2.loads(cbor_data)
    except Exception as e:
        raise ValueError(f"Failed to parse CBOR data: {str(e)}")
    
    # Validate envelope structure
    required_fields = ["version", "algorithm", "compression", "encrypted_key", "iv", "tag", "ciphertext"]
    for field in required_fields:
        if field not in envelope:
            raise ValueError(f"Missing required field in envelope: {field}")
    
    # Validate field types and values
    if not isinstance(envelope["version"], int):
        raise ValueError("version must be an integer")
    if envelope["version"] != ENVELOPE_VERSION:
        raise ValueError(f"Unsupported envelope version: {envelope['version']}")
    
    if not isinstance(envelope["algorithm"], str):
        raise ValueError("algorithm must be a string")
    if envelope["algorithm"] != ALGORITHM_RSA3072_OAEP_AES256_GCM:
        raise ValueError(f"Unsupported algorithm: {envelope['algorithm']}")
    
    if not isinstance(envelope["compression"], str):
        raise ValueError("compression must be a string")
    
    # Validate binary fields
    for field in ["encrypted_key", "iv", "tag", "ciphertext"]:
        if not isinstance(envelope[field], bytes):
            raise ValueError(f"{field} must be bytes")
    
    # Validate sizes
    if len(envelope["iv"]) != 12:
        raise ValueError(f"iv must be 12 bytes, got {len(envelope['iv'])}")
    if len(envelope["tag"]) != 16:
        raise ValueError(f"tag must be 16 bytes, got {len(envelope['tag'])}")
    
    return envelope


def extract_components(cbor_data: bytes) -> Tuple[bytes, bytes, bytes, bytes]:
    """
    Extract encryption components from CBOR envelope.
    
    Convenience function that parses envelope and returns components.
    
    Args:
        cbor_data: CBOR-encoded envelope (bytes)
    
    Returns:
        Tuple: (encrypted_key, iv, tag, ciphertext)
    
    Raises:
        ValueError: If parsing fails
    """
    envelope = parse_envelope(cbor_data)
    return (
        envelope["encrypted_key"],
        envelope["iv"],
        envelope["tag"],
        envelope["ciphertext"]
    )


# Example usage and testing
if __name__ == "__main__":
    print("Testing CBOR envelope creation and parsing...")
    
    # Create test data
    encrypted_key = b'\x01' * 384  # RSA-3072 encrypted key size
    iv = b'\x02' * 12
    tag = b'\x03' * 16
    ciphertext = b'\x04' * 100
    
    print(f"\nCreating envelope...")
    print(f"Encrypted key length: {len(encrypted_key)} bytes")
    print(f"IV length: {len(iv)} bytes")
    print(f"Tag length: {len(tag)} bytes")
    print(f"Ciphertext length: {len(ciphertext)} bytes")
    
    # Create envelope
    cbor_data = create_envelope(encrypted_key, iv, tag, ciphertext)
    print(f"\nCBOR envelope size: {len(cbor_data)} bytes")
    
    # Parse envelope
    print("\nParsing envelope...")
    parsed = parse_envelope(cbor_data)
    print(f"Version: {parsed['version']}")
    print(f"Algorithm: {parsed['algorithm']}")
    print(f"Compression: {parsed['compression']}")
    print(f"Encrypted key length: {len(parsed['encrypted_key'])} bytes")
    print(f"IV length: {len(parsed['iv'])} bytes")
    print(f"Tag length: {len(parsed['tag'])} bytes")
    print(f"Ciphertext length: {len(parsed['ciphertext'])} bytes")
    
    # Verify data integrity
    if (parsed['encrypted_key'] == encrypted_key and
        parsed['iv'] == iv and
        parsed['tag'] == tag and
        parsed['ciphertext'] == ciphertext):
        print("\n✅ CBOR envelope test PASSED")
    else:
        print("\n❌ CBOR envelope test FAILED")

