# src/FileAnalyzer/file_type.py

import os

MAGIC_NUMBERS = {
    b'\x7fELF': "ELF executable",
    b'%PDF': "PDF document",
    b'\x89PNG\r\n\x1a\n': "PNG image",
    b'\xff\xd8\xff': "JPEG image",
    b'PK\x03\x04': "ZIP archive (including .docx, .xlsx, .jar)",
    b'GIF87a': "GIF image",
    b'GIF89a': "GIF image",
    b'RIFF': "AVI / WAV",
    b'<!DOC': "HTML document",
    b'<html': "HTML document",
    b'<?xml': "XML document",
    b'{\n': "JSON document",
    b'BZh': "BZIP2 compressed",
    b'\x1f\x8b': "GZIP compressed",
    b'\xfd\x37\x7a\x58\x5a\x00': "XZ compressed",
}

def read_magic_bytes(file_path, size=16):
    """Lit les premiers octets du fichier"""
    try:
        with open(file_path, 'rb') as f:
            return f.read(size)
    except Exception as e:
        print(f"Erreur lecture magic bytes: {e}")
        return b''

def detect_magic(magic_bytes):
    """Détecte le type de fichier basé sur les magic numbers"""
    for signature, description in MAGIC_NUMBERS.items():
        if magic_bytes.startswith(signature):
            return description
    return "Unknown / Binaire"

def is_text_file(file_path, blocksize=512):
    """Détermine si un fichier est un fichier texte"""
    try:
        with open(file_path, 'rb') as f:
            block = f.read(blocksize)
        
        # Si le fichier est vide, c'est un fichier texte
        if len(block) == 0:
            return True
            
        # Vérifie la présence d'octets nuls (caractéristique des binaires)
        if b'\x00' in block:
            return False
            
        # Vérifie le ratio de caractères imprimables
        printable = 0
        for byte in block:
            if 32 <= byte <= 126 or byte in (9, 10, 13):  # caractères imprimables + tab, LF, CR
                printable += 1
        
        # Si plus de 80% sont imprimables, c'est probablement du texte
        return (printable / len(block)) > 0.8
        
    except Exception as e:
        print(f"Erreur détection texte: {e}")
        return False

def get_file_extension_info(file_path):
    """Donne des informations basées sur l'extension"""
    ext = os.path.splitext(file_path)[1].lower()
    
    extensions = {
        '.txt': "Fichier texte",
        '.py': "Script Python",
        '.c': "Code C",
        '.cpp': "Code C++",
        '.java': "Code Java",
        '.html': "Document HTML",
        '.css': "Feuille de style CSS",
        '.js': "Script JavaScript",
        '.json': "Fichier JSON",
        '.xml': "Fichier XML",
        '.csv': "Fichier CSV",
        '.md': "Markdown",
        '.pdf': "Document PDF",
        '.doc': "Document Word (ancien)",
        '.docx': "Document Word",
        '.xls': "Tableur Excel (ancien)",
        '.xlsx': "Tableur Excel",
        '.ppt': "Présentation PowerPoint (ancien)",
        '.pptx': "Présentation PowerPoint",
        '.jpg': "Image JPEG",
        '.jpeg': "Image JPEG",
        '.png': "Image PNG",
        '.gif': "Image GIF",
        '.bmp': "Image BMP",
        '.svg': "Image SVG",
        '.mp3': "Audio MP3",
        '.mp4': "Vidéo MP4",
        '.avi': "Vidéo AVI",
        '.mkv': "Vidéo Matroska",
        '.deb': "Package Debian",
        '.rpm': "Package Red Hat",
        '.iso': "Image disque ISO",
        '.so': "Bibliothèque partagée",
        '.dll': "Bibliothèque DLL",
        '.exe': "Exécutable Windows",
    }
    
    return extensions.get(ext, "")

def analyze_file_type(file_path):
    """Analyse complète du type de fichier"""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Fichier introuvable: {file_path}")

    # Taille du fichier
    file_size = os.path.getsize(file_path)
    
    # Lecture des magic bytes
    magic_bytes = read_magic_bytes(file_path)
    
    # Détection par magic number
    magic_type = detect_magic(magic_bytes)
    
    # Détection texte/binaire
    is_text = is_text_file(file_path)
    
    # Information par extension
    ext_info = get_file_extension_info(file_path)
    
    # Construction du type final
    if magic_type != "Unknown / Binaire":
        file_type = magic_type
    elif ext_info:
        file_type = ext_info
    elif is_text:
        file_type = "Fichier texte"
    else:
        file_type = "Fichier binaire inconnu"

    return {
        "file_type": file_type,
        "is_binary": not is_text,
        "magic_number": ' '.join(f'{b:02x}' for b in magic_bytes),
        "magic_ascii": ''.join(chr(b) if 32 <= b <= 126 else '.' for b in magic_bytes),
        "category": "text" if is_text else "binary",
        "extension_info": ext_info,
        "size": file_size,
        "extension": os.path.splitext(file_path)[1].lower()
    }