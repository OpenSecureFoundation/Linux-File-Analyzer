import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from FileAnalyzer.analyzer import analyze
import os
import subprocess
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ==========================
# INFO-BULLE POUR TERMES TECHNIQUES
# ==========================
class ToolTip:
    """Classe pour afficher une info-bulle sur un widget Tkinter."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("Arial", 10))
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


# ==========================
# CLASSE PRINCIPALE GUI
# ==========================
class FileAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux File Analyzer - EXT4")
        self.root.geometry("1250x800")

        # Menu principal
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouvelle analyse", command=self.new_analysis)
        file_menu.add_command(label="Exporter rapport", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_app)

        # Menu Affichage
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Affichage", menu=view_menu)
        view_menu.add_command(label="Mode clair", command=lambda: self.change_theme("clair"))
        view_menu.add_command(label="Mode sombre", command=lambda: self.change_theme("sombre"))

        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Aide générale", command=lambda: self.show_help_window(None))
        help_menu.add_command(label="À propos", command=self.show_about)

        # Menu Paramètres
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Paramètres", menu=settings_menu)
        settings_menu.add_command(label="Configurer l'analyse", command=self.open_settings_window)

        # Icône
        try:
            self.root.iconphoto(False, tk.PhotoImage(file="icon.png"))
        except:
            pass

        self.file_path = tk.StringVar()
        self.last_result = None
        self.fs_label = None
        self.settings_file = "settings.json"

        self.tab_key_mapping = {
            "Résumé": "summary",
            "Métadonnées": "metadata",
            "Organisation physique": "physical_layout",
            "Fragmentation": "fragmentation",
            "Carte physique": "physical_layout",
            "Contenu": "content",
        }

        self.create_widgets()
        self.apply_styles()
        self.load_settings()

    # ==========================
    # CHARGEMENT DES PARAMÈTRES
    # ==========================
    def load_settings(self):
        """Charge les paramètres depuis settings.json"""
        default_settings = {"max_display_size_mb": 50, "show_hex": True, "check_updates": True}
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                self.settings = json.load(f)
        else:
            self.settings = default_settings
            with open(self.settings_file, "w") as f:
                json.dump(default_settings, f, indent=4)

    # ==========================
    # STYLES ET COULEURS
    # ==========================
    def apply_styles(self):
        """Appliquer des couleurs à l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs personnalisées
        style.configure('TButton', padding=6, relief="flat", background="#3498db", foreground="white")
        style.map('TButton',
                  background=[('active', '#2980b9'), ('disabled', '#cccccc')],
                  foreground=[('disabled', '#888888')])
        
        style.configure('Success.TButton', background="#2ecc71")
        style.map('Success.TButton', background=[('active', '#27ae60')])
        
        style.configure('Warning.TButton', background="#f39c12")
        style.map('Warning.TButton', background=[('active', '#e67e22')])
        
        # Couleurs des onglets
        style.configure('TNotebook.Tab', padding=[10, 2], font=('Arial', 10))
        style.map('TNotebook.Tab',
                  background=[('selected', '#3498db'), ('active', '#2980b9')],
                  foreground=[('selected', 'white'), ('active', 'white')])
        
        # Labels
        style.configure('TLabel', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Entry
        style.configure('TEntry', fieldbackground='white')
        
        # Couleurs pour les tags du texte
        for tab_info in self.tabs.values():
            widget = tab_info["widget"]
            widget.tag_configure("section", foreground="#2c3e50", font=("Arial", 11, "bold"))
            widget.tag_configure("success", foreground="#27ae60")
            widget.tag_configure("warning", foreground="#f39c12")
            widget.tag_configure("error", foreground="#e74c3c")
            widget.tag_configure("info", foreground="#3498db")
            widget.tag_configure("orange", foreground="#e67e22")

    def change_theme(self, theme):
        """Changer le thème de l'application"""
        if theme == "sombre":
            bg_color = "#2c3e50"
            fg_color = "white"
        else:
            bg_color = "white"
            fg_color = "black"
        
        self.root.configure(bg=bg_color)
        # À compléter pour un changement complet de thème

    # ==========================
    # CREATION INTERFACE
    # ==========================
    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Fichier:", style='Header.TLabel').pack(side="left", padx=5)
        ttk.Entry(top_frame, textvariable=self.file_path, width=70).pack(side="left", padx=5)
        ttk.Button(top_frame, text="📂 Parcourir", command=self.browse_file).pack(side="left", padx=5)
        
        self.analyze_button = ttk.Button(top_frame, text="🔍 Analyser", command=self.run_analysis, state="disabled")
        self.analyze_button.pack(side="left", padx=5)
        
        ttk.Button(top_frame, text="📊 Exporter", command=self.export_report).pack(side="left", padx=5)
        
        # Bouton Fermer
        ttk.Button(top_frame, text="❌ Fermer", command=self.quit_app).pack(side="left", padx=20)

        self.fs_label = ttk.Label(top_frame, text="💾 Système : Non détecté")
        self.fs_label.pack(side="left", padx=10)

        # Bouton Nouvelle analyse (au départ caché)
        self.new_analysis_button = ttk.Button(top_frame, text="🔄 Nouvelle analyse", 
                                             command=self.new_analysis, style='Success.TButton')
        # Ne pas pack au départ, il sera affiché après analyse

        # Barre de progression
        self.progress = ttk.Progressbar(self.root, mode='indeterminate', style="green.Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=10, pady=5)

        # Onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabs = {}

        for name in self.tab_key_mapping.keys():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)

            # Text widget - RENDU NON MODIFIABLE
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill="both", expand=True)
            text_widget = tk.Text(text_frame, wrap="word", font=("Consolas", 10))
            text_widget.config(state="disabled")  # ← DÉSACTIVÉ PAR DÉFAUT
            scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Boutons de vue
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill="x", pady=2)
            
            text_btn = ttk.Button(btn_frame, text="📝 Texte", 
                                 command=lambda t=name: self.change_view(t, "texte"))
            table_btn = ttk.Button(btn_frame, text="📊 Tableau", 
                                  command=lambda t=name: self.change_view(t, "tableau"))
            graph_btn = ttk.Button(btn_frame, text="📈 Graphique", 
                                  command=lambda t=name: self.change_view(t, "graphique"))
            
            text_btn.pack(side="left", padx=2)
            table_btn.pack(side="left", padx=2)
            graph_btn.pack(side="left", padx=2)

            # Bouton aide
            help_btn = ttk.Button(btn_frame, text="❓", width=3, 
                                 command=lambda n=name: self.show_help_window(n))
            help_btn.pack(side="left", padx=5)

            # Tooltips CU6
            ToolTip(text_widget, "extent : Portion contiguë d'un fichier sur le disque")
            ToolTip(text_widget, "inode : Structure contenant les métadonnées d'un fichier")
            ToolTip(text_widget, "fragmentation : Découpage d'un fichier sur plusieurs blocs non contigus")

            self.tabs[name] = {
                "widget": text_widget,
                "buttons": {"texte": text_btn, "tableau": table_btn, "graphique": graph_btn},
                "frame": frame,
                "text_frame": text_frame
            }

    # ==========================
    # AIDE CONTEXTUELLE CU6 (AMÉLIORÉE)
    # ==========================
    def show_help_window(self, term=None):
        """CU6: Afficher l'aide contextuelle ou générale"""
        help_win = tk.Toplevel(self.root)
        help_win.title("Aide - Linux File Analyzer")
        help_win.geometry("600x500")
        
        # Notebook pour organiser l'aide
        help_notebook = ttk.Notebook(help_win)
        help_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ===== Onglet Général =====
        general_frame = ttk.Frame(help_notebook)
        help_notebook.add(general_frame, text="Général")
        
        general_text = tk.Text(general_frame, wrap="word", font=("Arial", 10))
        general_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        general_content = """
UTILISATION DE L'OUTIL
======================
1. Cliquez sur "Parcourir" pour sélectionner un fichier
2. Cliquez sur "Analyser" pour lancer l'analyse
3. Naviguez entre les onglets pour voir les résultats
4. Changez de vue (Texte/Tableau/Graphique) avec les boutons
5. Exportez le rapport en PDF ou TXT

FONCTIONNALITÉS
--------------
• Détection automatique du type de fichier
• Extraction des métadonnées (inode, permissions, dates)
• Analyse de l'organisation physique (extents)
• Calcul du taux de fragmentation
• Visualisation graphique de la carte des blocs
        """
        general_text.insert("1.0", general_content)
        general_text.config(state="disabled")
        
        # ===== Onglet Termes techniques =====
        terms_frame = ttk.Frame(help_notebook)
        help_notebook.add(terms_frame, text="Termes techniques")
        
        terms_text = tk.Text(terms_frame, wrap="word", font=("Arial", 10))
        terms_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        terms_content = """
GLOSSAIRE TECHNIQUE
===================

EXTENT
------
Portion contiguë de blocs physiques allouée à un fichier.
Un fichier peut être composé d'un ou plusieurs extents.
• 1 extent = fichier contigu (non fragmenté)
• Plusieurs extents = fichier fragmenté

INODE
-----
Structure de données contenant les métadonnées d'un fichier :
• Permissions (rwxr-xr-x)
• Propriétaire et groupe
• Taille
• Dates (atime, mtime, ctime)
• Pointeurs vers les blocs de données

FRAGMENTATION
-------------
État d'un fichier dont les blocs sont dispersés sur le disque.
• Faible : 1-2 extents
• Modéré : 3-5 extents
• Élevé : >5 extents

BLOC
----
Unité minimale de stockage sur le disque (généralement 4Ko sous EXT4)

SUPERBLOCK
----------
Structure contenant les informations globales du système de fichiers
        """
        terms_text.insert("1.0", terms_content)
        terms_text.config(state="disabled")
        
        # ===== Onglet Formats supportés =====
        formats_frame = ttk.Frame(help_notebook)
        help_notebook.add(formats_frame, text="Formats")
        
        formats_text = tk.Text(formats_frame, wrap="word", font=("Arial", 10))
        formats_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        formats_content = """
TYPES DE FICHIERS ANALYSABLES
=============================

📄 TEXTE
  • .txt, .py, .c, .html, .xml, .json, .csv
  • Affichage direct du contenu

🖼️ IMAGES
  • .png, .jpg, .gif, .bmp
  • Affichage des métadonnées EXIF

📑 DOCUMENTS
  • .pdf, .docx, .odt
  • Analyse de l'en-tête et métadonnées

💾 BINAIRES
  • .exe, .bin, .so, .dll, .deb, .rpm
  • Analyse des structures internes sans affichage du contenu brut

🔧 SYSTÈME
  • Fichiers EXT4, périphériques
  • Accès root requis pour les structures bas niveau
        """
        formats_text.insert("1.0", formats_content)
        formats_text.config(state="disabled")
        
        # Bouton fermer
        ttk.Button(help_win, text="Fermer", command=help_win.destroy).pack(pady=5)

    def show_about(self):
        """Afficher la boîte de dialogue À propos"""
        about_text = """
Linux File Analyzer v1.0
Analyseur avancé de fichiers EXT4

Développé par: SONGMENE LADO Belviane
Sous la direction de: M. NGUIMBUS Emmanuel

Université de Yaoundé 1
Année académique: 2025-2026

Fonctionnalités:
• Analyse approfondie des fichiers EXT4
• Visualisation des métadonnées et extents
• Calcul de fragmentation
• Interface graphique intuitive
        """
        messagebox.showinfo("À propos", about_text)

    # ==========================
    # PARAMÈTRES CU7
    # ==========================
    def open_settings_window(self):
        win = tk.Toplevel(self.root)
        win.title("Paramètres d'analyse")
        win.geometry("400x300")
        win.resizable(False, False)

        # Charger les paramètres actuels
        settings = self.settings.copy()

        # Frame principal
        main_frame = ttk.Frame(win, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Taille max d'affichage
        ttk.Label(main_frame, text="Taille max d'affichage (Mo):").grid(row=0, column=0, sticky="w", pady=5)
        max_display_var = tk.StringVar(value=str(settings.get("max_display_size_mb", 50)))
        ttk.Entry(main_frame, textvariable=max_display_var, width=10).grid(row=0, column=1, sticky="w", pady=5)

        # Options
        show_hex_var = tk.BooleanVar(value=settings.get("show_hex", True))
        ttk.Checkbutton(main_frame, text="Toujours afficher l'hexadécimal", 
                       variable=show_hex_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        check_updates_var = tk.BooleanVar(value=settings.get("check_updates", True))
        ttk.Checkbutton(main_frame, text="Vérifier les mises à jour au démarrage", 
                       variable=check_updates_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # Séparateur
        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        def apply_settings():
            try:
                max_size = int(max_display_var.get())
                if max_size <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erreur", "Taille max d'affichage invalide (>0 requis)")
                return

            new_settings = {
                "max_display_size_mb": max_size,
                "show_hex": show_hex_var.get(),
                "check_updates": check_updates_var.get()
            }

            with open(self.settings_file, "w") as f:
                json.dump(new_settings, f, indent=4)

            self.settings = new_settings
            messagebox.showinfo("Paramètres", "Paramètres sauvegardés avec succès.")
            win.destroy()

        def reset_settings():
            default = {"max_display_size_mb": 50, "show_hex": True, "check_updates": True}
            max_display_var.set(str(default["max_display_size_mb"]))
            show_hex_var.set(default["show_hex"])
            check_updates_var.set(default["check_updates"])

        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Appliquer", command=apply_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Réinitialiser", command=reset_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annuler", command=win.destroy).pack(side="left", padx=5)

    # ==========================
    # VÉRIFICATION FS
    # ==========================
    def is_ext4(self, path):
        try:
            result = subprocess.run(["df", "-T", path], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            if len(lines) >= 2:
                fs_type = lines[1].split()[1]
                self.fs_label.config(text=f"💾 Système : {fs_type}")
                return fs_type.lower() == "ext4"
            return False
        except:
            return False

    # ==========================
    # BROWSE FILE
    # ==========================
    def browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            if not os.access(path, os.R_OK):
                messagebox.showerror("Erreur", "Permission refusée.")
                return
            if not self.is_ext4(path):
                messagebox.showerror("Erreur", "Le fichier doit être sur une partition EXT4.")
                return
            self.file_path.set(path)
            self.analyze_button.config(state="normal")

    # ==========================
    # ANALYSE
    # ==========================
    def run_analysis(self):
        path = self.file_path.get()
        if not path:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier.")
            return

        # Démarrer la progression
        self.progress.start()
        self.analyze_button.config(state="disabled")
        self.root.update_idletasks()

        try:
            self.last_result = analyze(path)
            
            # Vérifier si l'analyse a réussi
            if self.last_result and self.last_result.get("status") == "ERROR":
                error_msg = self.last_result.get("error", "Erreur inconnue")
                messagebox.showerror("Erreur d'analyse", 
                                    f"Impossible d'analyser ce fichier.\n\nRaison: {error_msg}\n\n"
                                    "Ce type de fichier peut ne pas être supporté ou être corrompu.")
                self.progress.stop()
                self.analyze_button.config(state="normal")
                return
            
            self.display_results()

            # Afficher le bouton "Nouvelle analyse"
            self.new_analysis_button.pack(side="left", padx=5)

            # Arrêter la progression
            self.progress.stop()

        except Exception as e:
            self.progress.stop()
            self.analyze_button.config(state="normal")
            messagebox.showerror("Erreur Analyse", 
                               f"Une erreur est survenue lors de l'analyse:\n{str(e)}\n\n"
                               "Vérifiez que le fichier est accessible et non corrompu.")

    # Fonction Nouvelle analyse
    def new_analysis(self):
        if self.last_result:
            resp = messagebox.askyesno(
                "Nouvelle analyse",
                "Les résultats actuels ne sont pas sauvegardés. Continuer ?"
            )
            if not resp:
                return

        # Réinitialisation
        self.file_path.set("")
        self.analyze_button.config(state="disabled")
        self.last_result = None

        for tab_info in self.tabs.values():
            widget = tab_info["widget"]
            widget.config(state="normal")
            widget.delete("1.0", tk.END)
            widget.config(state="disabled")  # ← Remettre en disabled après effacement
            # Réactiver tous les boutons de vue
            for btn in tab_info["buttons"].values():
                btn.config(state="normal")

        # Cacher le bouton jusqu'à la prochaine analyse
        self.new_analysis_button.pack_forget()

    # ==========================
    # DISPLAY RESULTS
    # ==========================
    def display_results(self):
        if not self.last_result:
            return

        def format_data(widget, data, indent=0):
            space = "  " * indent
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, (dict, list)):
                        widget.insert(tk.END, f"{space}{k} :\n", "section")
                        format_data(widget, v, indent + 1)
                    else:
                        widget.insert(tk.END, f"{space}{k} : {v}\n")
            elif isinstance(data, list):
                for i, item in enumerate(data, 1):
                    if isinstance(item, (dict, list)):
                        widget.insert(tk.END, f"{space}- Élément {i} :\n", "section")
                        format_data(widget, item, indent + 1)
                    else:
                        widget.insert(tk.END, f"{space}- {item}\n")
            else:
                widget.insert(tk.END, f"{space}{data}\n")

        for tab_name, tab_info in self.tabs.items():
            widget = tab_info["widget"]
               
            # Activer temporairement pour écrire
            widget.config(state="normal")
            widget.delete("1.0", tk.END)
            
            key = self.tab_key_mapping[tab_name]

            if tab_name == "Résumé":
                widget.insert(tk.END, f"📁 Fichier : ", "section")
                widget.insert(tk.END, f"{self.last_result.get('file', 'Non disponible')}\n\n")
                
                status = self.last_result.get("status", "UNKNOWN")
                widget.insert(tk.END, f"📊 Statut : ", "section")
                
                if status == "SUCCESS":
                    widget.insert(tk.END, f"{status}\n", "success")
                elif status == "PARTIAL_SUCCESS":
                    widget.insert(tk.END, f"{status} (Analyse partielle)\n", "warning")
                else:
                    widget.insert(tk.END, f"{status}\n", "error")
                
                widget.insert(tk.END, f"\n📋 Informations générales:\n", "section")
                    
                # Type de fichier
                file_type = self.last_result.get("file_type", "Inconnu")
                widget.insert(tk.END, f"Type: {file_type}\n")
                
                # Taille logique (taille réelle du fichier)
                file_size = self.last_result.get("file_size", 0)
                widget.insert(tk.END, f"Taille logique: {file_size} octets")
                
                if file_size > 1024*1024:
                    widget.insert(tk.END, f" ({file_size/(1024*1024):.2f} Mo)\n")
                elif file_size > 1024:
                    widget.insert(tk.END, f" ({file_size/1024:.2f} Ko)\n")
                else:
                    widget.insert(tk.END, "\n")
                
                # Taille sur disque depuis les métadonnées
                metadata = self.last_result.get("metadata", {})
                
                # Avec votre nouveau metadata.py, les clés sont en anglais
                disk_size_bytes = metadata.get("disk_size_bytes", 0)
                
                if disk_size_bytes > 0:
                    widget.insert(tk.END, f"Taille sur disque: {disk_size_bytes} octets")
                    
                    if disk_size_bytes > 1024*1024:
                        widget.insert(tk.END, f" ({disk_size_bytes/(1024*1024):.2f} Mo)")
                    elif disk_size_bytes > 1024:
                        widget.insert(tk.END, f" ({disk_size_bytes/1024:.2f} Ko)")
                    
                    # Calcul de l'espace perdu (fragmentation interne)
                    if file_size > 0:
                        waste = disk_size_bytes - file_size
                        waste_percent = (waste / file_size) * 100
                        widget.insert(tk.END, f"\nEspace perdu: {waste} octets ({waste_percent:.2f}%)")
                    widget.insert(tk.END, "\n")
                
                # Afficher les métadonnées clés
                if metadata:
                    widget.insert(tk.END, f"\n📦 Métadonnées système:\n", "section")
                    
                    # Mapping des clés anglais -> français pour l'affichage
                    display_keys = {
                        "permissions": "Permissions",
                        "owner": "Propriétaire",
                        "group": "Groupe",
                        "links": "Liens physiques",
                        "inode": "Inode",
                        "blocks_allocated": "Blocs alloués (4K)",
                        "waste_percent": "Fragmentation interne"
                    }
                        
                    for eng_key, fr_key in display_keys.items():
                        if eng_key in metadata:
                            value = metadata[eng_key]
                            if eng_key == "waste_percent":
                                widget.insert(tk.END, f"{fr_key}: {value}%\n")
                            else:
                                widget.insert(tk.END, f"{fr_key}: {value}\n")
                    
                    # Afficher les timestamps
                    if "timestamps" in metadata:
                        ts = metadata["timestamps"]
                        widget.insert(tk.END, f"\n🕒 Horodatages:\n", "section")
                        widget.insert(tk.END, f"Accès: {ts['atime'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                        widget.insert(tk.END, f"Modif: {ts['mtime'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                        widget.insert(tk.END, f"Change: {ts['ctime'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                        if ts.get('btime'):
                            widget.insert(tk.END, f"Création: {ts['btime'].strftime('%Y-%m-%d %H:%M:%S')}\n")

            elif tab_name == "Métadonnées":
                metadata = self.last_result.get(key, {})
                if metadata:
                    # Afficher toutes les métadonnées
                    for k, v in metadata.items():
                        if k == "timestamps":
                            widget.insert(tk.END, f"📅 Horodatages:\n", "section")
                            for ts_name, ts_value in v.items():
                                if ts_value:
                                    widget.insert(tk.END, f"  {ts_name}: {ts_value.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        elif k == "flags" and v:
                            widget.insert(tk.END, f"🏷️ Flags: {', '.join(v)}\n")
                        else:
                            # Formater les clés
                            key_display = k.replace('_', ' ').title()
                            value = v
                            
                            # Formater certaines valeurs spéciales
                            if k == "size_bytes" or k == "disk_size_bytes":
                                if value > 1024*1024*1024:
                                    value = f"{value} ({value/(1024*1024*1024):.2f} Go)"
                                elif value > 1024*1024:
                                    value = f"{value} ({value/(1024*1024):.2f} Mo)"
                                elif value > 1024:
                                    value = f"{value} ({value/1024:.2f} Ko)"
                            
                            widget.insert(tk.END, f"{key_display}: {value}\n")
                else:
                    widget.insert(tk.END, "Aucune métadonnée disponible\n")

            elif tab_name == "Contenu":
                # Onglet Contenu - AFFICHAGE DU CONTENU RÉEL
                content_data = self.last_result.get(key, {})
                
                if isinstance(content_data, dict):
                    is_binary = content_data.get("is_binary", True)
                    file_type = content_data.get("file_type", "inconnu")
                    preview = content_data.get("preview", "")
                    hex_dump = content_data.get("hex_dump", "")
                    metadata_dict = content_data.get("metadata", {})
                    
                    # En-tête
                    widget.insert(tk.END, f"📄 CONTENU DU FICHIER\n", "section")
                    widget.insert(tk.END, "=" * 50 + "\n\n")
                    
                    if not is_binary:
                        # Fichier texte - afficher le contenu
                        widget.insert(tk.END, "📝 APERÇU TEXTE:\n", "info")
                        widget.insert(tk.END, "-" * 30 + "\n")
                        if preview:
                            widget.insert(tk.END, preview)
                        else:
                            widget.insert(tk.END, "(Fichier vide)\n")
                    
                    elif file_type and "PDF" in file_type:
                        # Fichier PDF - afficher les métadonnées
                        widget.insert(tk.END, "📑 DOCUMENT PDF\n", "info")
                        widget.insert(tk.END, "-" * 30 + "\n")
                        
                        if metadata_dict:
                            for k, v in metadata_dict.items():
                                if v:  # N'afficher que les valeurs non vides
                                    widget.insert(tk.END, f"{k}: {v}\n")
                        
                        # Afficher aussi un hex dump partiel
                        if hex_dump:
                            widget.insert(tk.END, "\n🔍 APERÇU HEXADÉCIMAL:\n", "info")
                            widget.insert(tk.END, "-" * 30 + "\n")
                            widget.insert(tk.END, hex_dump)
                    
                    elif file_type and any(ext in file_type.lower() for ext in ['jpg', 'png', 'gif', 'image']):
                        # Fichier image
                        widget.insert(tk.END, "🖼️ FICHIER IMAGE\n", "info")
                        widget.insert(tk.END, "-" * 30 + "\n")
                        widget.insert(tk.END, f"Format: {file_type}\n")
                        
                        if metadata_dict:
                            for k, v in metadata_dict.items():
                                widget.insert(tk.END, f"{k}: {v}\n")
                    
                    elif file_type and "DEB" in file_type.upper():
                        # Fichier Debian package
                        widget.insert(tk.END, "📦 PACKAGE DEBIAN\n", "info")
                        widget.insert(tk.END, "-" * 30 + "\n")
                        
                        if metadata_dict:
                            for k, v in metadata_dict.items():
                                widget.insert(tk.END, f"{k}: {v}\n")
                        
                        widget.insert(tk.END, "\n📋 INSTRUCTIONS:\n", "section")
                        widget.insert(tk.END, "Pour extraire ce package:\n")
                        widget.insert(tk.END, "$ dpkg-deb -x <fichier.deb> <dossier>\n")
                        widget.insert(tk.END, "\nPour voir le contenu:\n")
                        widget.insert(tk.END, "$ dpkg-deb -c <fichier.deb>\n")
                    
                    else:
                        # Autres fichiers binaires
                        widget.insert(tk.END, "🔒 FICHIER BINAIRE\n", "info")
                        widget.insert(tk.END, "-" * 30 + "\n")
                        widget.insert(tk.END, f"Type: {file_type}\n")
                        widget.insert(tk.END, f"Taille: {content_data.get('file_size', 0)} octets\n")
                        
                        if hex_dump:
                            widget.insert(tk.END, "\n🔍 APERÇU HEXADÉCIMAL:\n", "info")
                            widget.insert(tk.END, "-" * 30 + "\n")
                            widget.insert(tk.END, hex_dump)
                        
                        if metadata_dict:
                            widget.insert(tk.END, "\n📊 INFORMATIONS:\n", "info")
                            for k, v in metadata_dict.items():
                                widget.insert(tk.END, f"{k}: {v}\n")
                    
                    # Afficher les erreurs s'il y en a
                    if "error" in content_data:
                        widget.insert(tk.END, f"\n⚠️ Erreur: {content_data['error']}\n", "error")
                        
                else:
                    widget.insert(tk.END, "Aucune donnée de contenu disponible\n")

            elif tab_name == "Fragmentation":
                self.display_fragmentation(widget, self.last_result.get(key, {}))

            else:
                data = self.last_result.get(key)
                if not data:
                    widget.insert(tk.END, "Aucune donnée disponible\n")
                else:
                    format_data(widget, data)

            # Désactiver après écriture
            widget.config(state="disabled")

            # Activer/désactiver les boutons de vue selon l'onglet
            for view, btn in tab_info["buttons"].items():
                if tab_name in ["Résumé", "Contenu"] and view != "texte":
                    btn.config(state="disabled")
                else:
                    btn.config(state="normal")
            
    def display_fragmentation(self, widget, data):
        """Afficher la fragmentation avec des couleurs"""
        if not data:
            widget.insert(tk.END, "Aucune donnée de fragmentation\n")
            return

        rate = data.get("rate", 0)
        level = data.get("level", "inconnu")
        extents = data.get("extent_count", 0)

        # Choix de la couleur selon le niveau
        if level == "faible":
            color = "success"
            icon = "✅"
        elif level == "modéré":
            color = "warning"
            icon = "⚠️"
        elif level == "élevé":
            color = "error"
            icon = "❌"
        else:
            color = "info"
            icon = "❓"

        widget.insert(tk.END, f"{icon} Taux de fragmentation: ", "section")
        widget.insert(tk.END, f"{rate}%\n", color)

        widget.insert(tk.END, f"📊 Niveau: ", "section")
        widget.insert(tk.END, f"{level.upper()}\n", color)

        widget.insert(tk.END, f"📦 Nombre d'extents: ", "section")
        widget.insert(tk.END, f"{extents}\n\n")

        # Interprétation
        widget.insert(tk.END, "🔍 INTERPRÉTATION:\n", "section")
        if extents == 1:
            widget.insert(tk.END, "• Fichier parfaitement contigu\n", "success")
            widget.insert(tk.END, "• Aucune fragmentation détectée\n", "success")
            widget.insert(tk.END, "• Performance de lecture optimale\n", "success")
        elif extents <= 3:
            widget.insert(tk.END, "• Fragmentation légère\n", "warning")
            widget.insert(tk.END, "• Impact négligeable sur les performances\n", "warning")
        elif extents <= 6:
            widget.insert(tk.END, "• Fragmentation modérée\n", "orange")
            widget.insert(tk.END, "• Impact possible sur les temps d'accès\n", "orange")
        else:
            widget.insert(tk.END, "• Forte fragmentation\n", "error")
            widget.insert(tk.END, "• Recommandé: défragmenter le fichier\n", "error")
            widget.insert(tk.END, "• Performances de lecture dégradées\n", "error")

    # ==========================
    # CHANGER DE VUE (AMÉLIORÉ)
    # ==========================
    def change_view(self, tab_name, view_type):
        """CU5: Changer de vue d'affichage (texte, tableau, graphique)"""
        tab_info = self.tabs[tab_name]
        widget = tab_info["widget"]
        frame = tab_info["frame"]
        text_frame = tab_info["text_frame"]

        # Nettoyer l'ancien contenu
        for child in frame.winfo_children():
            if isinstance(child, (FigureCanvasTkAgg, ttk.Treeview, tk.Canvas)):
                child.destroy()
            elif child == text_frame:
                # Ne pas détruire text_frame, juste cacher ses enfants si nécessaire
                for subchild in text_frame.winfo_children():
                    if isinstance(subchild, (FigureCanvasTkAgg, ttk.Treeview)):
                        subchild.destroy()

        # Récupérer les données
        key = self.tab_key_mapping[tab_name]
        data = self.last_result.get(key) if self.last_result else None

        # ==========================
        # VUE TEXTE (pour tous les onglets)
        # ==========================
        if view_type == "texte":
            # Remontrer le text widget
            text_frame.pack(fill="both", expand=True)
            
            # Activer temporairement pour écrire
            widget.config(state="normal")
            widget.delete("1.0", tk.END)
            
            if not data:
                widget.insert(tk.END, "Aucune donnée disponible\n")
            elif isinstance(data, dict):
                for k, v in data.items():
                    widget.insert(tk.END, f"{k}: {v}\n")
            elif isinstance(data, list):
                for i, item in enumerate(data, 1):
                    widget.insert(tk.END, f"{i}. {item}\n")
            else:
                widget.insert(tk.END, str(data))
            
            # Désactiver après écriture
            widget.config(state="disabled")
            return

        # Cacher le text widget pour les autres vues
        text_frame.pack_forget()

        # ==========================
        # VUE TABLEAU (pour Onglet Métadonnées et Organisation)
        # ==========================
        if view_type == "tableau":
            if not data:
                # Afficher un message dans une étiquette
                msg_label = ttk.Label(frame, text="Aucune donnée pour affichage en tableau")
                msg_label.pack(pady=20)
                return

            # Créer un Treeview pour le tableau
            tree_frame = ttk.Frame(frame)
            tree_frame.pack(fill="both", expand=True)

            if tab_name == "Métadonnées" and isinstance(data, dict):
                # Tableau 2 colonnes : Propriété | Valeur
                tree = ttk.Treeview(tree_frame, columns=("Propriété", "Valeur"), 
                                   show="headings", height=20)
                tree.heading("Propriété", text="Propriété")
                tree.heading("Valeur", text="Valeur")
                tree.column("Propriété", width=200)
                tree.column("Valeur", width=300)

                for k, v in data.items():
                    tree.insert("", tk.END, values=(k, str(v)))

            elif tab_name == "Organisation physique" and isinstance(data, dict):
                extents = data.get("extents", [])
                if extents:
                    # Tableau des extents
                    tree = ttk.Treeview(tree_frame, 
                                       columns=("#", "Début logique", "Fin logique", "Longueur", "Blocs physiques"), 
                                       show="headings", height=20)
                    tree.heading("#", text="#")
                    tree.heading("Début logique", text="Début logique")
                    tree.heading("Fin logique", text="Fin logique")
                    tree.heading("Longueur", text="Longueur (blocs)")
                    tree.heading("Blocs physiques", text="Blocs physiques")

                    for i, extent in enumerate(extents, 1):
                        logical_start = extent.get("logical_offset", 0)
                        length = extent.get("length", 1)
                        physical_blocks = f"{extent.get('physical_start', 0)}-{extent.get('physical_end', 0)}"
                        
                        tree.insert("", tk.END, values=(
                            i,
                            logical_start,
                            logical_start + length,
                            length,
                            physical_blocks
                        ))
                else:
                    ttk.Label(tree_frame, text="Aucun extent trouvé").pack(pady=20)
                    return
            else:
                ttk.Label(tree_frame, text=f"Affichage tableau non disponible pour {tab_name}").pack(pady=20)
                return

            # Scrollbar pour le tableau
            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

            tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")

            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            return

        # ==========================
        # VUE GRAPHIQUE (CU9 - Carte physique)
        # ==========================
        if view_type == "graphique":
            if tab_name == "Carte physique" or tab_name == "Fragmentation":
                if not data:
                    ttk.Label(frame, text="Aucune donnée disponible").pack(pady=20)
                    return

                # Récupérer les extents
                if isinstance(data, dict):
                    extents = data.get("extents", [])
                else:
                    extents = data if isinstance(data, list) else []

                if not extents:
                    ttk.Label(frame, text="Aucun extent détecté - Fichier non fragmenté ?").pack(pady=20)
                    return

                # Créer le graphique
                fig, ax = plt.subplots(figsize=(10, 3))

                # Calculer la plage totale
                max_block = max(e.get("physical_end", 0) for e in extents) if extents else 0

                # Définir des couleurs pour les extents
                colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12', '#1abc9c']

                for i, extent in enumerate(extents):
                    start = extent.get("physical_start", 0)
                    length = extent.get("length", 1)
                    color = colors[i % len(colors)]

                    rect = Rectangle((start, 0), length, 1,
                                   facecolor=color,
                                   edgecolor='black',
                                   alpha=0.7)
                    ax.add_patch(rect)

                    # Ajouter le numéro d'extent
                    ax.text(start + length/2, 0.5, str(i+1),
                           ha='center', va='center', fontweight='bold')

                # Configuration des axes
                ax.set_xlim(0, max_block + 10)
                ax.set_ylim(0, 1)
                ax.set_title(f"Carte physique - {len(extents)} extent(s)")
                ax.set_xlabel("Numéro de bloc physique")
                ax.set_yticks([])

                # Ajouter une grille
                ax.grid(True, axis='x', alpha=0.3)

                # Intégration dans Tkinter
                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

                # Indicateur de fragmentation
                info_frame = ttk.Frame(frame)
                info_frame.pack(fill="x", pady=5)

                if len(extents) == 1:
                    ttk.Label(info_frame, text="✓ Fichier contigu (non fragmenté)", 
                             foreground="green", font=("Arial", 10, "bold")).pack()
                else:
                    rate = self.last_result.get("fragmentation", {}).get("rate", 0)
                    ttk.Label(info_frame, text=f"⚠ Taux de fragmentation: {rate}%", 
                             foreground="orange", font=("Arial", 10, "bold")).pack()
            else:
                ttk.Label(frame, text=f"Vue graphique non disponible pour {tab_name}").pack(pady=20)

    # ==========================
    # EXPORT PDF / TXT
    # ==========================
    def export_report(self):
        if not self.last_result:
            messagebox.showwarning("Attention", "Aucune analyse disponible.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt"), ("HTML files", "*.html")]
        )
        if not file_path:
            return

        try:
            if file_path.endswith(".pdf"):
                doc = SimpleDocTemplate(file_path)
                elements = []
                styles = getSampleStyleSheet()
                style = styles["Normal"]

                elements.append(Paragraph("<b>Linux File Analyzer Report</b>", styles["Heading1"]))
                elements.append(Spacer(1, 0.3 * inch))

                for tab_name, tab_info in self.tabs.items():
                    # Activer temporairement pour récupérer le contenu
                    widget = tab_info["widget"]
                    widget.config(state="normal")
                    content = widget.get("1.0", tk.END)
                    widget.config(state="disabled")
                    
                    elements.append(Paragraph(f"<b>{tab_name}</b>", styles["Heading2"]))
                    elements.append(Spacer(1, 0.2 * inch))
                    elements.append(Paragraph(content.replace("\n", "<br/>"), style))
                    elements.append(Spacer(1, 0.4 * inch))

                doc.build(elements)

            elif file_path.endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("=" * 50 + "\n")
                    f.write("LINUX FILE ANALYZER REPORT\n")
                    f.write("=" * 50 + "\n\n")

                    for tab_name, tab_info in self.tabs.items():
                        widget = tab_info["widget"]
                        widget.config(state="normal")
                        content = widget.get("1.0", tk.END)
                        widget.config(state="disabled")
                        
                        f.write(f"\n{'=' * 30}\n")
                        f.write(f"{tab_name}\n")
                        f.write(f"{'=' * 30}\n")
                        f.write(content)
                        f.write("\n")

            elif file_path.endswith(".html"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Linux File Analyzer Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
        h2 { color: #3498db; margin-top: 30px; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; }
        .section { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Linux File Analyzer Report</h1>
""")

                    for tab_name, tab_info in self.tabs.items():
                        widget = tab_info["widget"]
                        widget.config(state="normal")
                        content = widget.get("1.0", tk.END)
                        widget.config(state="disabled")
                        
                        f.write(f"    <h2>{tab_name}</h2>\n")
                        f.write(f"    <pre>{content}</pre>\n")

                    f.write("</body>\n</html>")

            messagebox.showinfo("Succès", "Rapport exporté avec succès.")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ==========================
    # QUITTER
    # ==========================
    def quit_app(self):
        """Fermer l'application avec confirmation"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter File Analyzer ?"):
            self.root.quit()
            self.root.destroy()