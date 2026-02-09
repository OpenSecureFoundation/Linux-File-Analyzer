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

def display_content(file_path, is_binary, max_size=1024 * 1024):
    if is_binary:
        content, truncated = read_binary_content(file_path, max_size)
        mode = "hexadecimal"
    else:
        content, truncated = read_text_content(file_path, max_size)
        mode = "text"

    return {
        "mode": mode,
        "content": content,
        "truncated": truncated
    }
