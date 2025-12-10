"""
RSA+AES Encryption GUI Application

A desktop GUI for encrypting and decrypting data using hybrid RSA-3072 and AES-256-GCM encryption.
Uses PyCryptodome (pure Python) - no DLL issues!
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys

# Import encryption modules
sys.path.insert(0, os.path.dirname(__file__))

try:
    from rsa_module import generate_key_pair, save_key_pair, load_public_key, load_private_key, encrypt_with_rsa_oaep, decrypt_with_rsa_oaep
    from aes_module import encrypt_with_aes_gcm, decrypt_with_aes_gcm
except ImportError:
    messagebox.showerror("Error", "PyCryptodome not installed!\n\nRun: pip install pycryptodome")
    sys.exit(1)

from compression_module import compress_data, decompress_data
from cbor_module import create_envelope, parse_envelope
from base45_module import encode_base45, decode_base45
from qr_generator import generate_qr_code
from qr_reader import read_qr_code
from PIL import Image, ImageTk


def encrypt_data_internal(data: bytes, public_key_path: str) -> str:
    """Internal encryption function"""
    # Step 1: Compress
    compressed_data = compress_data(data)
    
    # Step 2: Encrypt with AES-256-GCM
    ciphertext, tag, session_key, iv = encrypt_with_aes_gcm(compressed_data)
    
    # Step 3: Encrypt session key with RSA-OAEP
    public_key = load_public_key(public_key_path)
    encrypted_session_key = encrypt_with_rsa_oaep(session_key, public_key)
    
    # Step 4: Create CBOR envelope
    cbor_envelope = create_envelope(
        encrypted_key=encrypted_session_key,
        iv=iv,
        tag=tag,
        ciphertext=ciphertext
    )
    
    # Step 5: Encode with Base45
    base45_string = encode_base45(cbor_envelope)
    
    return base45_string


def decrypt_data_internal(base45_string: str, private_key_path: str) -> bytes:
    """Internal decryption function"""
    # Step 1: Decode Base45
    cbor_data = decode_base45(base45_string)
    
    # Step 2: Parse CBOR envelope
    envelope = parse_envelope(cbor_data)
    
    # Step 3: Decrypt session key
    private_key = load_private_key(private_key_path)
    session_key = decrypt_with_rsa_oaep(envelope['encrypted_key'], private_key)
    
    # Step 4: Decrypt with AES-GCM
    compressed_data = decrypt_with_aes_gcm(
        envelope['ciphertext'],
        envelope['tag'],
        session_key,
        envelope['iv']
    )
    
    # Step 5: Decompress
    plaintext = decompress_data(compressed_data)
    
    return plaintext


class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA+AES Encryption Tool")
        self.root.geometry("900x800")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_key_tab()
        self.create_encrypt_tab()
        self.create_decrypt_tab()
        self.create_qr_tab()
        
    def create_key_tab(self):
        """Tab for generating RSA key pairs"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Generate Keys")
        
        ttk.Label(frame, text="RSA-3072 Key Pair Generator", font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(frame, text="Key Name:").pack(pady=5)
        self.key_name_entry = ttk.Entry(frame, width=30)
        self.key_name_entry.insert(0, "recipient")
        self.key_name_entry.pack(pady=5)
        
        ttk.Button(frame, text="Generate Key Pair", command=self.generate_keys).pack(pady=10)
        
        self.key_status = ttk.Label(frame, text="", foreground="green")
        self.key_status.pack(pady=5)
        
    def create_encrypt_tab(self):
        """Tab for encryption"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Encrypt")
        
        ttk.Label(frame, text="Encrypt Data", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Public key selection
        key_frame = ttk.Frame(frame)
        key_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(key_frame, text="Public Key:").pack(side=tk.LEFT)
        self.public_key_entry = ttk.Entry(key_frame, width=40)
        self.public_key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(key_frame, text="Browse", command=self.browse_public_key).pack(side=tk.LEFT)
        
        # Mode selection
        mode_frame = ttk.Frame(frame)
        mode_frame.pack(fill=tk.X, padx=20, pady=10)
        self.encrypt_mode = tk.StringVar(value="text")
        ttk.Radiobutton(mode_frame, text="Encrypt Text", variable=self.encrypt_mode, value="text").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Encrypt File", variable=self.encrypt_mode, value="file").pack(side=tk.LEFT, padx=10)
        
        # Text input
        self.text_frame = ttk.Frame(frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        ttk.Label(self.text_frame, text="Text to Encrypt:").pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(self.text_frame, height=10, width=60)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # File input
        self.file_frame = ttk.Frame(frame)
        ttk.Label(self.file_frame, text="File to Encrypt:").pack(anchor=tk.W)
        file_input_frame = ttk.Frame(self.file_frame)
        file_input_frame.pack(fill=tk.X, pady=5)
        self.file_entry = ttk.Entry(file_input_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(file_input_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)
        
        # Encrypt button
        ttk.Button(frame, text="Encrypt", command=self.encrypt_data).pack(pady=10)
        
        # Result
        ttk.Label(frame, text="Encrypted Result (Base45):").pack(pady=5)
        self.encrypt_result = scrolledtext.ScrolledText(frame, height=8, width=60)
        self.encrypt_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Update mode handler
        self.encrypt_mode.trace('w', self.update_encrypt_mode)
        self.update_encrypt_mode()
        
    def create_decrypt_tab(self):
        """Tab for decryption"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Decrypt")
        
        ttk.Label(frame, text="Decrypt Data", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Private key selection
        key_frame = ttk.Frame(frame)
        key_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(key_frame, text="Private Key:").pack(side=tk.LEFT)
        self.private_key_entry = ttk.Entry(key_frame, width=40)
        self.private_key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(key_frame, text="Browse", command=self.browse_private_key).pack(side=tk.LEFT)
        
        # Base45 input
        input_label_frame = ttk.Frame(frame)
        input_label_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(input_label_frame, text="Base45 Encrypted String:").pack(side=tk.LEFT)
        ttk.Button(input_label_frame, text="Load from QR Code", command=self.load_qr_code).pack(side=tk.RIGHT)
        
        self.decrypt_input = scrolledtext.ScrolledText(frame, height=6, width=60)
        self.decrypt_input.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Decrypt button
        ttk.Button(frame, text="Decrypt", command=self.decrypt_data).pack(pady=10)
        
        # Result
        result_label_frame = ttk.Frame(frame)
        result_label_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(result_label_frame, text="Decrypted Result:").pack(side=tk.LEFT)
        
        self.decrypt_result = scrolledtext.ScrolledText(frame, height=6, width=60)
        self.decrypt_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Button frame for actions
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Save Decrypted Data to File", command=self.save_decrypted).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate QR Code for Phone", command=self.generate_qr_from_decrypted).pack(side=tk.LEFT, padx=5)
        
        # QR code display for decrypted message
        ttk.Label(frame, text="Scan this QR code on your phone to view the message:").pack(pady=5)
        self.decrypt_qr_label = ttk.Label(frame, text="QR code will appear here after generating")
        self.decrypt_qr_label.pack(pady=5)
        
        # Save QR button
        ttk.Button(frame, text="Save Decrypted Message QR", command=self.save_decrypted_qr).pack(pady=5)
        
        # Store QR image
        self.decrypt_qr_image = None
        self.decrypt_qr_path = None
        
    def create_qr_tab(self):
        """Tab for QR code generation"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="QR Code")
        
        ttk.Label(frame, text="Generate QR Code", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Base45 input
        ttk.Label(frame, text="Base45 String:").pack(pady=5)
        self.qr_input = scrolledtext.ScrolledText(frame, height=6, width=60)
        self.qr_input.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Generate button
        ttk.Button(frame, text="Generate QR Code", command=self.generate_qr).pack(pady=10)
        
        # QR code display
        self.qr_label = ttk.Label(frame, text="QR code will appear here")
        self.qr_label.pack(pady=10)
        
        # Save button
        ttk.Button(frame, text="Save QR Code", command=self.save_qr).pack(pady=5)
        self.qr_image = None
        self.qr_path = None
        
    def generate_keys(self):
        """Generate RSA key pair"""
        key_name = self.key_name_entry.get().strip()
        if not key_name:
            messagebox.showerror("Error", "Please enter a key name")
            return
        
        try:
            private_key, public_key = generate_key_pair()
            private_path, public_path = save_key_pair(private_key, public_key, key_name)
            
            self.key_status.config(text=f"Keys generated!\nPrivate: {private_path}\nPublic: {public_path}")
            messagebox.showinfo("Success", f"Key pair generated successfully!\n\nPrivate: {private_path}\nPublic: {public_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate keys: {str(e)}")
    
    def browse_public_key(self):
        """Browse for public key file"""
        filename = filedialog.askopenfilename(
            title="Select Public Key",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if filename:
            self.public_key_entry.delete(0, tk.END)
            self.public_key_entry.insert(0, filename)
    
    def browse_private_key(self):
        """Browse for private key file"""
        filename = filedialog.askopenfilename(
            title="Select Private Key",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if filename:
            self.private_key_entry.delete(0, tk.END)
            self.private_key_entry.insert(0, filename)
    
    def browse_file(self):
        """Browse for file to encrypt"""
        filename = filedialog.askopenfilename(title="Select File to Encrypt")
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
    
    def load_qr_code(self):
        """Load and decode QR code image"""
        filename = filedialog.askopenfilename(
            title="Select QR Code Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if not filename:
            return
        
        try:
            # Read QR code from image
            base45_string = read_qr_code(filename)
            
            # Fill in the decrypt input field
            self.decrypt_input.delete("1.0", tk.END)
            self.decrypt_input.insert("1.0", base45_string)
            
            messagebox.showinfo("Success", f"QR code loaded successfully!\n\nData length: {len(base45_string)} characters")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read QR code:\n\n{str(e)}")
    
    def update_encrypt_mode(self, *args):
        """Update UI based on encrypt mode"""
        mode = self.encrypt_mode.get()
        if mode == "text":
            self.text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            self.file_frame.pack_forget()
        else:
            self.text_frame.pack_forget()
            self.file_frame.pack(fill=tk.X, padx=20, pady=5)
    
    def encrypt_data(self):
        """Encrypt data based on selected mode"""
        public_key_path = self.public_key_entry.get().strip()
        if not public_key_path or not os.path.exists(public_key_path):
            messagebox.showerror("Error", "Please select a valid public key file")
            return
        
        try:
            mode = self.encrypt_mode.get()
            if mode == "text":
                text = self.text_input.get("1.0", tk.END).strip()
                if not text:
                    messagebox.showerror("Error", "Please enter text to encrypt")
                    return
                plaintext = text.encode('utf-8')
            else:
                file_path = self.file_entry.get().strip()
                if not file_path or not os.path.exists(file_path):
                    messagebox.showerror("Error", "Please select a valid file")
                    return
                with open(file_path, 'rb') as f:
                    plaintext = f.read()
            
            base45_string = encrypt_data_internal(plaintext, public_key_path)
            
            self.encrypt_result.delete("1.0", tk.END)
            self.encrypt_result.insert("1.0", base45_string)
            
            # Also populate QR tab
            self.qr_input.delete("1.0", tk.END)
            self.qr_input.insert("1.0", base45_string)
            
            messagebox.showinfo("Success", "Encryption completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")
    
    def decrypt_data(self):
        """Decrypt Base45 string"""
        private_key_path = self.private_key_entry.get().strip()
        if not private_key_path or not os.path.exists(private_key_path):
            messagebox.showerror("Error", "Please select a valid private key file")
            return
        
        base45_string = self.decrypt_input.get("1.0", tk.END).strip()
        if not base45_string:
            messagebox.showerror("Error", "Please enter Base45 encrypted string")
            return
        
        try:
            data = decrypt_data_internal(base45_string, private_key_path)
            
            # Try to decode as text
            try:
                text = data.decode('utf-8')
                self.decrypt_result.delete("1.0", tk.END)
                self.decrypt_result.insert("1.0", text)
                self.decrypted_data = data
                self.is_binary = False
            except UnicodeDecodeError:
                # Binary data
                self.decrypt_result.delete("1.0", tk.END)
                self.decrypt_result.insert("1.0", f"[Binary data - {len(data)} bytes]\n\nUse 'Save Decrypted Data to File' to save this file.")
                self.decrypted_data = data
                self.is_binary = True
            
            messagebox.showinfo("Success", "Decryption completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
    
    def save_decrypted(self):
        """Save decrypted data to file"""
        if not hasattr(self, 'decrypted_data'):
            messagebox.showerror("Error", "No decrypted data to save. Please decrypt first.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Decrypted Data",
            defaultextension=".txt"
        )
        if filename:
            try:
                with open(filename, 'wb') as f:
                    f.write(self.decrypted_data)
                messagebox.showinfo("Success", f"Data saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def generate_qr(self):
        """Generate QR code from Base45 string"""
        base45_string = self.qr_input.get("1.0", tk.END).strip()
        if not base45_string:
            messagebox.showerror("Error", "Please enter Base45 string")
            return
        
        try:
            # Generate QR code
            img = generate_qr_code(base45_string)
            self.qr_path = "temp_qr.png"
            img.save(self.qr_path)
            
            # Calculate maximum display size (leave some padding)
            # Use window size as reference, with reasonable defaults
            self.root.update_idletasks()  # Ensure window is updated
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            # Set maximum display dimensions (leave padding for other UI elements)
            max_width = min(window_width - 150, 600) if window_width > 0 else 600
            max_height = min(window_height - 300, 500) if window_height > 0 else 500
            
            # Get original image dimensions
            orig_width, orig_height = img.size
            
            # Calculate scaling factor to fit within bounds while maintaining aspect ratio
            width_ratio = max_width / orig_width if orig_width > 0 and max_width > 0 else 1
            height_ratio = max_height / orig_height if orig_height > 0 and max_height > 0 else 1
            scale_factor = min(width_ratio, height_ratio, 1.0)  # Don't scale up, only down
            
            # Resize image if needed
            if scale_factor < 1.0:
                new_width = max(1, int(orig_width * scale_factor))
                new_height = max(1, int(orig_height * scale_factor))
                img_display = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                img_display = img
            
            # Display in GUI
            photo = ImageTk.PhotoImage(img_display)
            self.qr_label.config(image=photo, text="")
            self.qr_label.image = photo  # Keep a reference
            self.qr_image = img  # Keep original for saving
            
            messagebox.showinfo("Success", "QR code generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
    
    def save_qr(self):
        """Save QR code to file"""
        if not self.qr_image:
            messagebox.showerror("Error", "No QR code to save. Please generate one first.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save QR Code",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.qr_image.save(filename)
                messagebox.showinfo("Success", f"QR code saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save QR code: {str(e)}")
    
    def generate_qr_from_decrypted(self):
        """Generate QR code from decrypted message for viewing on phone"""
        if not hasattr(self, 'decrypted_data'):
            messagebox.showerror("Error", "No decrypted data available. Please decrypt a message first.")
            return
        
        # Check if data is binary
        if hasattr(self, 'is_binary') and self.is_binary:
            messagebox.showerror("Error", "Cannot generate QR code from binary data. This feature only works with text messages.")
            return
        
        try:
            # Get the decrypted text
            text = self.decrypted_data.decode('utf-8')
            
            # Generate QR code from the decrypted text
            img = generate_qr_code(text)
            self.decrypt_qr_path = "temp_decrypted_qr.png"
            img.save(self.decrypt_qr_path)
            
            # Calculate display size
            self.root.update_idletasks()
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            max_width = min(window_width - 150, 400) if window_width > 0 else 400
            max_height = min(window_height - 400, 400) if window_height > 0 else 400
            
            # Get original dimensions
            orig_width, orig_height = img.size
            
            # Calculate scaling
            width_ratio = max_width / orig_width if orig_width > 0 and max_width > 0 else 1
            height_ratio = max_height / orig_height if orig_height > 0 and max_height > 0 else 1
            scale_factor = min(width_ratio, height_ratio, 1.0)
            
            # Resize if needed
            if scale_factor < 1.0:
                new_width = max(1, int(orig_width * scale_factor))
                new_height = max(1, int(orig_height * scale_factor))
                img_display = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                img_display = img
            
            # Display in GUI
            photo = ImageTk.PhotoImage(img_display)
            self.decrypt_qr_label.config(image=photo, text="")
            self.decrypt_qr_label.image = photo
            self.decrypt_qr_image = img
            
            messagebox.showinfo("Success", "QR code generated! Scan it with your phone to view the decrypted message.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
    
    def save_decrypted_qr(self):
        """Save the decrypted message QR code to file"""
        if not self.decrypt_qr_image:
            messagebox.showerror("Error", "No QR code to save. Please generate a QR code from decrypted message first.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Decrypted Message QR Code",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.decrypt_qr_image.save(filename)
                messagebox.showinfo("Success", f"Decrypted message QR code saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save QR code: {str(e)}")


def main():
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

