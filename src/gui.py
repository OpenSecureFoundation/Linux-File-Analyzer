import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from FileAnalyzer.analyzer import analyze
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os


class FileAnalyzerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Linux File Analyzer - EXT4")
        self.root.geometry("950x650")

        # Icône (mettre un .ico ou .png dans src/)
        try:
            self.root.iconphoto(False, tk.PhotoImage(file="icon.png"))
        except:
            pass

        self.file_path = tk.StringVar()
        self.last_result = None

        self.create_widgets()

    # ==========================
    # UI CREATION
    # ==========================
    def create_widgets(self):

        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")

        ttk.Entry(top_frame, textvariable=self.file_path, width=70).pack(side="left", padx=5)

        ttk.Button(top_frame, text="Parcourir", command=self.browse_file).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Analyser", command=self.run_analysis).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Export PDF", command=self.export_pdf).pack(side="left", padx=5)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabs = {}

        tab_names = [
            "Résumé",
            "Métadonnées",
            "Organisation physique",
            "Fragmentation",
            "Contenu"
        ]

        for name in tab_names:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)

            text_widget = tk.Text(frame, wrap="word")
            scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)

            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Mise en forme
            text_widget.tag_configure("section", font=("Arial", 11, "bold"))
            text_widget.tag_configure("success", foreground="green")
            text_widget.tag_configure("failed", foreground="red")

            self.tabs[name] = text_widget

    # ==========================
    # FILE SELECTION
    # ==========================
    def browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_path.set(path)

    # ==========================
    # ANALYSIS
    # ==========================
    def run_analysis(self):
        path = self.file_path.get()

        if not path:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier.")
            return

        try:
            result = analyze(path)
            self.last_result = result
            self.display_results(result)

        except Exception as e:
            messagebox.showerror("Erreur Analyse", str(e))

    # ==========================
    # DISPLAY RESULTS
    # ==========================
    def display_results(self, result):

        for tab in self.tabs.values():
            tab.delete("1.0", tk.END)

        # ===== Résumé =====
        type_info = result.get("type_analysis", {})
        resume_tab = self.tabs["Résumé"]

        resume_tab.insert(tk.END, "=== RÉSUMÉ GÉNÉRAL ===\n", "section")
        resume_tab.insert(tk.END, f"Fichier : {result.get('file')}\n")

        status = result.get("status", "UNKNOWN")
        if status == "SUCCESS":
            resume_tab.insert(tk.END, f"Statut : {status}\n\n", "success")
        else:
            resume_tab.insert(tk.END, f"Statut : {status}\n\n", "failed")

        resume_tab.insert(tk.END, "=== TYPE DE FICHIER ===\n", "section")
        resume_tab.insert(tk.END, f"Type détecté : {type_info.get('file_type')}\n")
        resume_tab.insert(tk.END, f"Catégorie    : {type_info.get('category')}\n")
        resume_tab.insert(tk.END, f"Binaire      : {type_info.get('is_binary')}\n")
        resume_tab.insert(tk.END, f"Magic number : {type_info.get('magic_number')}\n")

        # ===== Métadonnées =====
        meta_tab = self.tabs["Métadonnées"]
        meta_tab.insert(tk.END, "=== MÉTADONNÉES ===\n", "section")

        for key, value in result.get("metadata", {}).items():
            meta_tab.insert(tk.END, f"{key} : {value}\n")

        # ===== Organisation physique =====
        layout_tab = self.tabs["Organisation physique"]
        layout_tab.insert(tk.END, "=== ORGANISATION PHYSIQUE ===\n", "section")

        layout = result.get("physical_layout", {})
        layout_tab.insert(tk.END, f"Total extents : {layout.get('total_extents')}\n\n")

        for extent in layout.get("extents", []):
            layout_tab.insert(
                tk.END,
                f"Logical: {extent['logical_start']}..{extent['logical_end']} | "
                f"Physical: {extent['physical_start']}..{extent['physical_end']} | "
                f"Length: {extent['length']}\n"
            )

        # ===== Fragmentation =====
        frag_tab = self.tabs["Fragmentation"]
        frag_tab.insert(tk.END, "=== FRAGMENTATION ===\n", "section")

        for key, value in result.get("fragmentation", {}).items():
            frag_tab.insert(tk.END, f"{key} : {value}\n")

        # ===== Contenu =====
        content_tab = self.tabs["Contenu"]
        content_tab.insert(tk.END, "=== CONTENU ===\n", "section")

        content = result.get("content")
        if content:
            content_tab.insert(tk.END, content.get("preview", "Non disponible"))
        else:
            content_tab.insert(tk.END, "Non disponible")

    # ==========================
    # EXPORT PDF
    # ==========================
    def export_pdf(self):

        if not self.last_result:
            messagebox.showwarning("Attention", "Aucune analyse disponible.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not file_path:
            return

        doc = SimpleDocTemplate(file_path)
        elements = []

        styles = getSampleStyleSheet()
        style = styles["Normal"]

        elements.append(Paragraph("<b>Linux File Analyzer Report</b>", styles["Heading1"]))
        elements.append(Spacer(1, 0.3 * inch))

        for tab_name, tab_widget in self.tabs.items():
            content = tab_widget.get("1.0", tk.END)
            elements.append(Paragraph(f"<b>{tab_name}</b>", styles["Heading2"]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph(content.replace("\n", "<br/>"), style))
            elements.append(Spacer(1, 0.4 * inch))

        doc.build(elements)

        messagebox.showinfo("Succès", "Rapport PDF généré avec succès.")