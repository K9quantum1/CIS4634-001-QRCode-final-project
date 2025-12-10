# Project Summary

## Clean, Organized RSA+AES Encryption Project

This project implements a hybrid RSA-3072 + AES-256-GCM encryption system with a desktop GUI.

## Key Features

✅ **RSA-3072**: ~1536-bit primes, 128-bit security  
✅ **AES-256-GCM**: Maximum AES security with authentication  
✅ **Hybrid Encryption**: RSA for key exchange, AES for data  
✅ **PyCryptodome**: Pure Python - no DLL issues!  
✅ **Desktop GUI**: Simple tkinter interface  
✅ **QR Code Support**: Generate QR codes from encrypted data  
✅ **Local Processing**: Everything runs locally  

## Project Files

### Core Modules
- `rsa_module.py` - RSA-3072 key generation and OAEP encryption (PyCryptodome)
- `aes_module.py` - AES-256-GCM encryption (PyCryptodome)
- `cbor_module.py` - CBOR envelope creation/parsing
- `base45_module.py` - Base45 encoding/decoding
- `compression_module.py` - zstd compression/decompression

### Main Application
- `gui_app.py` - Desktop GUI application
- `encrypt.py` - Encryption orchestrator
- `decrypt.py` - Decryption orchestrator
- `qr_generator.py` - QR code generation

### Utilities
- `utils.py` - Helper functions
- `RUN.bat` - Easy launcher
- `requirements.txt` - Dependencies

### Documentation
- `README.md` - Main documentation
- `RSA_KEY_SIZE_EXPLANATION.md` - Explanation of key sizes vs prime sizes

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI
python gui_app.py
# Or double-click RUN.bat
```

## Encryption Flow

1. Compress data (zstd)
2. Encrypt with AES-256-GCM (random session key)
3. Encrypt session key with RSA-3072-OAEP
4. Package in CBOR envelope
5. Encode with Base45
6. Generate QR code (optional)

## Security

- **RSA-3072**: 3072-bit modulus (~1536-bit primes)
- **AES-256**: 256-bit keys
- **GCM Mode**: Authentication + integrity
- **OAEP Padding**: Secure RSA padding

All processing is local - no servers, no internet required!

