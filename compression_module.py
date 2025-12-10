"""
zstd Compression Module

This module handles:
- Compressing data with zstd (Zstandard)
- Decompressing data with zstd

zstd is a fast, modern compression algorithm that provides:
- High compression ratio
- Fast compression and decompression
- Better than gzip in most cases

Why compress before encryption?
- Encrypted data is random and doesn't compress well
- Compress plaintext to reduce payload size for QR codes
- Trade-off: Compression time vs. size reduction
"""

import zstandard as zstd


def compress_data(data: bytes, level: int = 3) -> bytes:
    """
    Compress data using zstd (Zstandard).
    
    Args:
        data: Data to compress (bytes)
        level: Compression level (1-22, default: 3)
               Higher = better compression but slower
               Level 3 is a good balance
    
    Returns:
        Compressed data (bytes)
    
    Raises:
        ValueError: If compression fails
    """
    if not isinstance(data, bytes):
        raise ValueError("data must be bytes")
    
    if len(data) == 0:
        return b""
    
    try:
        # Create compressor with specified level
        compressor = zstd.ZstdCompressor(level=level)
        compressed = compressor.compress(data)
        return compressed
    except Exception as e:
        raise ValueError(f"zstd compression failed: {str(e)}")


def decompress_data(compressed_data: bytes) -> bytes:
    """
    Decompress data using zstd (Zstandard).
    
    Args:
        compressed_data: Compressed data (bytes)
    
    Returns:
        Decompressed data (bytes)
    
    Raises:
        ValueError: If decompression fails (corrupted data, etc.)
    """
    if not isinstance(compressed_data, bytes):
        raise ValueError("compressed_data must be bytes")
    
    if len(compressed_data) == 0:
        return b""
    
    try:
        # Create decompressor
        decompressor = zstd.ZstdDecompressor()
        decompressed = decompressor.decompress(compressed_data)
        return decompressed
    except Exception as e:
        raise ValueError(f"zstd decompression failed: {str(e)}")


def get_compression_ratio(original: bytes, compressed: bytes) -> float:
    """
    Calculate compression ratio.
    
    Args:
        original: Original data size (bytes)
        compressed: Compressed data size (bytes)
    
    Returns:
        Compression ratio (compressed/original)
    """
    if len(original) == 0:
        return 0.0
    return len(compressed) / len(original)


# Example usage and testing
if __name__ == "__main__":
    print("Testing zstd compression/decompression...")
    
    # Test data (text with repetition - compresses well)
    test_data = b"This is a test message. " * 100
    print(f"\nOriginal data length: {len(test_data)} bytes")
    
    # Compress
    print("\nCompressing with zstd...")
    compressed = compress_data(test_data, level=3)
    print(f"Compressed data length: {len(compressed)} bytes")
    
    ratio = get_compression_ratio(test_data, compressed)
    print(f"Compression ratio: {ratio:.2%}")
    print(f"Space saved: {(1 - ratio):.2%}")
    
    # Decompress
    print("\nDecompressing with zstd...")
    decompressed = decompress_data(compressed)
    print(f"Decompressed data length: {len(decompressed)} bytes")
    
    if test_data == decompressed:
        print("\n✅ zstd compression/decompression test PASSED")
    else:
        print("\n❌ zstd compression/decompression test FAILED")
    
    # Test with binary data (less compressible)
    print("\n\nTesting with random binary data (less compressible)...")
    import os
    random_data = os.urandom(1000)
    print(f"Random data length: {len(random_data)} bytes")
    
    compressed_random = compress_data(random_data, level=3)
    print(f"Compressed random data length: {len(compressed_random)} bytes")
    ratio_random = get_compression_ratio(random_data, compressed_random)
    print(f"Compression ratio: {ratio_random:.2%}")
    print("(Random data doesn't compress well, which is expected)")

