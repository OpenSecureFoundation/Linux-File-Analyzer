# src/main.py

import sys
from FileAnalyzer.logger import get_logger
from FileAnalyzer.analyzer import analyze

logger = get_logger(__name__)

def print_section(title):
    print("\n" + "=" * 60)
    print(title.upper())
    print("=" * 60)

def main():
    if len(sys.argv) != 2:
        print("Usage : sudo python3 main.py <chemin_fichier>")
        sys.exit(1)

    file_path = sys.argv[1]

    print_section("DÉMARRAGE FILE ANALYZER")

    result = analyze(file_path)

    print_section("RÉSULTAT GLOBAL")
    print(f"Fichier analysé : {result['file']}")
    print(f"Statut          : {result['status']}")

    if result["errors"]:
        print_section("ERREURS / AVERTISSEMENTS")
        for err in result["errors"]:
            print(f"- {err}")

    print_section("TYPE DE FICHIER")
    print(result["type_analysis"])

    print_section("MÉTADONNÉES")
    print(result["metadata"])

    print_section("ORGANISATION PHYSIQUE")
    print(result["physical_layout"])

    print_section("FRAGMENTATION")
    print(result["fragmentation"])

    print_section("CONTENU (APERÇU)")
    content = result["content"]
    if content:
        print(content.get("preview", "Non disponible"))
    else:
        print("Aucun contenu affichable")

    print("\nAnalyse terminée.")

if __name__ == "__main__":
    main()
