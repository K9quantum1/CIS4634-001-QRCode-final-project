"""
Base45 Encoding Module

This module handles:
- Encoding binary data to Base45 strings
- Decoding Base45 strings to binary data

Base45 is a QR-code-friendly encoding scheme that uses 45 characters:
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:

Why Base45?
- More compact than Base64 for QR codes
- Uses characters that QR scanners handle well
- Used in real-world applications (EU Digital COVID Certificate)
"""

try:
    import base45
    HAS_BASE45_LIB = True
except ImportError:
    HAS_BASE45_LIB = False


# Base45 character set (45 characters)
BASE45_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"


def encode_base45(data: bytes) -> str:
    """
    Encode binary data to Base45 string.
    
    Args:
        data: Binary data to encode (bytes)
    
    Returns:
        Base45-encoded string
    
    Raises:
        ValueError: If encoding fails
    """
    if not isinstance(data, bytes):
        raise ValueError("data must be bytes")
    
    if HAS_BASE45_LIB:
        # Use library if available
        try:
            return base45.b45encode(data).decode('ascii')
        except Exception as e:
            raise ValueError(f"Base45 encoding failed: {str(e)}")
    else:
        # Fallback implementation
        return _encode_base45_manual(data)


def decode_base45(encoded: str) -> bytes:
    """
    Decode Base45 string to binary data.
    
    Args:
        encoded: Base45-encoded string
    
    Returns:
        Decoded binary data (bytes)
    
    Raises:
        ValueError: If decoding fails or string contains invalid characters
    """
    if not isinstance(encoded, str):
        raise ValueError("encoded must be a string")
    
    if HAS_BASE45_LIB:
        # Use library if available
        try:
            return base45.b45decode(encoded)
        except Exception as e:
            raise ValueError(f"Base45 decoding failed: {str(e)}")
    else:
        # Fallback implementation
        return _decode_base45_manual(encoded)


def _encode_base45_manual(data: bytes) -> str:
    """
    Manual Base45 encoding implementation.
    
    This is a fallback if the base45 library is not available.
    Implements RFC 9285 Base45 encoding.
    """
    if len(data) == 0:
        return ""
    
    result = []
    # Process data in pairs
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            # Two bytes
            value = data[i] * 256 + data[i + 1]
            # Convert to base 45 (3 digits)
            result.append(BASE45_CHARS[value % 45])
            value //= 45
            result.append(BASE45_CHARS[value % 45])
            value //= 45
            result.append(BASE45_CHARS[value])
        else:
            # Single byte
            value = data[i]
            result.append(BASE45_CHARS[value % 45])
            if value >= 45:
                result.append(BASE45_CHARS[value // 45])
    
    return ''.join(result)


def _decode_base45_manual(encoded: str) -> bytes:
    """
    Manual Base45 decoding implementation.
    
    This is a fallback if the base45 library is not available.
    Implements RFC 9285 Base45 decoding.
    """
    if len(encoded) == 0:
        return b""
    
    # Create reverse lookup
    char_to_value = {char: i for i, char in enumerate(BASE45_CHARS)}
    
    # Validate all characters are in Base45 set
    for char in encoded:
        if char not in char_to_value:
            raise ValueError(f"Invalid Base45 character: {char}")
    
    result = []
    i = 0
    while i < len(encoded):
        if i + 2 < len(encoded):
            # Three characters -> two bytes
            value = (char_to_value[encoded[i]] +
                    char_to_value[encoded[i + 1]] * 45 +
                    char_to_value[encoded[i + 2]] * 45 * 45)
            if value > 65535:
                raise ValueError("Invalid Base45 encoding: value too large")
            result.append(value // 256)
            result.append(value % 256)
            i += 3
        elif i + 1 < len(encoded):
            # Two characters -> one byte
            value = char_to_value[encoded[i]] + char_to_value[encoded[i + 1]] * 45
            if value > 255:
                raise ValueError("Invalid Base45 encoding: value too large")
            result.append(value)
            i += 2
        else:
            # Single character -> one byte
            result.append(char_to_value[encoded[i]])
            i += 1
    
    return bytes(result)


# Example usage and testing
if __name__ == "__main__":
    print("Testing Base45 encoding/decoding...")
    
    # Test data
    test_data = b"Hello, World! This is a test message for Base45 encoding."
    print(f"\nOriginal data: {test_data}")
    print(f"Data length: {len(test_data)} bytes")
    
    # Encode
    print("\nEncoding to Base45...")
    encoded = encode_base45(test_data)
    print(f"Encoded string: {encoded[:50]}..." if len(encoded) > 50 else f"Encoded string: {encoded}")
    print(f"Encoded length: {len(encoded)} characters")
    
    # Decode
    print("\nDecoding from Base45...")
    decoded = decode_base45(encoded)
    print(f"Decoded data: {decoded}")
    
    if test_data == decoded:
        print("\n✅ Base45 encoding/decoding test PASSED")
    else:
        print("\n❌ Base45 encoding/decoding test FAILED")
        print(f"Original: {test_data}")
        print(f"Decoded:  {decoded}")

