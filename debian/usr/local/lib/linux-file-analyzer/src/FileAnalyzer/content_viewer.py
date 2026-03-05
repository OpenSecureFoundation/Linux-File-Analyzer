# src/FileAnalyzer/content_viewer.py

import os

def read_text_content(file_path, max_size):
    """Lit le contenu d'un fichier texte"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(max_size)
            # Vérifier si le fichier est plus long
            try:
                f.read(1)
                truncated = True
            except:
                truncated = False
        return content, truncated
    except Exception as e:
        return f"Erreur lecture: {e}", False

def hexdump(data, max_bytes=512):
    """Génère un hex dump des données"""
    if len(data) > max_bytes:
        data = data[:max_bytes]
        truncated = True
    else:
        truncated = False
    
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08x}  {hex_part:<48}  {ascii_part}")
    
    result = "\n".join(lines)
    if truncated:
        result += "\n... (tronqué)"
    return result

def read_binary_content(file_path, max_size=1024):
    """Lit un fichier binaire et retourne un hex dump"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read(max_size)
            
        return hexdump(data), len(data) >= max_size
    except Exception as e:
        return f"Erreur lecture binaire: {e}", False

def get_pdf_info(file_path, max_size=4096):
    """Extrait des informations d'un fichier PDF"""
    info = {}
    try:
        with open(file_path, 'rb') as f:
            content = f.read(max_size).decode('latin-1', errors='ignore')
        
        # Version PDF
        import re
        version_match = re.search(r'%PDF-(\d+\.\d+)', content)
        if version_match:
            info["Version"] = version_match.group(1)
        
        # Titre
        title_match = re.search(r'/Title\s*\(([^)]+)\)', content)
        if title_match:
            info["Titre"] = title_match.group(1)
        
        # Auteur
        author_match = re.search(r'/Author\s*\(([^)]+)\)', content)
        if author_match:
            info["Auteur"] = author_match.group(1)
        
        # Pages approximatif
        pages = len(re.findall(r'/Type\s*/Page', content))
        if pages:
            info["Pages"] = str(pages)
            
    except Exception as e:
        info["Erreur"] = str(e)
    
    return info

def get_image_info(file_path):
    """Informations basiques sur une image"""
    info = {}
    ext = os.path.splitext(file_path)[1].lower()
    file_size = os.path.getsize(file_path)
    
    info["Format"] = ext.upper().replace('.', '')
    info["Taille"] = f"{file_size} octets"
    if file_size > 1024*1024:
        info["Taille"] += f" ({file_size/(1024*1024):.2f} Mo)"
    elif file_size > 1024:
        info["Taille"] += f" ({file_size/1024:.2f} Ko)"
    
    return info

def get_deb_info(file_path):
    """Informations sur un package Debian"""
    info = {}
    file_size = os.path.getsize(file_path)
    
    info["Type"] = "Package Debian"
    info["Taille"] = f"{file_size} octets"
    if file_size > 1024*1024:
        info["Taille"] += f" ({file_size/(1024*1024):.2f} Mo)"
    
    # Essayer d'extraire le nom du package
    filename = os.path.basename(file_path)
    if '_' in filename:
        parts = filename.split('_')
        info["Nom"] = parts[0]
        if len(parts) > 1:
            info["Version"] = parts[1].replace('.deb', '')
    
    return info

def display_content(file_path, is_binary, max_size=1024*1024):
    """
    Affiche le contenu du fichier de manière appropriée selon son type
    """
    # Déterminer le type par l'extension
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    # Structure de base
    result = {
        "is_binary": is_binary,
        "file_type": "Inconnu",
        "file_name": filename,
        "file_size": file_size,
        "preview": "",
        "hex_dump": "",
        "metadata": {},
        "error": None
    }
    
    try:
        # Détection du type réel
        if not is_binary:
            # Fichier texte
            result["file_type"] = "Fichier texte"
            content, truncated = read_text_content(file_path, max_size)
            result["preview"] = content
            if truncated:
                result["preview"] += "\n\n... (fichier tronqué, dépasse la limite d'affichage)"
        
        elif ext == '.pdf' or (is_binary and 'PDF' in str(file_path)):
            # Fichier PDF
            result["file_type"] = "Document PDF"
            result["metadata"] = get_pdf_info(file_path)
            hex_data, _ = read_binary_content(file_path, 512)
            result["hex_dump"] = hex_data
            result["preview"] = "Document PDF - Utilisez un lecteur PDF pour voir le contenu"
        
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            # Fichier image
            result["file_type"] = f"Image {ext.upper()}"
            result["metadata"] = get_image_info(file_path)
            result["preview"] = "Image - Utilisez un visualiseur d'images"
        
        elif ext == '.deb':
            # Package Debian
            result["file_type"] = "Package Debian"
            result["metadata"] = get_deb_info(file_path)
            hex_data, _ = read_binary_content(file_path, 256)
            result["hex_dump"] = hex_data
            result["preview"] = "Package Debian - Contient des fichiers binaires compressés"
        
        elif ext in ['.mp3', '.wav', '.ogg']:
            result["file_type"] = "Fichier Audio"
            result["preview"] = "Fichier audio - Utilisez un lecteur audio"
        
        elif ext in ['.mp4', '.avi', '.mkv']:
            result["file_type"] = "Fichier Vidéo"
            result["preview"] = "Fichier vidéo - Utilisez un lecteur vidéo"
        
        elif ext in ['.so', '.dll', '.exe']:
            result["file_type"] = "Binaire exécutable"
            hex_data, _ = read_binary_content(file_path, 256)
            result["hex_dump"] = hex_data
            result["preview"] = "Fichier binaire exécutable"
        
        else:
            # Autre fichier binaire
            result["file_type"] = "Fichier binaire"
            hex_data, _ = read_binary_content(file_path, 256)
            result["hex_dump"] = hex_data
            result["preview"] = f"Fichier binaire - {file_size} octets"
    
    except Exception as e:
        result["error"] = str(e)
        result["preview"] = f"Erreur lors de la lecture: {e}"
    
    return result