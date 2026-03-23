"""
Display and formatting functions for cycle tracker output.
"""

import calendar as cal
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from data_manager import Cycle
from predictions import predict_phase_on_date
from statistics import (
    calculate_average_period_length,
    calculate_cycle_statistics,
    calculate_tracking_quality,
    calculate_luteal_phase_stats,
    get_daily_updated_prediction,
    get_valid_cycles,
    DEFAULT_FOLLICULAR_PHASE_LENGTH
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
    if not cycles:
        print("No cycle data. Use 'cycle-tracker start' to begin tracking.")
        return
    
    status_data = _prepare_status_data(cycles)
    
    if not status_data:
        print(status_data.get('message', 'No status available'))
        return
    
    _render_status_box(status_data)


def _prepare_status_data(cycles: List[Cycle]) -> dict:
    """
    Prepare all data needed for status display.
    Decouples calculation logic from presentation.
    """
    today = datetime.now().date()
    
    from predictions import get_current_phase
    phase, info = get_current_phase(cycles, today)
    
    if not phase:
        return {'message': info}
    
    current_cycle = cycles[-1]
    days_elapsed = (today - current_cycle.start_date).days
    
    data = {
        'phase': phase,
        'phase_info': info,
        'visual': PHASE_VISUALS.get(phase, ''),
        'period_info': _calculate_period_info(current_cycle, cycles, today),
        'statistics': None
    }
    
    # Statistics (if enough data)
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    if len(valid_cycles) >= 2:
        data['statistics'] = _calculate_statistics(cycles, valid_cycles, current_cycle, days_elapsed)
    
    return data


def _calculate_period_info(current_cycle: Cycle, cycles: List[Cycle], today: datetime.date) -> Optional[str]:
    """
    Calculate period end information.
    Pure business logic - returns data dict instead of formatted string.
    """
    if current_cycle.period_end_date:
        return {
            'type': 'completed',
            'length': current_cycle.period_length,
            'end_date': current_cycle.period_end_date
        }
    
    avg_period = calculate_average_period_length(cycles)
    period_days = current_cycle.period_length or avg_period
    period_end_estimate = current_cycle.start_date + timedelta(days=period_days - 1)
    
    if today > period_end_estimate:
        return None
    
    days_left = (period_end_estimate - today).days
    
    return {
        'type': 'estimated',
        'days_left': days_left,
        'end_date': period_end_estimate
    }


def _calculate_statistics(cycles: List[Cycle], valid_cycles: List[Cycle], current_cycle: Cycle, days_elapsed: int) -> dict:
    """Calculate statistical data for display"""
    mean, std_dev = calculate_cycle_statistics(cycles, exclude_outliers=True)
    prediction = get_daily_updated_prediction(current_cycle, valid_cycles, days_elapsed)
    quality = calculate_tracking_quality(cycles)
    outliers = [c for c in cycles if c.is_outlier]
    
    stats = {
        'mean': mean,
        'std_dev': std_dev,
        'prediction': prediction if prediction['days_remaining'] > 0 else None,
        'quality': quality,
        'quality_level': _get_quality_level(quality),
        'outlier_count': len(outliers)
    }
    
    # Luteal phase
    if len(valid_cycles) >= 3:
        luteal_mean, luteal_std = calculate_luteal_phase_stats(cycles)
        stats['luteal'] = (luteal_mean, luteal_std)
    
    return stats


def _get_quality_level(quality: int) -> str:
    """Determine quality level indicator (business logic)"""
    if quality >= 80:
        return "🟢"
    if quality >= 60:
        return "🟡"
    return "🔴"


def _render_status_box(data: dict):
    """Render status data in formatted box"""
    lines = [
        f"{data['visual']}  Current Phase: {data['phase'].upper()}",
        "",
        data['phase_info']
    ]
    
    period_info = data.get('period_info')
    if period_info:
        if period_info['type'] == 'completed':
            lines.append(f"Period: {period_info['length']} days (ended {period_info['end_date'].strftime('%Y-%m-%d')})")
        elif period_info['type'] == 'estimated':
            if period_info['days_left'] == 0:
                lines.append(f"Period expected to end today ({period_info['end_date'].strftime('%Y-%m-%d')})")
            else:
                lines.append(f"Period expected to end in {period_info['days_left']} day(s) ({period_info['end_date'].strftime('%Y-%m-%d')})")
    
    stats = data.get('statistics')
    if not stats:
        print_box(lines)
        return
    
    lines.append("")
    lines.append(f"Cycle length: {stats['mean']:.0f} ± {stats['std_dev']:.1f} days (avg ± variation)")
    
    if stats['prediction']:
        pred = stats['prediction']
        earliest = pred['earliest_end'].strftime('%b %d')
        latest = pred['latest_end'].strftime('%b %d')
        
        lines.append(f"Expected cycle end: {earliest} - {latest} ({pred['confidence']}% confidence*)")
    
    lines.append(f"Tracking quality: {stats['quality_level']} {stats['quality']}/100")
    
    if stats['outlier_count'] > 0:
        lines.append(f"⚠️  {stats['outlier_count']} outlier cycle(s) excluded from stats")
    
    if stats.get('luteal'):
        luteal_mean, _ = stats['luteal']
        lines.append(f"Luteal phase: ~{luteal_mean} days (stable)")
    
    if stats['prediction']:
        lines.append("")
        lines.append("*Confidence is heuristic-based, not statistical")
    
    print_box(lines)


def show_calendar_view(cycles: List[Cycle], month_offset=0):
    """Show ASCII calendar for a specific month with phase predictions"""
    today = datetime.now().date()
    target_year, target_month = _calculate_target_month(today, month_offset)
    
    month_cal = cal.monthcalendar(target_year, target_month)
    month_name = cal.month_name[target_month]
    
    _render_calendar_header(month_name, target_year)
    _render_calendar_body(cycles, month_cal, target_year, target_month)
    _render_calendar_footer(cycles)


def _calculate_target_month(today: datetime.date, month_offset: int) -> Tuple[int, int]:
    """Calculate target year and month from offset"""
    target_month = today.month + month_offset
    target_year = today.year
    
    # Handle year overflow
    while target_month > 12:
        target_month -= 12
        target_year += 1
    while target_month < 1:
        target_month += 12
        target_year -= 1
    
    return target_year, target_month


def _render_calendar_header(month_name: str, target_year: int):
    """Render calendar header"""
    print(f"\n╭{'─' * 56}╮")
    print(f"│  {month_name} {target_year} - Cycle Calendar{' ' * (56 - len(f'{month_name} {target_year} - Cycle Calendar') - 2)}│")
    print(f"├{'─' * 56}┤")
    print("│  Mon  Tue  Wed  Thu  Fri  Sat  Sun                  │")
    print(f"├{'─' * 56}┤")


def _render_calendar_body(cycles: List[Cycle], month_cal, target_year: int, target_month: int):
    """Render calendar body with phase indicators"""
    for week in month_cal:
        line = "│  "
        for day in week:
            if day == 0:
                line += "     "
                continue
            
            date = datetime(target_year, target_month, day).date()
            day_display = _format_calendar_day(cycles, date, day)
            line += day_display
        
        line += " " * (55 - len(line) + 2) + "│"
        print(line)
    
    print(f"╰{'─' * 56}╯")


def _format_calendar_day(cycles: List[Cycle], date: datetime.date, day: int) -> str:
    """Format a single calendar day with phase indicator (business logic)"""
    phase, _ = predict_phase_on_date(cycles, date)
    
    if phase:
        emoji = PHASE_VISUALS.get(phase, ' ')
        return f"{emoji}{day:2d}  "
    
    return f" {day:2d}  "


def _render_calendar_footer(cycles: List[Cycle]):
    """Render calendar footer with legend and notes"""
    print("\nLegend: ◯ Menstrual  ◔ Follicular  ◕ Luteal")
    
    outlier_count = sum(1 for c in cycles if c.is_outlier)
    footer_note = _get_calendar_footer_note(outlier_count)
    print(footer_note)
    print()


def _get_calendar_footer_note(outlier_count: int) -> str:
    """Determine appropriate footer note (business logic)"""
    if outlier_count > 0:
        return f"Note: {outlier_count} outlier cycle(s) excluded from predictions"
    return "Note: Future dates are estimates based on average cycle length"


def show_prediction(cycles: List[Cycle]):
    """Show next cycle prediction with confidence ranges"""
    if not cycles:
        print("No cycle data available. Start tracking to see predictions.")
        return
    
    prediction_data = _prepare_prediction_data(cycles)
    
    if not prediction_data:
        return
    
    _render_prediction_box(prediction_data)


def _prepare_prediction_data(cycles: List[Cycle]) -> Optional[dict]:
    """
    Prepare all data needed for prediction display.
    Decouples calculation logic from presentation.
    """
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    
    if len(valid_cycles) < 2:
        print("Need at least 2 valid cycles for predictions.")
        if len(cycles) - len(valid_cycles) > 0:
            print(f"({len(cycles) - len(valid_cycles)} outlier cycles excluded)")
        return None
    
    from statistics import predict_next_cycle_date
    earliest, expected, latest = predict_next_cycle_date(cycles)
    mean, std_dev = calculate_cycle_statistics(cycles, exclude_outliers=True)
    quality = calculate_tracking_quality(cycles)
    outliers = [c for c in cycles if c.is_outlier]
    
    data = {
        'earliest': earliest,
        'expected': expected,
        'latest': latest,
        'mean': mean,
        'std_dev': std_dev,
        'quality': quality,
        'valid_count': len(valid_cycles),
        'outlier_count': len(outliers)
    }
    
    # Luteal phase
    if len(valid_cycles) >= 3:
        luteal_mean, luteal_std = calculate_luteal_phase_stats(cycles)
        data['luteal'] = (luteal_mean, luteal_std)
    
    return data


def _render_prediction_box(data: dict):
    """Render prediction data in formatted box"""
    lines = [
        "📅 Next Cycle Prediction",
        "",
        f"Expected start: {data['expected'].strftime('%Y-%m-%d')}",
        f"Likely range: {data['earliest'].strftime('%b %d')} - {data['latest'].strftime('%b %d')}",
        f"Confidence: 68% (±1 std dev)*",
        "",
        f"Based on {data['valid_count']} valid cycles:",
        f"  Average length: {data['mean']:.1f} days",
        f"  Variation: ±{data['std_dev']:.1f} days",
        f"  Tracking quality: {data['quality']}/100"
    ]
    
    if data['outlier_count'] > 0:
        lines.append(f"  ({data['outlier_count']} outlier(s) excluded)")
    
    if data.get('luteal'):
        luteal_mean, luteal_std = data['luteal']
        lines.extend([
            "",
            f"Luteal phase: {luteal_mean} ± {luteal_std:.1f} days",
            "(Luteal phase is typically more stable)"
        ])
    
    lines.extend([
        "",
        "*NOTE: Confidence intervals are approximate.",
        "For small sample sizes (<10 cycles), actual",
        "confidence may be lower than stated."
    ])
    
    print_box(lines)
