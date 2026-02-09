# src/FileAnalyzer/utils.py

import os
import subprocess

def check_root():
    return os.geteuid() == 0

def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def is_ext4(file_path):
    try:
        result = subprocess.run(
            ["df", "-T", file_path],
            capture_output=True,
            text=True
        )
        return "ext4" in result.stdout.lower()
    except Exception:
        return False
