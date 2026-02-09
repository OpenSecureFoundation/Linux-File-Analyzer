# src/FileAnalyzer/analyzer.py

from FileAnalyzer.file_type import analyze_file_type
from FileAnalyzer.metadata import extract_metadata
from FileAnalyzer.physical_layout import analyze_physical_layout
from FileAnalyzer.fragmentation import compute_fragmentation
from FileAnalyzer.content_viewer import display_content
from FileAnalyzer.utils import check_root, is_ext4
from FileAnalyzer.logger import get_logger


logger = get_logger(__name__)

def analyze(file_path, options=None):
    if options is None:
        options = {}

    result = {
        "file": file_path,
        "status": "SUCCESS",
        "type_analysis": None,
        "metadata": None,
        "physical_layout": None,
        "fragmentation": None,
        "content": None,
        "errors": []
    }

    logger.info(f"Début analyse : {file_path}")

    # 1️⃣ Vérifications système
    if not check_root():
        error = "L'analyse nécessite des privilèges root"
        logger.error(error)
        result["status"] = "FAILED"
        result["errors"].append(error)
        return result

    if not is_ext4(file_path):
        error = "Le fichier n'est pas situé sur un système EXT4"
        logger.warning(error)
        result["errors"].append(error)

    # 2️⃣ Détection type
    try:
        result["type_analysis"] = analyze_file_type(file_path)
    except Exception as e:
        logger.error(f"Erreur détection type : {e}")
        result["errors"].append(str(e))

    # 3️⃣ Métadonnées
    try:
        result["metadata"] = extract_metadata(file_path)
    except Exception as e:
        logger.error(f"Erreur métadonnées : {e}")
        result["errors"].append(str(e))

    # 4️⃣ Organisation physique
    try:
        layout = analyze_physical_layout(file_path)
        result["physical_layout"] = layout
    except Exception as e:
        logger.error(f"Erreur organisation physique : {e}")
        result["errors"].append(str(e))
        layout = None

    # 5️⃣ Fragmentation
    try:
        if layout and "extents" in layout:
            result["fragmentation"] = compute_fragmentation(layout["extents"])
    except Exception as e:
        logger.error(f"Erreur fragmentation : {e}")
        result["errors"].append(str(e))

    # 6️⃣ Contenu
    try:
        is_binary = result["type_analysis"]["is_binary"]
        max_size = options.get("max_display_size", 1024 * 1024)
        result["content"] = display_content(file_path, is_binary, max_size)
    except Exception as e:
        logger.error(f"Erreur affichage contenu : {e}")
        result["errors"].append(str(e))

    if result["errors"]:
        result["status"] = "PARTIAL_SUCCESS"
        logger.warning("Analyse terminée avec erreurs")
    else:
        logger.info("Analyse terminée avec succès")

    return result
