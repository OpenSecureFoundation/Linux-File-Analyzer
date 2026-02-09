# src/FileAnalyzer/fragmentation.py

def count_blocks(extents):
    return sum(extent["length"] for extent in extents)

def interpret_fragmentation(rate):
    if rate <= 5:
        return "Faible"
    elif rate <= 20:
        return "Modéré"
    else:
        return "Élevé"

def compute_fragmentation(extents):
    if not extents:
        return {
            "extent_count": 0,
            "block_count": 0,
            "fragmentation_rate": 0.0,
            "level": "Inconnu"
        }

    extent_count = len(extents)
    block_count = count_blocks(extents)

    if extent_count <= 1:
        rate = 0.0
    else:
        rate = ((extent_count - 1) / block_count) * 100

    return {
        "extent_count": extent_count,
        "block_count": block_count,
        "fragmentation_rate": round(rate, 2),
        "level": interpret_fragmentation(rate)
    }
