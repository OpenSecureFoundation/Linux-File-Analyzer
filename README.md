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

## *************************************************************************************************

# Description

**File Analyzer** est un outil graphique conçu pour analyser en profondeur les fichiers stockés sur une partition **EXT4** sous **Debian**. Il offre une interface unifiée permettant d'explorer :

- Le **type de fichier** (magic number, en-tête)
- Les **métadonnées système** (inode, permissions, dates)
- L'**organisation physique** (extents, blocs)
- Le **taux de fragmentation**
- Le **contenu** (texte, hexadécimal, informations spécifiques) 


# Installation

## Prérequis
1. Système : Debian 13.1.0 (Trixie) ou supérieur
2. Python : 3.9 ou supérieur
3. Partition : EXT4

## Méthode 1 : Installation rapide (package .deb)

### Télécharger la dernière version
wget https://github.com/OpenSecureFoundation/Linux-File-Analyzer/raw/main/linux-file-analyzer-1.0.0.deb

### Installer le package
sudo apt install ./linux-file-analyzer-1.0.0.deb

## Méthode 2 : Installation depuis les sources

## Cloner le dépôt
git clone https://github.com/OpenSecureFoundation/Linux-File-Analyzer.git

cd Linux-File-Analyzer

## Installer les dépendances système
sudo apt update
sudo apt install -y python3 python3-tk python3-pip python3-matplotlib \
                    python3-reportlab python3-pil file e2fsprogs

## Installer les dépendances Python
pip install -r requirements.txt

## Lancer l'application
python3 src/main.py

## Utilisation

## Lancement normal (analyse basique)
file-analyzer

## Lancement avec droits root (analyse complète des extents)
sudo file-analyzer