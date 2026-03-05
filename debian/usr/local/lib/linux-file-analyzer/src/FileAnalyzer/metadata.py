# src/FileAnalyzer/metadata.py

import os
import stat
import pwd
import grp
from datetime import datetime

def format_permissions(mode):
    return stat.filemode(mode)

def get_owner_group(uid, gid):
    return pwd.getpwuid(uid).pw_name, grp.getgrgid(gid).gr_name

def get_birth_time(file_path):
    """
    EXT4 supporte btime, accessible via stat (Linux récent)
    """
    try:
        stat_info = os.stat(file_path)
        if hasattr(stat_info, "st_birthtime"):
            return datetime.fromtimestamp(stat_info.st_birthtime)
    except Exception:
        pass
    return None

def extract_metadata(file_path):
    stat_info = os.stat(file_path)

    owner, group = get_owner_group(stat_info.st_uid, stat_info.st_gid)

    # Calcul de la taille sur disque en octets
    # st_blocks est en blocs de 512 octets (norme POSIX)
    disk_size_bytes = stat_info.st_blocks * 512
    
    # Taille de bloc typique du système de fichiers
    # On peut l'obtenir via statvfs, mais 4096 est la valeur par défaut EXT4
    try:
        # Essayer d'obtenir la taille de bloc réelle
        statvfs = os.statvfs(file_path)
        block_size = statvfs.f_bsize
    except:
        block_size = 4096  # Valeur par défaut EXT4
    
    # Nombre de blocs alloués (arrondi supérieur)
    blocks_allocated = (stat_info.st_size + block_size - 1) // block_size

    # Calcul de l'espace perdu (fragmentation interne)
    waste_bytes = disk_size_bytes - stat_info.st_size
    waste_percent = (waste_bytes / stat_info.st_size * 100) if stat_info.st_size > 0 else 0

    metadata = {
        "permissions": format_permissions(stat_info.st_mode),
        "owner": owner,
        "group": group,
        "size_bytes": stat_info.st_size,
        "size_blocks": stat_info.st_blocks,
        "disk_size_bytes": disk_size_bytes,  # AJOUTÉ
        "disk_size_human": f"{disk_size_bytes / 1024:.2f} Ko" if disk_size_bytes < 1024*1024 else f"{disk_size_bytes / (1024*1024):.2f} Mo",
        "block_size": block_size,
        "blocks_allocated": blocks_allocated,
        "waste_bytes": waste_bytes,
        "waste_percent": round(waste_percent, 2),
        "links": stat_info.st_nlink,
        "inode": stat_info.st_ino,
        "device": stat_info.st_dev,
        "timestamps": {
            "atime": datetime.fromtimestamp(stat_info.st_atime),
            "mtime": datetime.fromtimestamp(stat_info.st_mtime),
            "ctime": datetime.fromtimestamp(stat_info.st_ctime),
            "btime": get_birth_time(file_path)
        },
        "flags": []  # extensible (chattr)
    }

    return metadata

def get_metadata_display(metadata):
    """
    Retourne une version formatée pour l'affichage
    """
    display = {}
    
    for key, value in metadata.items():
        if key == "timestamps":
            ts = value
            display["Dernier accès (atime)"] = ts["atime"].strftime("%Y-%m-%d %H:%M:%S")
            display["Dernière modification (mtime)"] = ts["mtime"].strftime("%Y-%m-%d %H:%M:%S")
            display["Changement inode (ctime)"] = ts["ctime"].strftime("%Y-%m-%d %H:%M:%S")
            if ts["btime"]:
                display["Création (btime)"] = ts["btime"].strftime("%Y-%m-%d %H:%M:%S")
        elif key not in ["block_size", "waste_bytes"]:  # On garde waste_percent mais pas waste_bytes
            # Convertir les clés en français pour l'affichage
            key_map = {
                "permissions": "Permissions",
                "owner": "Propriétaire",
                "group": "Groupe",
                "size_bytes": "Taille logique",
                "size_blocks": "Blocs (512o)",
                "disk_size_bytes": "Taille sur disque",
                "disk_size_human": "Taille disque (formatée)",
                "blocks_allocated": "Blocs alloués (4K)",
                "waste_percent": "Espace perdu (%)",
                "links": "Liens physiques",
                "inode": "Inode",
                "device": "Périphérique",
                "flags": "Flags"
            }
            display_key = key_map.get(key, key)
            
            if key == "size_bytes":
                # Formater la taille logique
                if value > 1024*1024*1024:
                    display[display_key] = f"{value} octets ({value/(1024*1024*1024):.2f} Go)"
                elif value > 1024*1024:
                    display[display_key] = f"{value} octets ({value/(1024*1024):.2f} Mo)"
                elif value > 1024:
                    display[display_key] = f"{value} octets ({value/1024:.2f} Ko)"
                else:
                    display[display_key] = f"{value} octets"
            elif key == "disk_size_bytes":
                # Formater la taille disque
                if value > 1024*1024*1024:
                    display[display_key] = f"{value} octets ({value/(1024*1024*1024):.2f} Go)"
                elif value > 1024*1024:
                    display[display_key] = f"{value} octets ({value/(1024*1024):.2f} Mo)"
                elif value > 1024:
                    display[display_key] = f"{value} octets ({value/1024:.2f} Ko)"
                else:
                    display[display_key] = f"{value} octets"
            elif key == "waste_percent":
                display[display_key] = f"{value}%"
            else:
                display[display_key] = value
    
    return display