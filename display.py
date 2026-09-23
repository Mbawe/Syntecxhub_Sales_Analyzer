import os
import tkinter as tk
from tkinter import ttk, messagebox
from Data_Analytics import CSVDataProcessor
from Pie_chart_generation import ChartGenerator


class WorkspaceTab(ttk.Frame):
    """Manages an independent tab workspace for a single opened CSV file."""

    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path
        self.processor = CSVDataProcessor()

        # Load file and initialize data metrics
        success, message = self.processor.load_file(file_path)
        if not success:
            raise Exception(f"Failed to read file: {message}")

        self._build_ui()
        self.refresh_analysis()

    def _build_ui(self):
        """Constructs a responsive, scannable layout configuration."""
        # Top-level control deck
        filter_frame = ttk.LabelFrame(self, text=" Data Row Filters ", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        self.filter_var = tk.BooleanVar(value=True)
        self.filter_check = ttk.Checkbutton(
            filter_frame,
            text="Isolate Row Context (Filter by Channel Status)",
            variable=self.filter_var,
            command=self.refresh_analysis,
        )
        self.filter_check.pack(side=tk.LEFT, padx=5)

        self.filter_val_entry = ttk.Entry(filter_frame, width=15)
        self.filter_val_entry.insert(0, "Online")
        self.filter_val_entry.pack(side=tk.LEFT, padx=5)

        # Main Workspace Division: Left Controls, Right Analytics Output
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left Column Selector Card
        left_panel = ttk.Frame(main_pane, padding=5)
        main_pane.add(left_panel, weight=1)

        ttk.Label(left_panel, text="Select Metric for Statistics:", font=("Arial", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 5)
        )

        # Multi-selection listbox for manual analysis tracking
        self.column_listbox = tk.Listbox(left_panel, selectmode=tk.BROWSE, exportselection=False, height=12)
        self.column_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.column_listbox.bind("<<ListboxSelect>>", self.on_metric_selected)

        for col in self.processor.numeric_columns:
            self.column_listbox.insert(tk.END, col)

        # Charting Action Deck
        chart_frame = ttk.LabelFrame(left_panel, text=" Image Export Engine ", padding=10)
        chart_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(chart_frame, text="Export Comparison Bar PNG", command=self.export_bar_chart).pack(
            fill=tk.X, pady=3
        )
        ttk.Button(chart_frame, text="Export Share Pie PNG", command=self.export_pie_chart).pack(
            fill=tk.X, pady=3
        )

        # Right Analysis Statistical Panel
        right_panel = ttk.LabelFrame(main_pane, text=" Calculated Estimations & Statistics ", padding=10)
        main_pane.add(right_panel, weight=2)

        # Structured Table View for universal scannability
        self.stats_tree = ttk.Treeview(right_panel, columns=("Metric", "Value"), show="headings", height=10)
        self.stats_tree.heading("Metric", text="Statistical Indicator")
        self.stats_tree.heading("Value", text="Calculated Result")
        self.stats_tree.column("Metric", width=200, anchor=tk.W)
        self.stats_tree.column("Value", width=180, anchor=tk.E)
        self.stats_tree.pack(fill=tk.BOTH, expand=True)

    def refresh_analysis(self):
        """Re-runs analytical transformations based on structural row adjustments."""
        filter_text = self.filter_val_entry.get().strip()
        self.processor.apply_filter(enabled=self.filter_var.get(), filter_value=filter_text)
        self.on_metric_selected(None)

    def on_metric_selected(self, event):
        """Updates display tables dynamically using explicit calculations."""
        # Clean current tree items out
        for row in self.stats_tree.get_children():
            self.stats_tree.delete(row)

        selection = self.column_listbox.curselection()
        if not selection:
            return

        selected_col = self.column_listbox.get(selection[0])
        stats = self.processor.get_summary_statistics(selected_col)

        # Render summary figures using clean string mapping formats
        for indicator, val in stats.items():
            fmt_val = f"{val:,.2f}" if isinstance(val, (int, float)) and indicator != "Count" else str(val)
            self.stats_tree.insert("", tk.END, values=(indicator, fmt_val))

    def export_bar_chart(self):
        """Triggers decoupled generation for isolated comparison bar plots."""
        totals = self.processor.compute_all_totals()
        if totals.empty:
            messagebox.showwarning("Export Void", "No viable filtered numeric records found to visualize.")
            return

        out_path = ChartGenerator.generate_bar_graph(self.file_path, totals)
        if out_path:
            messagebox.showinfo("Export Success", f"Bar graph PNG saved to:\n{out_path}")

    def export_pie_chart(self):
        """Triggers decoupled generation for isolated distribution pie plots."""
        totals = self.processor.compute_all_totals()
        if totals.empty:
            messagebox.showwarning("Export Void", "No viable filtered numeric records found to visualize.")
            return

        out_path = ChartGenerator.generate_pie_chart(self.file_path, totals)
        if out_path:
            messagebox.showinfo("Export Success", f"Pie chart PNG saved to:\n{out_path}")


class MainInterfaceLayout(ttk.Notebook):
    """The central multi-tab view controller for the workspace platform."""

    def __init__(self, parent):
        super().__init__(parent)
        self.enable_drop_bindings()

    def enable_drop_bindings(self):
        """Creates standard workspace tracking context hooks."""
        # Tab closing behavior using middle-click mouse mapping natively
        self.bind("<Button-2>", self.close_tab_event)

    def append_new_csv_workspace(self, file_path):
        """Spawns an isolated processing frame into a unique tab layout."""
        # Prevent identical duplicate document workspaces from fragmenting window frames
        for index in range(self.index("end")):
            tab_frame = self.nametowidget(self.tabs()[index])
            if getattr(tab_frame, "file_path", None) == file_path:
                self.select(index)
                return

        try:
            tab_title = os.path.basename(file_path)
            new_tab = WorkspaceTab(self, file_path)
            self.add(new_tab, text=f" {tab_title}   ")
            self.select(new_tab)
        except Exception as e:
            messagebox.showerror("Workspace Load Failure", f"Could not map document structure:\n{e}")

    def close_tab_event(self, event):
        """Destroys execution contexts cleanly for targeted browser tabs."""
        clicked_element = self.identify(event.x, event.y)
        if "tab" in clicked_element:
            tab_index = self.index(f"@{event.x},{event.y}")
            self.forget(tab_index)
 