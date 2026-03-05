    # src/FileAnalyzer/physical_layout.py

import subprocess
import re

def analyze_physical_layout(file_path):
    result = {
        "total_extents": 0,
        "extents": []
    }

    try:
        process = subprocess.run(
            ["filefrag", "-v", file_path],
            capture_output=True,
            text=True
        )

        output = process.stdout.splitlines()

        extent_pattern = re.compile(
            r"\s*\d+:\s+(\d+)\.\.\s*(\d+):\s+(\d+)\.\.\s*(\d+):\s+(\d+)"
        )

        for line in output:
            match = extent_pattern.search(line)
            if match:
                logical_start = int(match.group(1))
                logical_end = int(match.group(2))
                physical_start = int(match.group(3))
                physical_end = int(match.group(4))
                length = int(match.group(5))

                result["extents"].append({
                    "logical_start": logical_start,
                    "logical_end": logical_end,
                    "physical_start": physical_start,
                    "physical_end": physical_end,
                    "length": length
                })

        result["total_extents"] = len(result["extents"])

    except Exception as e:
        raise RuntimeError(f"Erreur analyse physique : {e}")

    return result