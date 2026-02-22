import tkinter as tk
from gui import FileAnalyzerGUI

def main():
    root = tk.Tk()
    app = FileAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()