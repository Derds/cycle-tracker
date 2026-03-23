#!/usr/bin/env python3
"""
Graphing functionality for cycle tracker - visualise historical trends.
Uses ASCII art for terminal-based graphs (no matplotlib required).
"""

from typing import List, Tuple
from datetime import date
from data_manager import Cycle
from statistics import calculate_cycle_statistics, calculate_average_period_length


def create_ascii_graph(
    data_points: List[Tuple[date, int]], 
    title: str, 
    y_label: str,
    width: int = 60,
    height: int = 15
) -> str:
    """
    Create an ASCII graph of data over time.
    
    Args:
        data_points: List of (date, value) tuples
        title: Graph title
        y_label: Label for Y-axis
        width: Graph width in characters
        height: Graph height in lines
    
    Returns:
        ASCII art graph as string
    """
    if not data_points:
        return f"No data to graph for {title}"
    
    # Sort by date
    data_points = sorted(data_points, key=lambda x: x[0])
    
    dates = [d[0] for d in data_points]
    values = [d[1] for d in data_points]
    
    min_val = min(values)
    max_val = max(values)
    
    # Add some padding to the range
    range_val = max_val - min_val
    if range_val == 0:
        range_val = 1
    padding = max(1, range_val * 0.1)
    min_val -= padding
    max_val += padding
    
    # Calculate trend line (simple linear regression)
    n = len(values)
    x_vals = list(range(n))
    
    mean_x = sum(x_vals) / n
    mean_y = sum(values) / n
    
    numerator = sum((x_vals[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    denominator = sum((x - mean_x) ** 2 for x in x_vals)
    
    if denominator != 0:
        slope = numerator / denominator
        intercept = mean_y - slope * mean_x
    else:
        slope = 0
        intercept = mean_y
    
    # Build the graph
    graph = []
    graph.append("╭" + "─" * (width + 8) + "╮")
    graph.append(f"│ {title:^{width + 6}} │")
    graph.append("├" + "─" * (width + 8) + "┤")
    
    # Y-axis and plot area
    for row in range(height):
        # Y value for this row (top to bottom = high to low)
        y_val = max_val - (row / (height - 1)) * (max_val - min_val)
        
        # Y-axis label
        y_label_str = f"{int(y_val):3d}"
        line = f"│ {y_label_str} │ "
        
        # Plot each column
        for col in range(width):
            # Map column to data point
            if n == 1:
                data_idx = 0
            else:
                data_idx = int((col / (width - 1)) * (n - 1))
            
            actual_val = values[data_idx]
            trend_val = slope * data_idx + intercept
            
            # Determine what to plot
            # Check if actual data point is at this position
            actual_y_pos = height - 1 - int(((actual_val - min_val) / (max_val - min_val)) * (height - 1))
            trend_y_pos = height - 1 - int(((trend_val - min_val) / (max_val - min_val)) * (height - 1))
            
            if row == actual_y_pos:
                # Show actual data point
                line += "●"
            elif row == trend_y_pos:
                # Show trend line
                line += "─"
            else:
                line += " "
        
        line += " │"
        graph.append(line)
    
    # X-axis
    graph.append("├" + "─" * 5 + "┼" + "─" * width + "┤")
    
    # X-axis labels (dates)
    if n >= 3:
        first_date = dates[0].strftime("%b %y")
        mid_date = dates[n // 2].strftime("%b %y")
        last_date = dates[-1].strftime("%b %y")
        
        # Build label line more carefully
        label_line = "│" + " " * 6
        
        # Add first date
        label_line += first_date
        
        # Calculate where mid and last dates should go
        mid_target = 6 + width // 2 - len(mid_date) // 2
        last_target = 6 + width - len(last_date)
        
        # Fill spaces and add labels
        current_pos = 6 + len(first_date)
        
        # Fill to mid position
        while current_pos < mid_target:
            label_line += " "
            current_pos += 1
        
        # Add mid date if we're at the right position
        if current_pos == mid_target:
            label_line += mid_date
            current_pos += len(mid_date)
        
        # Fill to last position
        while current_pos < last_target:
            label_line += " "
            current_pos += 1
        
        # Add last date
        if current_pos == last_target:
            label_line += last_date
            current_pos += len(last_date)
        
        # Pad to end
        while current_pos < 6 + width:
            label_line += " "
            current_pos += 1
        
        label_line += " │"
    else:
        # Not enough data for multiple labels
        first_date = dates[0].strftime("%b %y")
        label_line = f"│      {first_date}" + " " * (width - len(first_date)) + " │"
    
    graph.append(label_line)
    graph.append("╰" + "─" * (width + 8) + "╯")
    
    # Add legend
    graph.append("")
    graph.append(f"  ● Data points     ─ Trend line")
    graph.append(f"  {y_label}: {min(values)}-{max(values)} days (avg: {sum(values)/len(values):.1f})")
    
    # Trend interpretation
    if abs(slope) < 0.01:
        trend_text = "stable"
    elif slope > 0:
        trend_text = f"increasing (↗ +{slope:.2f} days per cycle)"
    else:
        trend_text = f"decreasing (↘ {slope:.2f} days per cycle)"
    graph.append(f"  Trend: {trend_text}")
    
    return "\n".join(graph)


def graph_cycle_history(cycles: List[Cycle]) -> str:
    """
    Create graphs showing cycle length and period length trends.
    
    Args:
        cycles: List of Cycle objects
    
    Returns:
        Multi-line string with graphs
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
    
    # Graph 1: Cycle Length over time
    cycle_data = [(c.start_date, c.cycle_length) for c in complete_cycles]
    cycle_graph = create_ascii_graph(
        cycle_data,
        "Cycle Length Over Time",
        "Days",
        width=55,
        height=12
    )
    output.append(cycle_graph)
    output.append("")
    output.append("")
    
    # Graph 2: Period (Menstrual Phase) Length over time
    period_cycles = [c for c in complete_cycles if c.period_length is not None]
    
    if period_cycles:
        period_data = [(c.start_date, c.period_length) for c in period_cycles]
        period_graph = create_ascii_graph(
            period_data,
            "Menstrual Phase Length Over Time",
            "Days",
            width=55,
            height=12
        )
        output.append(period_graph)
        output.append("")
    else:
        output.append("Track period end dates to see menstrual phase trends!")
        output.append("Use: cycle-tracker end-period")
        output.append("")
    
    # Summary statistics
    mean_cycle, std_cycle = calculate_cycle_statistics(complete_cycles, exclude_outliers=True)
    avg_period = calculate_average_period_length(cycles)
    
    output.append("=" * 70)
    output.append("SUMMARY STATISTICS")
    output.append("=" * 70)
    output.append(f"  Total cycles tracked: {len(cycles)}")
    output.append(f"  Complete cycles: {len(complete_cycles)}")
    output.append(f"  Average cycle length: {mean_cycle:.1f} ± {std_cycle:.1f} days")
    output.append(f"  Average period length: {avg_period} days")
    
    if len(cycles) != len(complete_cycles):
        output.append(f"  Excluded from graphs: {len(cycles) - len(complete_cycles)} (ongoing or outliers)")
    
    output.append("=" * 70)
    
    return "\n".join(output)


if __name__ == "__main__":
    # For testing
    from data_manager import load_cycles
    cycles = load_cycles()
    print(graph_cycle_history(cycles))
