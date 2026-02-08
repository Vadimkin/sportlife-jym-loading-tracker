#!/usr/bin/env python3
"""
Plot gym load data for the last 96 hours.
Reads CSV files from data/ directory and generates a chart.
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = Path(__file__).parent / "gym_load_chart.png"
THRESHOLD = 140
HOURS_TO_SHOW = 96


def load_data(hours: int = HOURS_TO_SHOW) -> tuple[list[datetime], list[int]]:
    """Load data from CSV files for the last N hours."""
    cutoff = datetime.now() - timedelta(hours=hours)

    timestamps = []
    counts = []

    # Get list of CSV files sorted by date
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    for csv_path in csv_files:
        # Parse date from filename
        try:
            file_date = datetime.strptime(csv_path.stem, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Skip files older than our cutoff date
        if file_date < cutoff.date() - timedelta(days=1):
            continue

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    time_str = row["time"]
                    count = int(row["count"])

                    # Parse full datetime
                    dt = datetime.strptime(f"{file_date} {time_str}", "%Y-%m-%d %H:%M")

                    # Only include data within our time window
                    if dt >= cutoff:
                        timestamps.append(dt)
                        counts.append(count)
                except (ValueError, KeyError):
                    continue

    return timestamps, counts


def plot_chart(timestamps: list[datetime], counts: list[int]) -> None:
    """Generate and save the chart."""
    if not timestamps:
        print("No data to plot")
        return

    fig, ax = plt.subplots(figsize=(14, 6))

    # Create colors based on threshold
    colors = ["#e74c3c" if c >= THRESHOLD else "#2ecc71" for c in counts]

    # Plot the data
    ax.bar(timestamps, counts, width=0.005, color=colors, alpha=0.8)

    # Add threshold line
    ax.axhline(y=THRESHOLD, color="#f39c12", linestyle="--", linewidth=2, label=f"Threshold ({THRESHOLD})")

    # Formatting
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("People in Gym", fontsize=12)
    ax.set_title(f"SportLife Gym Load (Last {HOURS_TO_SHOW} Hours)", fontsize=14, fontweight="bold")

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    plt.xticks(rotation=45, ha="right")

    # Add grid
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_axisbelow(True)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2ecc71", label="Below threshold"),
        Patch(facecolor="#e74c3c", label="Above threshold"),
        plt.Line2D([0], [0], color="#f39c12", linestyle="--", linewidth=2, label=f"Threshold ({THRESHOLD})"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    # Add stats
    if counts:
        avg = sum(counts) / len(counts)
        min_c = min(counts)
        max_c = max(counts)
        stats_text = f"Min: {min_c}  |  Max: {max_c}  |  Avg: {avg:.0f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150)
    plt.close()

    print(f"Chart saved to: {OUTPUT_FILE}")
    print(f"Data points: {len(counts)}")
    if counts:
        print(f"Time range: {timestamps[0]} to {timestamps[-1]}")


def main():
    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")
        print("Run fetch_gym_data.py first to collect data.")
        return

    timestamps, counts = load_data()
    plot_chart(timestamps, counts)


if __name__ == "__main__":
    main()
