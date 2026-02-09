    # src/FileAnalyzer/physical_layout.py

import subprocess
import re

def run_filefrag(file_path):
    """
    Exécute filefrag -v pour récupérer les extents EXT4
    """
    cmd = ["filefrag", "-v", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError("Erreur lors de l'analyse des extents")

    return result.stdout

def parse_extents(output):
    extents = []
    lines = output.splitlines()

    for line in lines:
        # Exemple ligne :
        # 0: 0..7: 105632..105639: 8 blocks
        match = re.search(
            r'^\s*\d+:\s+(\d+)\.\.\d+:\s+(\d+)\.\.\d+:\s+(\d+)\s+blocks',
            line
        )
        if match:
            logical_offset = int(match.group(1))
            physical_block = int(match.group(2))
            length = int(match.group(3))

            extents.append({
                "logical_offset": logical_offset,
                "physical_block": physical_block,
                "length": length
            })

    return extents

def analyze_physical_layout(file_path):
    output = run_filefrag(file_path)
    extents = parse_extents(output)

    return {
        "total_extents": len(extents),
        "extents": extents
    }
