import os
from pathlib import Path
import pandas as pd
import matplotlib
# Use headless backend to guarantee seamless background execution without threading lockups
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class ChartGenerator:
    """Decoupled charting component to handle high-resolution image

    exports natively to the local storage system.
    """

    @staticmethod
    def _generate_clean_filename(base_path, suffix, extension=".png"):
        """Creates a standardized path string to prevent symbol crashes."""
        directory = os.path.dirname(base_path)
        base_file = os.path.splitext(os.path.basename(base_path))[0]
        sanitized_name = f"{base_file}_{suffix}{extension}"
        return os.path.join(directory, sanitized_name)

    @classmethod
    def generate_line_chart(cls, original_file_path, monthly_series, quarterly_series):
        """Project 1: Line chart for time series (monthly + quarterly aggregation)."""
        if (monthly_series is None or monthly_series.empty) and (quarterly_series is None or quarterly_series.empty):
            return None
        # Dual subplot if both available, else single
        if monthly_series is not None and not monthly_series.empty and quarterly_series is not None and not quarterly_series.empty:
            fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=False)
            # Monthly
            ax = axes[0]
            ax.plot(monthly_series.index, monthly_series.values, marker="o", linewidth=2.2, color="#4C78A8")
            ax.set_title(f"Monthly Sales Trend — Revenue in USD\nSource: {os.path.basename(original_file_path)}", fontsize=12, fontweight="bold", pad=10)
            ax.set_ylabel("Revenue in USD", fontsize=11)
            ax.set_xlabel("Month", fontsize=11)
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.set_axisbelow(True)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            ax.tick_params(axis="x", rotation=30, labelsize=9)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
            fig.autofmt_xdate()
            # Quarterly
            ax2 = axes[1]
            ax2.plot(quarterly_series.index, quarterly_series.values, marker="s", linewidth=2.2, color="#F58518")
            ax2.set_title("Quarterly Sales Trend — Revenue in USD", fontsize=12, fontweight="bold", pad=10)
            ax2.set_ylabel("Revenue in USD", fontsize=11)
            ax2.set_xlabel("Quarter", fontsize=11)
            ax2.grid(True, linestyle="--", alpha=0.6)
            ax2.set_axisbelow(True)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            ax2.tick_params(axis="x", rotation=30, labelsize=9)
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
            fig.tight_layout(rect=[0,0,1,0.96])
        else:
            series = monthly_series if monthly_series is not None and not monthly_series.empty else quarterly_series
            label = "Monthly" if monthly_series is not None and not monthly_series.empty else "Quarterly"
            fig, ax = plt.subplots(figsize=(12,5))
            ax.plot(series.index, series.values, marker="o", linewidth=2.5, color="#4C78A8")
            ax.set_title(f"{label} Sales Trend — Revenue in USD\nSource: {os.path.basename(original_file_path)}", fontsize=13, fontweight="bold", pad=12)
            ax.set_ylabel("Revenue in USD", fontsize=11); ax.set_xlabel("Date", fontsize=11)
            ax.grid(True, linestyle="--", alpha=0.6); ax.set_axisbelow(True)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            ax.tick_params(axis="x", rotation=30, labelsize=9)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
            fig.autofmt_xdate()
            plt.tight_layout()
        output_path = cls._generate_clean_filename(original_file_path, "sales_trends")
        plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return output_path

    @classmethod
    def generate_bar_graph(cls, original_file_path, metric_series):
        """Project 1: Bar chart compares CATEGORIES (groupby), not metrics."""
        if metric_series.empty or metric_series.sum() == 0:
            return None

        # If too many categories, cap at top 8 for readability
        if len(metric_series) > 8:
            metric_series = metric_series.nlargest(8)

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#4C78A8', '#F58518', '#54A24B', '#E45756', '#72B7B2', '#B279A2', '#9C755F', '#BAB0AC']
        slice_colors = colors[:len(metric_series)]
        # Horizontal for readability, sorted descending already
        bars = ax.barh(metric_series.index, metric_series.values, color=slice_colors, edgecolor='#333333', height=0.55)
        ax.set_xlabel('Revenue in USD', fontsize=11, fontweight='bold', labelpad=10)
        ax.set_ylabel('Category', fontsize=11, fontweight='bold')
        ax.set_title(f'Total Sales by Category\nSource: {os.path.basename(original_file_path)}', fontsize=13, pad=15, fontweight='bold')
        ax.grid(axis='x', linestyle='--', alpha=0.6)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        # Invert so top is largest
        ax.invert_yaxis()
        ax.bar_label(bars, fmt='%,.2f', padding=6, fontsize=9)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        plt.tight_layout()
        output_path = cls._generate_clean_filename(original_file_path, "category_comparison")
        plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return output_path

    @classmethod
    def generate_pie_chart(cls, original_file_path, metric_series):
        """Project 1: Pie chart for category share (<6 wedges)."""
        active_series = metric_series[metric_series > 0]
        if active_series.empty:
            return None
        # Cap at 5 + Other per spec for readability
        if len(active_series) > 5:
            top5 = active_series.nlargest(5)
            other = active_series.nsmallest(len(active_series)-5).sum()
            active_series = pd.concat([top5, pd.Series([other], index=["Other"])])
            # Re-sort descending
            active_series = active_series.sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = ['#4C78A8', '#F58518', '#54A24B', '#E45756', '#72B7B2', '#B279A2']
        slice_colors = colors[:len(active_series)]
        wedges, texts, autotexts = ax.pie(
            active_series.values,
            labels=active_series.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=slice_colors,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2, 'antialiased': True},
            pctdistance=0.85
        )
        plt.setp(texts, size=10, weight="bold")
        plt.setp(autotexts, size=9, weight="bold", color="white")
        ax.set_title(f'Market Share by Category\nSource: {os.path.basename(original_file_path)}', fontsize=13, pad=15, fontweight='bold')
        # Legend outside to avoid overlap
        ax.legend(wedges, active_series.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9, title="Category")
        ax.axis("equal")
        plt.tight_layout()
        output_path = cls._generate_clean_filename(original_file_path, "market_share")
        plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return output_path

    @classmethod
    def generate_summary(cls, original_file_path, processor):
        """Project 1: Short summary with total, top category, best quarter."""
        import pandas as pd
        kpis = processor.get_kpis()
        if not kpis:
            return None
        monthly = kpis.get("monthly")
        quarterly = kpis.get("quarterly")
        cat = kpis.get("category_totals")
        total = kpis.get("total_revenue", 0)
        top_cat = kpis.get("top_category", "N/A")
        top_val = kpis.get("top_value", 0)
        best_q = kpis.get("best_quarter", "N/A")
        best_val = kpis.get("best_value", 0)
        n = kpis.get("n_records", 0)
        # Determine date range string
        dmin = kpis.get("date_min")
        dmax = kpis.get("date_max")
        date_str = f"{dmin.date()} → {dmax.date()}" if pd.notna(dmin) and pd.notna(dmax) else "N/A"

        lines = [
            "="*64,
            "  SALES ANALYTICS — PROJECT 1 SUMMARY",
            "="*64,
            f"  Source    : {os.path.basename(original_file_path)}",
            f"  Records   : {n:,}  ({date_str})",
            f"  Detected  : Date='{processor.date_col}'  Category='{processor.category_col}'  Sales='{processor.value_col}'",
            f"  Total Revenue        : ${total:,.2f}",
            f"  Top Category         : {top_cat} (${top_val:,.2f})",
            f"  Best Quarter         : {best_q} (${best_val:,.2f})",
            "-"*64,
            "  Monthly Aggregation (resample ME):",
        ]
        if monthly is not None and not monthly.empty:
            for ts, val in monthly.items():
                lines.append(f"    {ts.strftime('%Y-%m')}: ${val:,.2f}")
        lines.append("  Quarterly Aggregation (resample QE):")
        if quarterly is not None and not quarterly.empty:
            for ts, val in quarterly.items():
                lines.append(f"    {ts.year}-Q{ts.quarter}: ${val:,.2f}")
        lines.extend([
            "-"*64,
            "  Chart choice:",
            "    Line (monthly/quarterly): continuous time → slope shows velocity/trend",
            "    Bar (by category): length encodes magnitude → precise ranking",
            "    Pie (<6 slices, top5+Other): angle shows share → proportional readability",
            "  Formatting: titles Revenue in USD, grid -- alpha 0.6, legend outside, top/right spines removed",
            "="*64,
        ])
        text = "\n".join(lines)
        out_path = os.path.join(os.path.dirname(original_file_path), os.path.splitext(os.path.basename(original_file_path))[0] + "_summary.txt")
        # Also write to output dir for consistency
        try:
            Path = __import__("pathlib").Path
            alt = Path(original_file_path).parent / "summary.txt"
            alt.write_text(text, encoding="utf-8")
        except Exception:
            pass
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        return out_path
