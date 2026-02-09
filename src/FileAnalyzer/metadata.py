# src/FileAnalyzer/metadata.py

import os
import stat
import pwd
import grp
import subprocess
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

    return {
        "permissions": format_permissions(stat_info.st_mode),
        "owner": owner,
        "group": group,
        "size_bytes": stat_info.st_size,
        "size_blocks": stat_info.st_blocks,
        "links": stat_info.st_nlink,
        "timestamps": {
            "atime": datetime.fromtimestamp(stat_info.st_atime),
            "mtime": datetime.fromtimestamp(stat_info.st_mtime),
            "ctime": datetime.fromtimestamp(stat_info.st_ctime),
            "btime": get_birth_time(file_path)
        },
        "flags": []  # extensible (chattr)
    }
