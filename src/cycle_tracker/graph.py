#!/usr/bin/env python3
"""
Graphing functionality for cycle tracker - visualise historical trends.
Uses ASCII art for terminal-based graphs (no matplotlib required).
"""

from typing import List, Tuple
from datetime import date
from data_manager import Cycle
from statistics import calculate_cycle_statistics, calculate_average_period_length


def create_ascii_bar_chart(
    data_points: List[Tuple[date, int]], 
    title: str, 
    y_label: str,
    height: int = 12
) -> str:
    """
    Create an ASCII bar chart of data over time.
    
    Args:
        data_points: List of (date, value) tuples
        title: Chart title
        y_label: Label for Y-axis
        height: Chart height in lines
    
    Returns:
        ASCII art bar chart as string
    """
    if not data_points:
        return f"No data to chart for {title}"
    
    # Sort by date
    data_points = sorted(data_points, key=lambda x: x[0])
    
    dates = [d[0] for d in data_points]
    values = [d[1] for d in data_points]
    
    n = len(values)
    min_val = min(values)
    max_val = max(values)
    
    # Calculate statistics
    mean_val = sum(values) / n
    
    # Calculate trend line (simple linear regression)
    x_vals = list(range(n))
    mean_x = sum(x_vals) / n
    
    numerator = sum((x_vals[i] - mean_x) * (values[i] - mean_val) for i in range(n))
    denominator = sum((x - mean_x) ** 2 for x in x_vals)
    
    if denominator != 0:
        slope = numerator / denominator
    else:
        slope = 0
    
    # Calculate bar width based on number of data points
    # Leave space between bars
    bar_width = 3 if n <= 15 else (2 if n <= 25 else 1)
    spacing = 1
    total_width = n * (bar_width + spacing) + 10
    
    # Build the chart
    chart = []
    chart.append("╭" + "─" * total_width + "╮")
    chart.append(f"│ {title:^{total_width - 2}} │")
    chart.append("├" + "─" * total_width + "┤")
    
    # Y-axis range
    range_val = max_val - min_val
    if range_val == 0:
        range_val = 1
    
    # Get unique values that appear in the data for Y-axis
    unique_values = sorted(set(values), reverse=True)
    
    # Draw bars from top to bottom
    for row in range(height):
        # Y value for this row (top to bottom = high to low)
        y_threshold = max_val - (row / (height - 1)) * range_val
        
        # Y-axis label (show actual data values, not interpolated)
        # Only show label if this row corresponds to an actual value
        y_label_str = "   "
        for val in unique_values:
            if abs(y_threshold - val) < (range_val / height / 2):  # Close enough to this value
                y_label_str = f"{val:3d}"
                break
        
        line = f"│ {y_label_str} │ "
        
        # Draw bars
        for i, val in enumerate(values):
            # Check if bar reaches this height
            if val >= y_threshold:
                line += "█" * bar_width
            else:
                line += " " * bar_width
            
            # Add spacing between bars
            if i < n - 1:
                line += " " * spacing
        
        line += " │"
        chart.append(line)
    
    # X-axis
    chart.append("├" + "─" * 5 + "┴" + "─" * (total_width - 6) + "┤")
    
    # Date labels on bottom - show month abbreviations
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    label_line = "│     │ "
    for i, dt in enumerate(dates):
        month_str = month_names[dt.month - 1]
        # Center month within bar width
        label_line += month_str.center(bar_width)
        if i < n - 1:
            label_line += " " * spacing
    label_line += " │"
    chart.append(label_line)
    
    chart.append("╰" + "─" * total_width + "╯")
    
    return "\n".join(chart)


def graph_cycle_history(cycles: List[Cycle]) -> str:
    """
    Create bar charts showing cycle length and period length trends.
    
    Args:
        cycles: List of Cycle objects
    
    Returns:
        Multi-line string with bar charts and statistics
    """
    if not cycles:
        return "No cycle data to graph. Start tracking with 'cycle-tracker start'."
    
    # Filter to complete cycles only (need both start and end)
    complete_cycles = [c for c in cycles if c.is_complete and not c.is_outlier]
    
    if not complete_cycles:
        return "No complete cycles to graph yet. Keep tracking!"
    
    output = []
    output.append("=" * 70)
    output.append("CYCLE TRACKER - HISTORICAL TRENDS")
    output.append("=" * 70)
    output.append("")
    
    # Chart 1: Cycle Length over time
    cycle_data = [(c.start_date, c.cycle_length) for c in complete_cycles]
    values = [d[1] for d in cycle_data]
    
    cycle_chart = create_ascii_bar_chart(
        cycle_data,
        "Cycle Length Over Time",
        "Days",
        height=10
    )
    output.append(cycle_chart)
    output.append("")
    
    # Statistics for cycle length
    mean_cycle = sum(values) / len(values)
    min_cycle = min(values)
    max_cycle = max(values)
    
    # Calculate trend
    n = len(values)
    x_vals = list(range(n))
    mean_x = sum(x_vals) / n
    numerator = sum((x_vals[i] - mean_x) * (values[i] - mean_cycle) for i in range(n))
    denominator = sum((x - mean_x) ** 2 for x in x_vals)
    slope = numerator / denominator if denominator != 0 else 0
    
    output.append(f"  Average: {mean_cycle:.1f} days  |  Range: {min_cycle}-{max_cycle} days")
    
    if abs(slope) < 0.01:
        trend_text = "Trend: Stable ═"
    elif slope > 0:
        trend_text = f"Trend: Increasing ↗ (+{slope:.2f} days per cycle)"
    else:
        trend_text = f"Trend: Decreasing ↘ ({slope:.2f} days per cycle)"
    output.append(f"  {trend_text}")
    output.append("")
    output.append("")
    
    # Chart 2: Period (Menstrual Phase) Length over time
    period_cycles = [c for c in complete_cycles if c.period_length is not None]
    
    if period_cycles:
        period_data = [(c.start_date, c.period_length) for c in period_cycles]
        period_values = [d[1] for d in period_data]
        
        # Statistics for period length
        mean_period = sum(period_values) / len(period_values)
        min_period = min(period_values)
        max_period = max(period_values)
        
        # Calculate trend
        n_period = len(period_values)
        x_vals_period = list(range(n_period))
        mean_x_period = sum(x_vals_period) / n_period
        numerator_period = sum((x_vals_period[i] - mean_x_period) * (period_values[i] - mean_period) for i in range(n_period))
        denominator_period = sum((x - mean_x_period) ** 2 for x in x_vals_period)
        slope_period = numerator_period / denominator_period if denominator_period != 0 else 0
        
        # Check if data is variable enough to warrant a chart
        # Show chart if range > 1 day OR there's a meaningful trend
        range_period = max_period - min_period
        is_variable = range_period > 1 or abs(slope_period) >= 0.06
        
        if is_variable:
            # Show the chart for variable data
            period_chart = create_ascii_bar_chart(
                period_data,
                "Menstrual Phase Length Over Time",
                "Days",
                height=10
            )
            output.append(period_chart)
            output.append("")
        
        # Always show statistics
        output.append("MENSTRUAL PHASE LENGTH:")
        output.append(f"  Average: {mean_period:.1f} days  |  Range: {min_period}-{max_period} days")
        
        if abs(slope_period) < 0.01:
            trend_text_period = "Trend: Stable ═"
        elif slope_period > 0:
            trend_text_period = f"Trend: Increasing ↗ (+{slope_period:.2f} days per cycle)"
        else:
            trend_text_period = f"Trend: Decreasing ↘ ({slope_period:.2f} days per cycle)"
        output.append(f"  {trend_text_period}")
        
        if not is_variable:
            output.append(f"  (Chart hidden - data is consistent)")
        
        output.append("")
    else:
        output.append("Track period end dates to see menstrual phase statistics!")
        output.append("Use: cycle-tracker end-period")
        output.append("")
    
    # Summary statistics
    mean_cycle_stat, std_cycle = calculate_cycle_statistics(complete_cycles, exclude_outliers=True)
    avg_period = calculate_average_period_length(cycles)
    
    output.append("=" * 70)
    output.append("SUMMARY")
    output.append("=" * 70)
    output.append(f"  Total cycles tracked: {len(cycles)}")
    output.append(f"  Complete cycles: {len(complete_cycles)}")
    output.append(f"  Average cycle length: {mean_cycle_stat:.1f} ± {std_cycle:.1f} days")
    output.append(f"  Average period length: {avg_period} days")
    
    if len(cycles) != len(complete_cycles):
        output.append(f"  Excluded from charts: {len(cycles) - len(complete_cycles)} (ongoing or outliers)")
    
    output.append("=" * 70)
    
    return "\n".join(output)


if __name__ == "__main__":
    # For testing
    from data_manager import load_cycles
    cycles = load_cycles()
    print(graph_cycle_history(cycles))
