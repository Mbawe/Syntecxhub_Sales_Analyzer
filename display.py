import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from Data_Analytics import CSVDataProcessor
from Pie_chart_generation import ChartGenerator


class WorkspaceTab(ttk.Frame):
    """Manages an independent tab workspace for a single opened CSV file.
    Project 1: time series line (monthly/quarterly) + category bar/pie, auto-detect columns.
    """

    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path
        self.processor = CSVDataProcessor()

        success, message = self.processor.load_file(file_path)
        if not success:
            raise Exception(f"Failed to read file: {message}")

        self._build_ui()
        # Auto-select first metric
        if self.processor.numeric_columns:
            self.column_listbox.selection_set(0)
            self.on_metric_selected(None)

    def _build_ui(self):
        """Constructs layout: left controls, right stats, bottom summary. Filter removed per request."""
        # Info bar showing auto-detected mapping
        mapping = f"Detected: Date='{self.processor.date_col}'  Category='{self.processor.category_col}'  Sales='{self.processor.value_col}'"
        info_lbl = ttk.Label(self, text=mapping, font=("Arial", 8, "italic"), foreground="#0F172A", background="#EFF6FF", padding=6)
        info_lbl.pack(fill=tk.X, padx=10, pady=(5, 0))

        # Main Paned: Left / Right
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left Panel
        left_panel = ttk.Frame(main_pane, padding=5)
        main_pane.add(left_panel, weight=1)

        ttk.Label(left_panel, text="Select Metric for Statistics:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.column_listbox = tk.Listbox(left_panel, selectmode=tk.BROWSE, exportselection=False, height=8)
        self.column_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.column_listbox.bind("<<ListboxSelect>>", self.on_metric_selected)
        for col in self.processor.numeric_columns:
            self.column_listbox.insert(tk.END, col)

        # Charting Deck — Project 1: line (time series) + bar/pie (category)
        chart_frame = ttk.LabelFrame(left_panel, text=" Image Export Engine — Project 1 ", padding=8)
        chart_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(chart_frame, text="Export Sales Trends (Line) PNG", command=self.export_line_chart).pack(fill=tk.X, pady=2)
        ttk.Button(chart_frame, text="Export Category Bar PNG", command=self.export_bar_chart).pack(fill=tk.X, pady=2)
        ttk.Button(chart_frame, text="Export Market Share Pie PNG", command=self.export_pie_chart).pack(fill=tk.X, pady=2)

        # Data navigation / edit
        nav_frame = ttk.LabelFrame(left_panel, text=" Data Navigation & Edit ", padding=8)
        nav_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(nav_frame, text="View / Edit Data Table", command=self.open_data_table).pack(fill=tk.X, pady=2)
        ttk.Button(nav_frame, text="Save Edited CSV", command=self.save_edited).pack(fill=tk.X, pady=2)
        ttk.Button(nav_frame, text="Export Global Summary TXT", command=self.export_summary).pack(fill=tk.X, pady=2)

        # Right Panel — Stats + Global summary
        right_panel = ttk.Frame(main_pane, padding=5)
        main_pane.add(right_panel, weight=2)

        # Stats tree (per-column)
        stats_frame = ttk.LabelFrame(right_panel, text=" Calculated Estimations & Statistics (per metric) ", padding=8)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        self.stats_tree = ttk.Treeview(stats_frame, columns=("Metric", "Value"), show="headings", height=7)
        self.stats_tree.heading("Metric", text="Statistical Indicator")
        self.stats_tree.heading("Value", text="Calculated Result")
        self.stats_tree.column("Metric", width=200, anchor=tk.W)
        self.stats_tree.column("Value", width=180, anchor=tk.E)
        self.stats_tree.pack(fill=tk.BOTH, expand=True)

        # Global Project 1 summary (below stats)
        summary_frame = ttk.LabelFrame(right_panel, text=" Global Project 1 Summary ", padding=8)
        summary_frame.pack(fill=tk.BOTH, expand=False, pady=(8, 0))
        self.global_text = tk.Text(summary_frame, height=7, wrap=tk.WORD, font=("Consolas", 8), bg="#F8FAFC")
        self.global_text.pack(fill=tk.BOTH, expand=True)
        self.global_text.configure(state=tk.DISABLED)
        self._refresh_global_summary()
        ttk.Button(summary_frame, text="Copy Summary", command=self.copy_summary).pack(pady=4)

    def _refresh_global_summary(self):
        kpis = self.processor.get_kpis()
        if not kpis:
            return
        lines = [
            f"Records: {kpis.get('n_records',0):,}  Cats: {kpis.get('n_categories',0)}",
            f"Period: {kpis.get('date_min')} → {kpis.get('date_max')}",
            f"Total Revenue: ${kpis.get('total_revenue',0):,.2f}",
            f"Top Category: {kpis.get('top_category')} (${kpis.get('top_value',0):,.2f})",
            f"Best Quarter: {kpis.get('best_quarter')} (${kpis.get('best_value',0):,.2f})",
            f"Monthly periods: {len(kpis.get('monthly',[]))}  Quarterly: {len(kpis.get('quarterly',[]))}",
        ]
        self.global_text.configure(state=tk.NORMAL)
        self.global_text.delete("1.0", tk.END)
        self.global_text.insert(tk.END, "\n".join(lines))
        self.global_text.configure(state=tk.DISABLED)

    def on_metric_selected(self, event):
        for row in self.stats_tree.get_children():
            self.stats_tree.delete(row)
        sel = self.column_listbox.curselection()
        if not sel:
            return
        col = self.column_listbox.get(sel[0])
        stats = self.processor.get_summary_statistics(col)
        for ind, val in stats.items():
            fmt = f"{val:,.2f}" if isinstance(val, (int, float)) and ind != "Count" else str(val)
            self.stats_tree.insert("", tk.END, values=(ind, fmt))

    def export_line_chart(self):
        monthly = self.processor.get_monthly_sales()
        quarterly = self.processor.get_quarterly_sales()
        if (monthly is None or monthly.empty) and (quarterly is None or quarterly.empty):
            messagebox.showwarning("Export Void", "No date/value data for time series.\nCheck that CSV has a Date column.")
            return
        out = ChartGenerator.generate_line_chart(self.file_path, monthly, quarterly)
        if out:
            messagebox.showinfo("Export Success", f"Sales trends PNG saved to:\n{out}\n\nLine charts for continuous time (monthly+quarterly), grid -- alpha 0.6, legend outside.")

    def export_bar_chart(self):
        totals = self.processor.get_category_totals()
        if totals.empty or totals.sum() == 0:
            messagebox.showwarning("Export Void", "No category data to visualize.\nCheck that CSV has a Category column.")
            return
        out = ChartGenerator.generate_bar_graph(self.file_path, totals)
        if out:
            messagebox.showinfo("Export Success", f"Category bar PNG saved to:\n{out}\n\nBar length encodes magnitude (ranked).")
        else:
            messagebox.showwarning("Export Void", "Bar chart not generated — all values zero.")

    def export_pie_chart(self):
        totals = self.processor.get_category_totals()
        if totals.empty or totals.sum() == 0:
            messagebox.showwarning("Export Void", "No category data to visualize.")
            return
        out = ChartGenerator.generate_pie_chart(self.file_path, totals)
        if out:
            messagebox.showinfo("Export Success", f"Market share pie PNG saved to:\n{out}\n\nPie capped at <6 slices (top5+Other) for readability.")
        else:
            messagebox.showwarning("Export Void", "Pie not generated — zero or single slice.")

    def export_summary(self):
        out = ChartGenerator.generate_summary(self.file_path, self.processor)
        if out:
            messagebox.showinfo("Export Success", f"Global summary TXT saved to:\n{out}")
        else:
            messagebox.showwarning("Export Void", "Could not generate summary.")

    def copy_summary(self):
        txt = self.global_text.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(txt)
        messagebox.showinfo("Copied", "Summary copied to clipboard.")

    def open_data_table(self):
        win = tk.Toplevel(self)
        win.title(f"Data Table — {os.path.basename(self.file_path)}")
        win.geometry("900x520")
        win.transient(self.winfo_toplevel())
        # Top info
        info = f"{len(self.processor.df):,} rows × {len(self.processor.df.columns)} cols  |  Double-click a cell to edit"
        ttk.Label(win, text=info, font=("Arial", 9, "italic"), foreground="#334155").pack(fill=tk.X, padx=8, pady=6)
        # Treeview with scrollbars
        frame = ttk.Frame(win, padding=6)
        frame.pack(fill=tk.BOTH, expand=True)
        cols = list(self.processor.df.columns)
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140, anchor=tk.W)
        # Pagination: show 200 rows at a time
        page_size = 200
        total = len(self.processor.df)
        pages = (total + page_size - 1) // page_size
        cur_page = [0]

        def load_page(idx):
            for r in tree.get_children():
                tree.delete(r)
            start = idx * page_size
            end = min(start + page_size, total)
            for i in range(start, end):
                vals = [str(self.processor.df.at[i, c]) for c in cols]
                tree.insert("", tk.END, iid=str(i), values=vals)
            page_lbl.configure(text=f"Page {idx+1}/{pages}  ({start+1}–{end} of {total})")

        page_row = ttk.Frame(win, padding=4)
        page_row.pack(fill=tk.X)
        page_lbl = ttk.Label(page_row, text="")
        page_lbl.pack(side=tk.LEFT, padx=8)
        ttk.Button(page_row, text="◀ Prev", command=lambda: (cur_page.__setitem__(0, max(0, cur_page[0]-1)), load_page(cur_page[0]))).pack(side=tk.LEFT, padx=4)
        ttk.Button(page_row, text="Next ▶", command=lambda: (cur_page.__setitem__(0, min(pages-1, cur_page[0]+1)), load_page(cur_page[0]))).pack(side=tk.LEFT, padx=4)
        ttk.Button(page_row, text="Save CSV", command=lambda: self.save_edited()).pack(side=tk.RIGHT, padx=8)

        def on_double_click(event):
            sel = tree.selection()
            if not sel:
                return
            row_idx = int(sel[0])
            # Which column clicked?
            col_id = tree.identify_column(event.x)
            try:
                col_idx = int(col_id.replace("#","")) - 1
            except Exception:
                return
            if col_idx < 0 or col_idx >= len(cols):
                return
            col_name = cols[col_idx]
            old_val = self.processor.df.at[row_idx, col_name]
            new_val = simpledialog.askstring("Edit Cell", f"Row {row_idx}  Col '{col_name}'\nOld: {old_val}\nNew:", initialvalue=str(old_val), parent=win)
            if new_val is None:
                return
            ok, msg = self.processor.update_cell(row_idx, col_name, new_val)
            if ok:
                tree.set(sel[0], column=col_name, value=new_val)
                self._refresh_global_summary()
                # Refresh stats for current selection
                self.on_metric_selected(None)
            else:
                messagebox.showerror("Edit Failed", msg, parent=win)

        tree.bind("<Double-Button-1>", on_double_click)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        load_page(0)
        win.grab_set()

    def save_edited(self):
        ok, msg = self.processor.save_current(self.file_path)
        if ok:
            messagebox.showinfo("Saved", f"Edited CSV saved to:\n{msg}")
            self._refresh_global_summary()
        else:
            messagebox.showerror("Save Failed", msg)


class MainInterfaceLayout(ttk.Notebook):
    """The central multi-tab view controller."""

    def __init__(self, parent):
        super().__init__(parent)
        self.enable_drop_bindings()

    def enable_drop_bindings(self):
        self.bind("<Button-2>", self.close_tab_event)

    def append_new_csv_workspace(self, file_path):
        for index in range(self.index("end")):
            try:
                tab_frame = self.nametowidget(self.tabs()[index])
                if getattr(tab_frame, "file_path", None) == file_path:
                    self.select(index)
                    return
            except Exception:
                pass
        try:
            tab_title = os.path.basename(file_path)
            new_tab = WorkspaceTab(self, file_path)
            self.add(new_tab, text=f" {tab_title}   ")
            self.select(new_tab)
        except Exception as e:
            messagebox.showerror("Workspace Load Failure", f"Could not map document structure:\n{e}")

    def close_tab_event(self, event):
        clicked = self.identify(event.x, event.y)
        if "tab" in clicked:
            try:
                idx = self.index(f"@{event.x},{event.y}")
                self.forget(idx)
            except Exception:
                pass
