# Conception et mise en œuvre de File Analyzer, un analyseur avancé de fichiers : cas de EXT4 sous Debian


## Conception et mise en œuvre de File Analyzer, un analyseur avancé de fichiers : cas de EXT4 sous Debian


# Objectifs:
Mettre en pratique les notions sur les systèmes de fichiers.

# Fonctionnalités attendues
1. Détecter le type du fichier analysé et afficher tous les champs du header.
2. Afficher les permissions, propriétaire/groupe, taille logique, taille sur disque, timestamps (atime/mtime/ctime/btime), nombre de liens, flags (immutable…).
3. Obtenir la liste des extents (offset logique, longueur, bloc(s) physique(s)).
4. Calculer le taux de fragmentation    
5. Afficher le contenu brut du fichier si ce n’est pas un binaire.

# NB: README à mettre à jour progressivement par l'équipe.


# L'objectif principal de notre projet est de faciliter la compréhension et l'analyse approfondie des systèmes de fichiers EXT4 en fournissant un outil unifié permettant d'explorer de manière claire et accessible la structure interne, les métadonnées et l'organisation physique des fichiers sous Debian.

