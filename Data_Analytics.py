import pandas as pd


class CSVDataProcessor:
    """Handles parsing, runtime cleaning, explicit column discovery,
    and arbitrary statistics calculations for variable CSV layouts.
    Auto-detects Date/Category/Sales_Amount for any CSV (per Project 1 spec).
    """

    def __init__(self):
        self.df = None
        self.filtered_df = None
        self.all_columns = []
        self.numeric_columns = []
        # Project 1 auto-detected mappings
        self.date_col = None
        self.category_col = None
        self.value_col = None

    def _parse_date_candidates(self):
        for c in self.df.columns:
            if any(kw in c.lower() for kw in ["date", "time", "day", "timestamp"]):
                try:
                    self.df[c] = pd.to_datetime(self.df[c], errors="coerce")
                except Exception:
                    pass

    def _guess_project_columns(self):
        cols = self.df.columns.tolist()
        # Date: first datetime dtype or date keyword
        self.date_col = None
        for c in cols:
            if pd.api.types.is_datetime64_any_dtype(self.df[c]):
                self.date_col = c
                break
        if self.date_col is None:
            for c in cols:
                if any(kw in c.lower() for kw in ["date", "time", "day", "timestamp"]):
                    s = pd.to_datetime(self.df[c], errors="coerce")
                    if s.notna().sum() > 0:
                        self.df[c] = s
                        self.date_col = c
                        break
        # Category: string col <80 uniques, prefer category/type/item — exclude numeric value candidates
        numeric_set = set(self.df.select_dtypes(include="number").columns.tolist())
        cat_candidates = []
        for c in cols:
            if c == self.date_col or c in numeric_set:
                continue
            if pd.api.types.is_numeric_dtype(self.df[c]):
                continue
            nunique = self.df[c].nunique(dropna=True)
            if nunique == 0 or nunique > 80:
                continue
            low = c.lower()
            score = 0
            for i, kw in enumerate(["category", "type", "item", "product", "region", "country", "channel", "segment", "client", "location"]):
                if kw in low:
                    score = 100 - i * 10
                    break
            if self.df[c].dtype == "object":
                score += 5
            cat_candidates.append((score, c))
        cat_candidates.sort(reverse=True)
        self.category_col = cat_candidates[0][1] if cat_candidates else None
        if self.category_col is None:
            for c in cols:
                if c != self.date_col and self.df[c].dtype == "object":
                    self.category_col = c
                    break
        # Value: numeric col preferring revenue/sales
        numeric_cols = self.df.select_dtypes(include="number").columns.tolist()
        for c in cols:
            if c not in numeric_cols:
                try:
                    if pd.to_numeric(self.df[c], errors="coerce").notna().sum() > len(self.df) * 0.7:
                        numeric_cols.append(c)
                except Exception:
                    pass
        val_cands = []
        for c in numeric_cols:
            if c == self.date_col:
                continue
            low = c.lower()
            score = 0
            for i, kw in enumerate(["revenue", "sales", "amount", "total", "profit", "price", "cost", "value"]):
                if kw in low:
                    score = 100 - i * 5
                    if kw in ("revenue", "sales"):
                        score += 20
                    if "total" in low and ("revenue" in low or "sales" in low):
                        score += 10
                    break
            try:
                mv = pd.to_numeric(self.df[c], errors="coerce").mean()
                if pd.notna(mv) and mv > 1000:
                    score += 2
            except Exception:
                pass
            val_cands.append((score, c))
        val_cands.sort(reverse=True)
        self.value_col = val_cands[0][1] if val_cands else (numeric_cols[0] if numeric_cols else None)

    def load_file(self, file_path):
        """Loads a CSV file dynamically and discovers column characteristics."""
        try:
            self.df = pd.read_csv(file_path)
            self.df.columns = self.df.columns.str.strip()
            self.all_columns = list(self.df.columns)

            # Discover numeric metrics while skipping IDs/dates
            self.numeric_columns = []
            for col in self.df.columns:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    if not any(x in col.lower() for x in ["id", "date", "year", "code"]):
                        self.numeric_columns.append(col)

            # Auto-detect Project 1 columns (Date/Category/Sales_Amount) for any layout
            self._parse_date_candidates()
            self._guess_project_columns()

            # No Online filter — keep full dataset (filter removed per request)
            self.filtered_df = self.df.copy()
            return True, "Success"
        except Exception as e:
            return False, str(e)

    # Removed: apply_filter (Online) — per request to get rid of it

    def get_summary_statistics(self, column_name):
        """Calculates explicit data metrics for an isolated numeric column."""
        if self.filtered_df is None or column_name not in self.numeric_columns:
            return {}
        target_series = pd.to_numeric(self.filtered_df[column_name], errors="coerce").dropna()
        if target_series.empty:
            return {}
        return {
            "Count": int(target_series.count()),
            "Sum": float(target_series.sum()),
            "Mean": float(target_series.mean()),
            "Median": float(target_series.median()),
            "Min": float(target_series.min()),
            "Max": float(target_series.max()),
            "Std Dev": float(target_series.std()) if target_series.count() > 1 else 0.0,
        }

    def compute_all_totals(self):
        """Aggregates sums across numeric metrics (legacy). For Project 1, use compute_category_totals."""
        if self.filtered_df is None or not self.numeric_columns:
            return pd.Series(dtype=float)
        return pd.to_numeric(self.filtered_df[self.numeric_columns].sum(), errors="coerce")

    # --- Project 1: Time series & category aggregations ---
    def get_monthly_sales(self):
        if self.df is None or not self.date_col or not self.value_col:
            return pd.Series(dtype=float)
        df = self.df.copy()
        df[self.date_col] = pd.to_datetime(df[self.date_col], errors="coerce")
        df[self.value_col] = pd.to_numeric(df[self.value_col], errors="coerce")
        df = df.dropna(subset=[self.date_col, self.value_col]).sort_values(self.date_col)
        if df.empty:
            return pd.Series(dtype=float)
        s = df.set_index(self.date_col).resample("ME")[self.value_col].sum()
        s = s.asfreq("ME", fill_value=0.0)
        s.name = "Monthly"
        return s

    def get_quarterly_sales(self):
        if self.df is None or not self.date_col or not self.value_col:
            return pd.Series(dtype=float)
        df = self.df.copy()
        df[self.date_col] = pd.to_datetime(df[self.date_col], errors="coerce")
        df[self.value_col] = pd.to_numeric(df[self.value_col], errors="coerce")
        df = df.dropna(subset=[self.date_col, self.value_col]).sort_values(self.date_col)
        if df.empty:
            return pd.Series(dtype=float)
        s = df.set_index(self.date_col).resample("QE")[self.value_col].sum()
        s = s.asfreq("QE", fill_value=0.0)
        s.name = "Quarterly"
        return s

    def get_category_totals(self):
        if self.df is None or not self.category_col or not self.value_col:
            return pd.Series(dtype=float)
        tmp = self.df.copy()
        tmp[self.value_col] = pd.to_numeric(tmp[self.value_col], errors="coerce")
        tmp = tmp.dropna(subset=[self.category_col, self.value_col])
        if tmp.empty:
            return pd.Series(dtype=float)
        s = tmp.groupby(self.category_col, observed=True)[self.value_col].sum().sort_values(ascending=False)
        s.name = "CategoryTotals"
        return s

    def get_kpis(self):
        if self.df is None or not self.value_col:
            return {}
        monthly = self.get_monthly_sales()
        quarterly = self.get_quarterly_sales()
        cat = self.get_category_totals()
        total = float(pd.to_numeric(self.df[self.value_col], errors="coerce").sum())
        top_cat = str(cat.idxmax()) if not cat.empty else "N/A"
        top_val = float(cat.max()) if not cat.empty else 0.0
        if not quarterly.empty and quarterly.sum() > 0:
            bq = quarterly.idxmax()
            bq_label = f"{bq.year}-Q{bq.quarter}"
            bq_val = float(quarterly.max())
        else:
            bq_label = "N/A"
            bq_val = 0.0
        date_series = pd.to_datetime(self.df[self.date_col], errors="coerce") if self.date_col else pd.Series(dtype="datetime64[ns]")
        return {
            "total_revenue": total,
            "n_records": int(len(self.df)),
            "n_categories": int(cat.size) if not cat.empty else 0,
            "date_min": date_series.min() if not date_series.empty else None,
            "date_max": date_series.max() if not date_series.empty else None,
            "top_category": top_cat,
            "top_value": top_val,
            "best_quarter": bq_label,
            "best_value": bq_val,
            "monthly": monthly,
            "quarterly": quarterly,
            "category_totals": cat,
        }

    def update_cell(self, row_idx, col_name, new_value):
        """Edit data in place for navigation/edit feature."""
        if self.df is None or col_name not in self.df.columns:
            return False, "Column not found"
        try:
            self.df.at[row_idx, col_name] = new_value
            # Re-coerce types if needed
            if pd.api.types.is_numeric_dtype(self.df[col_name]):
                self.df[col_name] = pd.to_numeric(self.df[col_name], errors="coerce")
            elif "date" in col_name.lower():
                self.df[col_name] = pd.to_datetime(self.df[col_name], errors="coerce")
            self.filtered_df = self.df.copy()
            # Re-discover numeric if type changed
            return True, "Updated"
        except Exception as e:
            return False, str(e)

    def save_current(self, path):
        try:
            self.df.to_csv(path, index=False)
            return True, path
        except Exception as e:
            return False, str(e)
