# RSA+AES Encryption Tool

A desktop GUI application for encrypting and decrypting data using hybrid RSA-3072 and AES-256-GCM encryption.

**✅ No DLL Issues!** This version uses PyCryptodome (pure Python) - no Visual C++ Redistributables needed!

## Features

- **RSA-3072 Key Generation**: Generate secure RSA key pairs
- **AES-256-GCM Encryption**: Fast, secure symmetric encryption
- **Hybrid Encryption**: Best of both worlds - RSA for key exchange, AES for data
- **Text & File Support**: Encrypt text or files
- **QR Code Generation & Reading**: Generate QR codes from encrypted data and scan them back to decrypt
- **📱 Mobile-Friendly Decryption**: Generate QR codes from decrypted messages to view on your phone!
- **Offline Operation**: Everything runs locally - no server or internet required
- **No DLL Issues**: Uses PyCryptodome (pure Python implementation)

## Quick Start

### Installation

1. **Install Python 3.9 or later**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or just:
   ```bash
   pip install pycryptodome cbor2 base45 zstandard qrcode[pil] Pillow pyzbar opencv-python
   ```

### Run the Application

**Easiest way:** Double-click `RUN.bat`

**Or manually:**
```bash
python gui_app.py
```

## Using the Application

### 1. Generate Keys (First Time)

1. Go to the "Generate Keys" tab
2. Enter a key name (e.g., "recipient")
3. Click "Generate Key Pair"
4. Keys will be saved as:
   - `recipient_private.pem` (keep this secret!)
   - `recipient_public.pem` (share this)

### 2. Encrypt Data

1. Go to the "Encrypt" tab
2. Select your public key file
3. Choose "Encrypt Text" or "Encrypt File"
4. Enter text or select a file
5. Click "Encrypt"
6. Copy the Base45 string (or use it in QR Code tab)

### 3. Decrypt Data

1. Go to the "Decrypt" tab
2. Select your private key file
3. **Option A**: Paste the Base45 encrypted string
   **Option B**: Click "Load from QR Code" to read a QR code image
4. Click "Decrypt"
5. View the decrypted message in the text area
6. **NEW!** Click "Generate QR Code for Phone" to create a scannable QR code of your decrypted message
7. Scan the QR code with your phone to view the message on your mobile device!

### 4. Generate QR Code

1. Go to the "QR Code" tab
2. Paste a Base45 string (or use encrypted data from Encrypt tab)
3. Click "Generate QR Code"
4. View or save the QR code image

### 5. Complete Workflow Example

**Full End-to-End Workflow:**

1. **Generate Key Pairs** (Generate Keys tab)
   - Click "Generate Key Pair" 
   - Save the public and private keys

2. **Encrypt Your Message** (Encrypt tab)
   - Select the recipient's public key
   - Write your secret message
   - Click "Encrypt"

3. **Create Encrypted QR Code** (QR Code tab)
   - The encrypted Base45 string is automatically added
   - Click "Generate QR Code"
   - Save the QR code image

4. **Decrypt and View on Phone** (Decrypt tab)
   - Select your private key
   - Click "Load from QR Code" and select the encrypted QR image
   - Click "Decrypt" to reveal the message
   - Click "Generate QR Code for Phone" 
   - **Scan the new QR code with your phone to read the message!**

**Quick Encrypt & Share:**
1. Encrypt tab → Enter message → Generate QR Code → Save QR image
2. Send the QR code image to someone (e.g., via email)

**Decrypt & View on Phone:**
1. Decrypt tab → Load from QR Code → Decrypt → Generate QR Code for Phone
2. Scan with your phone to read the secret message!

## Encryption Scheme

This tool uses a hybrid encryption system:

1. **Compression**: Data is compressed with zstd
2. **AES-256-GCM**: Compressed data is encrypted with a random session key
3. **RSA-3072-OAEP**: The session key is encrypted with the recipient's public key
4. **CBOR Packaging**: Everything is packaged in a CBOR envelope
5. **Base45 Encoding**: Encoded for QR code compatibility

## Security

- **RSA-3072**: 128-bit security level
- **AES-256**: Maximum AES security
- **GCM Mode**: Provides authentication and integrity
- **OAEP Padding**: Secure RSA padding scheme

## Project Structure

```
├── gui_app.py                 # Main GUI application
├── rsa_module.py              # RSA-3072 using PyCryptodome
├── aes_module.py             # AES-256-GCM using PyCryptodome
├── cbor_module.py            # CBOR envelope handling
├── base45_module.py          # Base45 encoding
├── compression_module.py      # zstd compression
├── qr_generator.py           # QR code generation
├── qr_reader.py              # QR code reading/scanning
├── encrypt.py                # Encryption orchestrator
├── decrypt.py                # Decryption orchestrator
├── utils.py                  # Helper functions
└── RUN.bat                   # Easy launcher
```

## Requirements

- Python 3.9+
- pycryptodome (pure Python - no DLL issues!)
- cbor2
- base45
- zstandard
- qrcode
- Pillow
- pyzbar (for QR code reading)
- opencv-python (for QR code reading)

## Why No DLL Issues?

This version uses **PyCryptodome** instead of the `cryptography` library:
- ✅ Pure Python implementation
- ✅ No Visual C++ Redistributables needed
- ✅ No Windows DLL issues
- ✅ Works immediately after installation
- ✅ Same security level (RSA-3072 + AES-256-GCM)

## Troubleshooting

### Import errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### GUI doesn't open

Make sure tkinter is installed (usually comes with Python):
```bash
# On Linux, you might need:
sudo apt install python3-tk
```

## License

This is an educational project demonstrating RSA and AES encryption schemes.
