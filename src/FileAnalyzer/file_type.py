# src/FileAnalyzer/file_type.py

import os

MAGIC_NUMBERS = {
    b'\x7fELF': "ELF executable",
    b'%PDF': "PDF document",
    b'\x89PNG\r\n\x1a\n': "PNG image",
    b'\xff\xd8\xff': "JPEG image",
    b'PK\x03\x04': "ZIP archive",
}

def read_magic_bytes(file_path, size=16):
    with open(file_path, 'rb') as f:
        return f.read(size)

def detect_magic(magic_bytes):
    for signature, description in MAGIC_NUMBERS.items():
        if magic_bytes.startswith(signature):
            return description
    return "Unknown"

def is_text_file(file_path, blocksize=512):
    try:
        with open(file_path, 'rb') as f:
            block = f.read(blocksize)
        if b'\x00' in block:
            return False
        return True
    except Exception:
        return False

def analyze_file_type(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError("Fichier introuvable")

    magic_bytes = read_magic_bytes(file_path)
    description = detect_magic(magic_bytes)
    text = is_text_file(file_path)

    return {
        "file_type": description,
        "is_binary": not text,
        "magic_number": magic_bytes.hex(" "),
        "category": "text" if text else "binary"
    }
