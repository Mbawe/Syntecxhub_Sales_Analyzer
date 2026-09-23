import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from display import MainInterfaceLayout


class CSVAnalyzerApp(tk.Tk):
    """The root runtime environment for the multi-tab CSV analytical utility."""

    def __init__(self):
        super().__init__()
        self.title("Dynamic CSV Data Engine")
        self.geometry("1100x680")
        self.minsize(850, 500)
        
        self._set_ui_theme()
        self._build_main_window_layout()

    def _set_ui_theme(self):
        """Applies a clean UI theme configuration framework."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure layout styling properties for browser-style scannability
        style.configure('TNotebook', background='#e0e0e0', padding=2)
        style.configure('TNotebook.Tab', padding=[12, 6], background='#d0d0d0', font=('Arial', 9))
        style.map('TNotebook.Tab',
                  background=[('selected', '#ffffff'), ('active', '#eaeaea')],
                  font=[('selected', ('Arial', 9, 'bold'))])
        
        style.configure('TButton', font=('Arial', 9, 'bold'), padding=6)
        style.configure('Treeview.Heading', font=('Arial', 9, 'bold'), background='#eaeaea')
        style.configure('Treeview', rowheight=25, font=('Arial', 9))

    def _build_main_window_layout(self):
        """Constructs structural global navigation boundaries."""
        # Persistent global header execution toolbar
        nav_bar = ttk.Frame(self, padding=8, relief=tk.RAISED)
        nav_bar.pack(fill=tk.X, side=tk.TOP)
        
        open_btn = ttk.Button(
            nav_bar, 
            text="📁 Import CSV Document Via File Explorer", 
            command=self.trigger_file_explorer_selection
        )
        open_btn.pack(side=tk.LEFT, padx=5)
        
        status_lbl = ttk.Label(
            nav_bar, 
            text="Tip: Middle-click a browser tab to close its active dataset workspace.", 
            font=("Arial", 9, "italic"),
            foreground="#555555"
        )
        status_lbl.pack(side=tk.RIGHT, padx=10)

        # Initialize the global layout notebook
        self.notebook = MainInterfaceLayout(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Display explicit home greeting view if empty
        self.welcome_frame = ttk.Frame(self.notebook, padding=40)
        self.notebook.add(self.welcome_frame, text=" Home Workspace ")
        
        lbl_title = ttk.Label(self.welcome_frame, text="Multi-Document Analysis Platform", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=(40, 10))
        
        lbl_desc = ttk.Label(
            self.welcome_frame, 
            text="An automated parsing system built to handle shifting file columns natively.\n"
                 "Isolate row records, track multi-column metrics, and export crisp PNG charts seamlessly.",
            justify=tk.CENTER,
            font=("Arial", 10)
        )
        lbl_desc.pack(pady=10)
        
        action_btn = ttk.Button(self.welcome_frame, text="Browse Files Now", command=self.trigger_file_explorer_selection)
        action_btn.pack(pady=20)

    def trigger_file_explorer_selection(self):
        """Launches the operational system environment file navigator."""
        selected_path = filedialog.askopenfilename(
            title="Locate Target CSV Document",
            filetypes=[("Comma Separated Values", "*.csv"), ("All Data Files", "*.*")]
        )
        
        if selected_path:
            # Clear initial baseline card if real workspaces are running
            if self.welcome_frame in self.notebook.winfo_children():
                try:
                    self.notebook.forget(self.welcome_frame)
                    self.welcome_frame.destroy()
                except Exception:
                    pass
            
            # Mount workspace into browser tab structure
            self.notebook.append_new_csv_workspace(selected_path)


if __name__ == "__main__":
    app = CSVAnalyzerApp()
    app.mainloop()
