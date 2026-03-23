"""
Display and formatting functions for cycle tracker output.
"""

import calendar as cal
from datetime import datetime, timedelta
from typing import List
from data_manager import Cycle
from predictions import predict_phase_on_date
from statistics import (
    calculate_average_period_length,
    calculate_cycle_statistics,
    calculate_tracking_quality,
    calculate_luteal_phase_stats,
    get_daily_updated_prediction,
    get_valid_cycles
)

# Phase visual indicators
PHASE_VISUALS = {
    'menstrual': '◯',
    'follicular': '◔',
    'luteal': '◕',
    'complete': '●'
}


def print_box(lines: List[str]):
    """Print text in a bordered box"""
    if not lines:
        return
    
    max_width = max(len(line) for line in lines)
    border_width = max_width + 4
    
    print("╭" + "─" * border_width + "╮")
    for line in lines:
        padding = max_width - len(line)
        print(f"│  {line}{' ' * padding}  │")
    print("╰" + "─" * border_width + "╯")


def show_status(cycles: List[Cycle]):
    """Show current cycle status with detailed statistics"""
    today = datetime.now().date()
    
    if not cycles:
        print("No cycle data. Use 'cycle-tracker start' to begin tracking.")
        return
    
    from predictions import get_current_phase
    phase, info = get_current_phase(cycles, today)
    
    if not phase:
        print(info)
        return
    
    current_cycle = cycles[-1]
    days_elapsed = (today - current_cycle.start_date).days
    visual = PHASE_VISUALS.get(phase, '')
    
    lines = [
        f"{visual}  Current Phase: {phase.upper()}",
        "",
        info
    ]
    
    # Period end information
    avg_period = calculate_average_period_length(cycles)
    period_days = current_cycle.period_length or avg_period
    
    if current_cycle.period_end_date:
        lines.append(f"Period: {current_cycle.period_length} days (ended {current_cycle.period_end_date.strftime('%Y-%m-%d')})")
    else:
        period_end_estimate = current_cycle.start_date + timedelta(days=period_days - 1)
        if today <= period_end_estimate:
            days_left = (period_end_estimate - today).days
            if days_left == 0:
                lines.append(f"Period expected to end today ({period_end_estimate.strftime('%Y-%m-%d')})")
            else:
                lines.append(f"Period expected to end in {days_left} day(s) ({period_end_estimate.strftime('%Y-%m-%d')})")
    
    # Statistics (if enough data)
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    if len(valid_cycles) >= 2:
        lines.append("")
        
        mean, std_dev = calculate_cycle_statistics(cycles, exclude_outliers=True)
        lines.append(f"Cycle length: {mean:.0f} ± {std_dev:.1f} days (avg ± variation)")
        
        # Daily updated prediction
        prediction = get_daily_updated_prediction(current_cycle, valid_cycles, days_elapsed)
        
        if prediction['days_remaining'] > 0:
            earliest = prediction['earliest_end'].strftime('%b %d')
            latest = prediction['latest_end'].strftime('%b %d')
            lines.append(f"Expected cycle end: {earliest} - {latest} ({prediction['confidence']}% confidence)")
        
        # Quality score
        quality = calculate_tracking_quality(cycles)
        quality_emoji = "🟢" if quality >= 80 else "🟡" if quality >= 60 else "🔴"
        lines.append(f"Tracking quality: {quality_emoji} {quality}/100")
        
        # Outlier warning
        outliers = [c for c in cycles if c.is_outlier]
        if outliers:
            lines.append(f"⚠️  {len(outliers)} outlier cycle(s) excluded from stats")
        
        # Luteal phase
        if len(valid_cycles) >= 3:
            luteal_mean, luteal_std = calculate_luteal_phase_stats(cycles)
            lines.append(f"Luteal phase: ~{luteal_mean} days (stable)")
    
    print_box(lines)


def show_calendar_view(cycles: List[Cycle], month_offset=0):
    """Show ASCII calendar for a specific month with phase predictions"""
    today = datetime.now().date()
    target_month = today.month + month_offset
    target_year = today.year
    
    # Handle year overflow
    while target_month > 12:
        target_month -= 12
        target_year += 1
    while target_month < 1:
        target_month += 12
        target_year -= 1
    
    month_cal = cal.monthcalendar(target_year, target_month)
    month_name = cal.month_name[target_month]
    
    print(f"\n╭{'─' * 56}╮")
    print(f"│  {month_name} {target_year} - Cycle Calendar{' ' * (56 - len(f'{month_name} {target_year} - Cycle Calendar') - 2)}│")
    print(f"├{'─' * 56}┤")
    print("│  Mon  Tue  Wed  Thu  Fri  Sat  Sun                  │")
    print(f"├{'─' * 56}┤")
    
    for week in month_cal:
        line = "│  "
        for day in week:
            if day == 0:
                line += "     "
            else:
                date = datetime(target_year, target_month, day).date()
                phase, _ = predict_phase_on_date(cycles, date)
                
                if phase:
                    emoji = PHASE_VISUALS.get(phase, ' ')
                    line += f"{emoji}{day:2d}  "
                else:
                    line += f" {day:2d}  "
        
        line += " " * (55 - len(line) + 2) + "│"
        print(line)
    
    print(f"╰{'─' * 56}╯")
    print("\nLegend: ◯ Menstrual  ◔ Follicular  ◕ Luteal")
    
    # Show outlier warning if any
    outliers = [c for c in cycles if c.is_outlier]
    if outliers:
        print(f"Note: {len(outliers)} outlier cycle(s) excluded from predictions")
    else:
        print("Note: Future dates are estimates based on average cycle length")
    print()


def show_prediction(cycles: List[Cycle]):
    """Show next cycle prediction with confidence ranges"""
    if not cycles:
        print("No cycle data available. Start tracking to see predictions.")
        return
    
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    
    if len(valid_cycles) < 2:
        print("Need at least 2 valid cycles for predictions.")
        if len(cycles) - len(valid_cycles) > 0:
            print(f"({len(cycles) - len(valid_cycles)} outlier cycles excluded)")
        return
    
    from statistics import predict_next_cycle_date
    earliest, expected, latest = predict_next_cycle_date(cycles)
    mean, std_dev = calculate_cycle_statistics(cycles, exclude_outliers=True)
    quality = calculate_tracking_quality(cycles)
    
    lines = [
        "📅 Next Cycle Prediction",
        "",
        f"Expected start: {expected.strftime('%Y-%m-%d')}",
        f"Likely range: {earliest.strftime('%b %d')} - {latest.strftime('%b %d')}",
        f"Confidence: 68% (±1 std dev)",
        "",
        f"Based on {len(valid_cycles)} valid cycles:",
        f"  Average length: {mean:.1f} days",
        f"  Variation: ±{std_dev:.1f} days",
        f"  Tracking quality: {quality}/100"
    ]
    
    # Outlier info
    outliers = [c for c in cycles if c.is_outlier]
    if outliers:
        lines.append(f"  ({len(outliers)} outlier(s) excluded)")
    
    # Luteal phase
    if len(valid_cycles) >= 3:
        luteal_mean, luteal_std = calculate_luteal_phase_stats(cycles)
        lines.extend([
            "",
            f"Luteal phase: {luteal_mean} ± {luteal_std:.1f} days",
            "(Luteal phase is typically more stable)"
        ])
    
    print_box(lines)
