# src/FileAnalyzer/fragmentation.py

def count_blocks(extents):
    """Compte le nombre total de blocs dans les extents"""
    return sum(extent.get("length", 0) for extent in extents)

def interpret_fragmentation(rate):
    """Interprète le taux de fragmentation"""
    if rate <= 5:
        return "faible"
    elif rate <= 20:
        return "modéré"
    else:
        return "élevé"

def compute_fragmentation(extents):
    """
    Calcule le taux de fragmentation d'un fichier
    Retourne un dictionnaire avec les clés attendues par la GUI
    """
    if not extents:
        return {
            "extent_count": 0,
            "block_count": 0,
            "rate": 0.0,           # ← IMPORTANT: la GUI cherche "rate"
            "level": "inconnu"
        }

    extent_count = len(extents)
    block_count = count_blocks(extents)

    if extent_count <= 1:
        rate = 0.0
    else:
        # Formule: (nombre d'extents - 1) / nombre total de blocs * 100
        rate = ((extent_count - 1) / block_count) * 100

    return {
        "extent_count": extent_count,
        "block_count": block_count,
        "rate": round(rate, 2),     # ← La GUI utilise "rate"
        "level": interpret_fragmentation(rate)
    }