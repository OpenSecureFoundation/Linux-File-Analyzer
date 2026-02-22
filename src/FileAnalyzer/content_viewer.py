# src/FileAnalyzer/content_viewer.py

def read_text_content(file_path, max_size):
    with open(file_path, 'r', errors='replace') as f:
        content = f.read(max_size)
        truncated = f.read(1) != ""
    return content, truncated

def hexdump(data):
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08x}  {hex_part:<48}  {ascii_part}")
    return "\n".join(lines)

def read_binary_content(file_path, max_size):
    with open(file_path, 'rb') as f:
        data = f.read(max_size)
        truncated = f.read(1) != b""
    return hexdump(data), truncated

def display_content(file_path, is_binary, max_size=1024*1024):

    result = {
        "preview": None
    }

    if is_binary:
        result["preview"] = "Fichier binaire - affichage non supporté."
        return result

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_size)

        result["preview"] = content

    except Exception as e:
        result["preview"] = f"Erreur lecture contenu : {e}"

    return result
