import os
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
    def generate_bar_graph(cls, original_file_path, metric_series):
        """Generates a separate comparison bar graph tracking numeric aggregates."""
        if metric_series.empty:
            return None

        # Instantiate a clean figure layout context
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Premium color palette assignment 
        colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a']
        slice_colors = colors[:len(metric_series)]
        
        # Render horizontal columns to maximize label layout space
        bars = ax.barh(metric_series.index, metric_series.values, color=slice_colors, edgecolor='#333333', height=0.6)
        
        # Format axes cleanly
        ax.set_xlabel('Calculated Sum Value', fontsize=11, fontweight='bold', labelpad=10)
        ax.set_title(f'Comparative Metrics Summary\nSource: {os.path.basename(original_file_path)}', fontsize=13, pad=15, fontweight='bold')
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        
        # Add labels directly to bars for rapid manual visibility
        ax.bar_label(bars, fmt='%,.2f', padding=6, fontsize=9)
        
        # Minimize clipping
        plt.tight_layout()
        
        # Write asset out cleanly
        output_path = cls._generate_clean_filename(original_file_path, "comparison_bar")
        plt.savefig(output_path, dpi=300)
        plt.close(fig)
        
        return output_path

    @classmethod
    def generate_pie_chart(cls, original_file_path, metric_series):
        """Generates a separate relative share pie chart tracking distributions."""
        # Strip zeroes out to prevent overlapping zero-percent label collisions
        active_series = metric_series[metric_series > 0]
        
        if active_series.empty:
            return None

        fig, ax = plt.subplots(figsize=(8, 8))
        
        colors = ['#4994c4', '#84b7db', '#e68435', '#f3b879', '#53b453', '#9ce49c']
        slice_colors = colors[:len(active_series)]
        
        # Build out the visualization frame
        wedges, texts, autotexts = ax.pie(
            active_series.values,
            labels=active_series.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=slice_colors,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2, 'antialiased': True}
        )
        
        # Maximize text legibility thresholds
        plt.setp(texts, size=10, weight="bold")
        plt.setp(autotexts, size=9, weight="bold", color="#222222")
        
        ax.set_title(f'Share Distribution Metrics\nSource: {os.path.basename(original_file_path)}', fontsize=13, pad=15, fontweight='bold')
        
        plt.tight_layout()
        
        output_path = cls._generate_clean_filename(original_file_path, "share_pie")
        plt.savefig(output_path, dpi=300)
        plt.close(fig)
        
        return output_path
