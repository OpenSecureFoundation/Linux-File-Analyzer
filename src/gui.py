import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from FileAnalyzer.analyzer import analyze
import os
import subprocess
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

        self.tab_key_mapping = {
            "Résumé": None,
            "Métadonnées": "metadata",
            "Organisation physique": "physical_layout",
            "Fragmentation": "fragmentation",
            "Carte physique": "physical_layout",
            "Contenu": "content",
        }

        self.create_widgets()

    # ==========================
    # CREATION INTERFACE
    # ==========================
    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")

        ttk.Entry(top_frame, textvariable=self.file_path, width=70).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Parcourir", command=self.browse_file).pack(side="left", padx=5)
        self.analyze_button = ttk.Button(top_frame, text="Analyser", command=self.run_analysis, state="disabled")
        self.analyze_button.pack(side="left", padx=5)
        ttk.Button(top_frame, text="Exporter rapport", command=self.export_report).pack(side="left", padx=5)

        self.fs_label = ttk.Label(top_frame, text="Système de fichier : Non détecté")
        self.fs_label.pack(side="left", padx=10)

        # Bouton Nouvelle analyse (au départ caché)
        self.new_analysis_button = ttk.Button(top_frame, text="Nouvelle analyse", command=self.new_analysis)
        # Ne pas pack au départ, il sera affiché après analyse

        # Onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabs = {}

        for name in self.tab_key_mapping.keys():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)

            # Text widget
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill="both", expand=True)
            text_widget = tk.Text(text_frame, wrap="word")
            scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            text_widget.tag_configure("section", font=("Arial", 11, "bold"))
            text_widget.tag_configure("success", foreground="green")
            text_widget.tag_configure("failed", foreground="red")

            # Boutons de vue
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill="x", pady=2)
            text_btn = ttk.Button(btn_frame, text="Texte", command=lambda t=name: self.change_view(t, "texte"))
            table_btn = ttk.Button(btn_frame, text="Tableau", command=lambda t=name: self.change_view(t, "tableau"))
            graph_btn = ttk.Button(btn_frame, text="Graphique", command=lambda t=name: self.change_view(t, "graphique"))
            text_btn.pack(side="left", padx=2)
            table_btn.pack(side="left", padx=2)
            graph_btn.pack(side="left", padx=2)

            # Bouton aide
            help_btn = ttk.Button(frame, text="Aide", width=5, command=lambda n=name: self.show_help_window(n))
            help_btn.pack(side="left", padx=5)

            # Tooltips CU6
            ToolTip(text_widget, "extent : Portion contiguë d'un fichier sur le disque")
            ToolTip(text_widget, "inode : Structure contenant les métadonnées d'un fichier")
            ToolTip(text_widget, "fragmentation : Découpage d'un fichier sur plusieurs blocs non contigus")

            self.tabs[name] = {
                "widget": text_widget,
                "buttons": {"texte": text_btn, "tableau": table_btn, "graphique": graph_btn},
                "frame": text_frame
            }

    # ==========================
    # AIDE CONTEXTUELLE CU6
    # ==========================
    def show_help_window(self, term):
        help_texts = {
            "extent": "Extent : Portion contiguë d'un fichier sur le disque.",
            "fragmentation": "Fragmentation : Découpage d'un fichier sur plusieurs blocs non contigus.",
            "inode": "Inode : Structure contenant les métadonnées d'un fichier.",
            "block": "Bloc : Unité de stockage physique sur le disque.",
        }
        text = help_texts.get(term.lower(), "Documentation non disponible.")
        help_win = tk.Toplevel(self.root)
        help_win.title(f"Aide : {term}")
        help_win.geometry("400x400")
        label = tk.Label(help_win, text=text, wraplength=380, justify="left", font=("Arial", 11))
        label.pack(padx=10, pady=10, fill="both", expand=True)
        ttk.Button(help_win, text="Fermer", command=help_win.destroy).pack(pady=5)

    # ==========================
    # PARAMÈTRES CU7
    # ==========================
    def open_settings_window(self):
        import json
        self.settings_file = "settings.json"
        default_settings = {"max_display_size_mb": 50, "show_hex": True, "check_updates": True}
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                settings = json.load(f)
        else:
            settings = default_settings

        win = tk.Toplevel(self.root)
        win.title("Paramètres d'analyse")
        win.geometry("350x200")
        win.resizable(False, False)

        tk.Label(win, text="Taille max d'affichage (Mo)").pack(anchor="w", padx=10, pady=5)
        max_display_var = tk.StringVar(value=str(settings.get("max_display_size_mb",50)))
        tk.Entry(win, textvariable=max_display_var).pack(anchor="w", padx=10)

        show_hex_var = tk.BooleanVar(value=settings.get("show_hex",True))
        tk.Checkbutton(win, text="Toujours afficher l'hexadécimal", variable=show_hex_var).pack(anchor="w", padx=10, pady=5)

        check_updates_var = tk.BooleanVar(value=settings.get("check_updates",True))
        tk.Checkbutton(win, text="Vérifier les mises à jour", variable=check_updates_var).pack(anchor="w", padx=10, pady=5)

        def apply_settings():
            try:
                max_size = int(max_display_var.get())
                if max_size <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Erreur","Taille max d'affichage invalide (>0 requis)")
                return
            new_settings = {
                "max_display_size_mb": max_size,
                "show_hex": show_hex_var.get(),
                "check_updates": check_updates_var.get()
            }
            with open(self.settings_file,"w") as f:
                json.dump(new_settings,f,indent=4)
            messagebox.showinfo("Paramètres","Paramètres sauvegardés avec succès.")
            win.destroy()

        tk.Button(win, text="Appliquer", command=apply_settings).pack(pady=10)

    # ==========================
    # VÉRIFICATION FS
    # ==========================
    def is_ext4(self, path):
        try:
            result = subprocess.run(["df","-T",path], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            if len(lines) >= 2:
                fs_type = lines[1].split()[1]
                self.fs_label.config(text=f"Systeme de fichier : {fs_type}")
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
                messagebox.showerror("Erreur","Permission refusée.")
                return
            if not self.is_ext4(path):
                messagebox.showerror("Erreur","Le fichier doit être sur EXT4.")
                return
            self.file_path.set(path)
            self.analyze_button.config(state="normal")

    # ==========================
    # ANALYSE
    # ==========================
    def run_analysis(self):
        path = self.file_path.get()
        if not path:
            messagebox.showerror("Erreur","Veuillez sélectionner un fichier.")
            return
        try:
            self.last_result = analyze(path)
            self.display_results()

            # Afficher le bouton "Nouvelle analyse"
            self.new_analysis_button.pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Erreur Analyse",str(e))

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
            # Réactiver tous les boutons de vue
            for btn in tab_info["buttons"].values():
                btn.config(state="normal")

        # Cacher le bouton jusqu'à la prochaine analyse
        self.new_analysis_button.pack_forget()

    # ==========================
    # DISPLAY RESULTS
    # ==========================
    def display_results(self):
        if not self.last_result: return
        def format_data(widget,data,indent=0):
            space="  "*indent
            if isinstance(data,dict):
                for k,v in data.items():
                    if isinstance(v,(dict,list)):
                        widget.insert(tk.END,f"{space}{k} :\n")
                        format_data(widget,v,indent+1)
                    else:
                        widget.insert(tk.END,f"{space}{k} : {v}\n")
            elif isinstance(data,list):
                for i,item in enumerate(data,1):
                    if isinstance(item,(dict,list)):
                        widget.insert(tk.END,f"{space}- Élément {i} :\n")
                        format_data(widget,item,indent+1)
                    else:
                        widget.insert(tk.END,f"{space}- {item}\n")
            else:
                widget.insert(tk.END,f"{space}{data}\n")

        for tab_name,tab_info in self.tabs.items():
            widget = tab_info["widget"]
            widget.delete("1.0", tk.END)
            key = self.tab_key_mapping[tab_name]
            if tab_name=="Résumé":
                widget.insert(tk.END,f"Fichier : {self.last_result.get('file','Non disponible')}\n")
                status=self.last_result.get("status","UNKNOWN")
                widget.insert(tk.END,f"Statut : {status}\n","success" if status=="SUCCESS" else "failed")
                format_data(widget,self.last_result.get("type_analysis",{}))
            else:
                data=self.last_result.get(key)
                if not data:
                    widget.insert(tk.END,"Aucune donnée disponible\n")
                else:
                    format_data(widget,data)
            for view,btn in tab_info["buttons"].items():
                if tab_name in ["Résumé","Contenu"] and view!="texte":
                    btn.config(state="disabled")
                else:
                    btn.config(state="normal")

    # ==========================
    # CHANGER DE VUE
    # ==========================
    def change_view(self, tab_name, view_type):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        tab_info = self.tabs[tab_name]
        widget = tab_info["widget"]
        frame = tab_info["frame"]

        widget.delete("1.0", tk.END)
        for child in frame.winfo_children():
            if isinstance(child,FigureCanvasTkAgg):
                child.get_tk_widget().destroy()

        key=self.tab_key_mapping[tab_name]
        data=self.last_result.get(key)

        # ==========================
        # CU9 – CARTE PHYSIQUE
        # ==========================
        if tab_name == "Carte physique" and view_type == "graphique":

            if not data or not isinstance(data, dict):
                widget.insert(tk.END, "Aucune donnée physique disponible\n")
                return

            extents = data.get("extents", [])

            if not extents:
                widget.insert(tk.END, "Aucun extent détecté\n")
                return

            if len(extents) == 1:
                widget.insert(tk.END, "Fichier contigu (1 seul extent)\n")

            # Nettoyage ancien graphique
            for child in frame.winfo_children():
                try:
                    child.destroy()
                except:
                    pass

            fig, ax = plt.subplots(figsize=(12, 2))

            # Calcul plage totale physique
            total_blocks = max(e["physical_end"] for e in extents)

            for extent in extents:
                start = extent["physical_start"]
                width = extent["length"]

                rect = plt.Rectangle(
                    (start, 0),
                    width,
                    1
                )
                ax.add_patch(rect)

            ax.set_xlim(0, total_blocks)
            ax.set_ylim(0, 1)
            ax.set_title("Carte physique des blocs (EXT4)")
            ax.set_xlabel("Blocs physiques")
            ax.axis("off")

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            return

    # ==========================
    # EXPORT PDF / TXT
    # ==========================
    def export_report(self):
        if not self.last_result:
            messagebox.showwarning("Attention","Aucune analyse disponible.")
            return

        file_path=filedialog.asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF files","*.pdf"),("Text files","*.txt")])
        if not file_path: return

        try:
            if file_path.endswith(".pdf"):
                doc=SimpleDocTemplate(file_path)
                elements=[]
                styles=getSampleStyleSheet()
                style=styles["Normal"]

                elements.append(Paragraph("<b>Linux File Analyzer Report</b>",styles["Heading1"]))
                elements.append(Spacer(1,0.3*inch))

                for tab_name,tab_info in self.tabs.items():
                    content=tab_info["widget"].get("1.0",tk.END)
                    elements.append(Paragraph(f"<b>{tab_name}</b>",styles["Heading2"]))
                    elements.append(Spacer(1,0.2*inch))
                    elements.append(Paragraph(content.replace("\n","<br/>"),style))
                    elements.append(Spacer(1,0.4*inch))
                doc.build(elements)
            elif file_path.endswith(".txt"):
                with open(file_path,"w",encoding="utf-8") as f:
                    for tab_name,tab_info in self.tabs.items():
                        content=tab_info["widget"].get("1.0",tk.END)
                        f.write(f"===== {tab_name} =====\n")
                        f.write(content)
                        f.write("\n\n")
            messagebox.showinfo("Succès","Rapport exporté avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur",str(e))