import pandas as pd


class CSVDataProcessor:
    """Handles parsing, runtime cleaning, explicit column discovery,

    and arbitrary statistics calculations for variable CSV layouts.
    """

    def __init__(self):
        self.df = None
        self.filtered_df = None
        self.all_columns = []
        self.numeric_columns = []
        self.status_column = None

    def load_file(self, file_path):
        """Loads a CSV file dynamically and discovers column characteristics."""
        try:
            # Load file and strip trailing spaces from column names
            self.df = pd.read_csv(file_path)
            self.df.columns = self.df.columns.str.strip()
            self.all_columns = list(self.df.columns)

            # Discover numeric metrics automatically while skipping typical structural IDs/dates
            self.numeric_columns = []
            for col in self.df.columns:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    if not any(
                        x in col.lower() for x in ["id", "date", "year", "code"]
                    ):
                        self.numeric_columns.append(col)

            # Locate potential filtering columns for online/status conditions
            self.status_column = None
            for col in self.df.columns:
                if col.lower() in [
                    "online",
                    "sales channel",
                    "status",
                    "online(y/n)",
                ]:
                    self.status_column = col
                    break

            # Initialize filtered data to complete dataset by default
            self.filtered_df = self.df.copy()
            return True, "Success"
        except Exception as e:
            return False, str(e)

    def apply_filter(self, enabled=True, filter_value="Online"):
        """Filters dataset rows dynamically if a valid routing status column exists."""
        if self.df is None:
            return

        if enabled and self.status_column:
            # Handle normalized checks for 'Online', 'Y', 'Yes', etc.
            val_clean = str(filter_value).strip().lower()
            mask = self.df[self.status_column].astype(str).str.strip().str.lower() == val_clean
            self.filtered_df = self.df[mask].copy()
        else:
            self.filtered_df = self.df.copy()

    def get_summary_statistics(self, column_name):
        """Calculates explicit data metrics for an isolated numeric column."""
        if self.filtered_df is None or column_name not in self.numeric_columns:
            return {}

        target_series = self.filtered_df[column_name].dropna()

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
        """Aggregates absolute sums across every detected metric column for charting usage."""
        if self.filtered_df is None or not self.numeric_columns:
            return pd.Series(dtype=float)
        return self.filtered_df[self.numeric_columns].sum()
