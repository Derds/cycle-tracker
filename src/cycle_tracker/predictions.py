"""
Phase detection and prediction logic.
"""

from datetime import datetime, timedelta
from typing import Tuple, Optional
from data_manager import Cycle
from statistics import (
    calculate_average_period_length,
    calculate_average_cycle_length,
    calculate_cycle_statistics,
    get_valid_cycles
)


def get_current_phase(cycles, today=None) -> Tuple[Optional[str], str]:
    """
    Determine current cycle phase for a given date.
    
    Returns: (phase_name, description) or (None, message)
    """
    if today is None:
        today = datetime.now().date()
    
    if not cycles:
        return None, "No cycle data. Use 'cycle-tracker start' to begin tracking."
    
    # Find which cycle this date belongs to
    target_cycle = None
    for cycle in cycles:
        if cycle.start_date > today:
            continue
            
        # Check if date falls within this cycle
        if cycle.is_complete:
            # Completed cycle: check if before end date
            if today <= cycle.end_date:
                target_cycle = cycle
                break
        else:
            # Ongoing cycle: it's the latest one, use it
            target_cycle = cycle
            break
    
    if not target_cycle:
        # Date is before first recorded cycle
        return None, "Date is before first recorded cycle."
    
    # If we're past the end of a completed cycle, check if new one is due
    if target_cycle.is_complete and target_cycle.end_date < today:
        return None, check_cycle_due(today, cycles)
    
    days_since_start = (today - target_cycle.start_date).days
    
    # Determine phase
    avg_period = calculate_average_period_length(cycles)
    period_days = target_cycle.period_length or avg_period
    
    if days_since_start < period_days:
        # Determine if we should show actual or estimated
        if target_cycle.period_length:
            day_label = f"Day {days_since_start + 1} of menstrual phase (typically {period_days} days)"
        else:
            day_label = f"Day {days_since_start + 1} of menstrual phase (avg {period_days} days)"
        return 'menstrual', day_label
    
    if days_since_start < 14:
        return 'follicular', f"Day {days_since_start + 1} of cycle"
    
    return 'luteal', f"Day {days_since_start + 1} of cycle"


def check_cycle_due(today, cycles) -> str:
    """Check if a new cycle is due, overdue, or early"""
    if not cycles:
        return "No previous cycles recorded."
    
    last_cycle = cycles[-1]
    
    # Calculate expected next cycle start
    if not last_cycle.is_complete:
        avg_length = calculate_average_cycle_length(cycles[:-1], exclude_outliers=True)
        expected_end = last_cycle.start_date + timedelta(days=avg_length - 1)
    else:
        expected_end = last_cycle.end_date
    
    expected_start = expected_end + timedelta(days=1)
    days_diff = (today - expected_start).days
    
    if days_diff < -2:
        return f"Next cycle expected in {abs(days_diff)} days (around {expected_start.strftime('%Y-%m-%d')})"
    
    if days_diff <= 2:
        return f"Next cycle is due (expected around {expected_start.strftime('%Y-%m-%d')})"
    
    return f"Next cycle is {days_diff} days overdue (expected {expected_start.strftime('%Y-%m-%d')})"


def predict_phase_on_date(cycles, target_date) -> Tuple[Optional[str], str]:
    """Predict what phase will occur on a specific date"""
    if not cycles:
        return None, "No cycle data available."
    
    current_cycle = cycles[-1]
    today = datetime.now().date()
    
    # If target is in the past or today, use actual data
    if target_date <= today:
        return get_current_phase(cycles, target_date)
    
    # Get averages for predictions
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    if not valid_cycles:
        return None, "Need at least 1 valid cycle for future predictions."
    
    mean_cycle, _ = calculate_cycle_statistics(cycles, exclude_outliers=True)
    avg_period = calculate_average_period_length(cycles)
    
    # If target is within current ongoing cycle
    if not current_cycle.is_complete and target_date >= current_cycle.start_date:
        days_into_cycle = (target_date - current_cycle.start_date).days
        expected_cycle_length = int(mean_cycle)
        
        # Check if target is still within this cycle
        if days_into_cycle < expected_cycle_length:
            return _determine_phase_in_cycle(days_into_cycle, avg_period, estimated=True)
    
    # For dates beyond current cycle, predict future cycles
    if current_cycle.is_complete:
        estimate_start = current_cycle.end_date + timedelta(days=1)
    else:
        estimate_start = current_cycle.start_date + timedelta(days=int(mean_cycle))
    
    # Step through cycles until we reach target
    while estimate_start + timedelta(days=int(mean_cycle)) <= target_date:
        estimate_start += timedelta(days=int(mean_cycle))
    
    days_into_cycle = (target_date - estimate_start).days
    
    if days_into_cycle < 0:
        # Target is between cycles (in the gap before next cycle starts)
        return None, f"Between cycles (next expected ~{estimate_start.strftime('%Y-%m-%d')})"
    
    return _determine_phase_in_cycle(days_into_cycle, avg_period, estimated=True, likely=True)


def _determine_phase_in_cycle(days_into_cycle: int, avg_period: int, estimated: bool = False, likely: bool = False) -> Tuple[str, str]:
    """
    Helper function to determine phase based on days into cycle.
    Decouples phase logic from prediction and display concerns.
    """
    prefix = "Likely day" if likely else "Day"
    suffix = " (estimated)" if estimated else ""
    
    if days_into_cycle < avg_period:
        return 'menstrual', f"{prefix} {days_into_cycle + 1} of menstrual phase{suffix}"
    
    if days_into_cycle < 14:
        return 'follicular', f"{prefix} {days_into_cycle + 1} of cycle{suffix}"
    
    return 'luteal', f"{prefix} {days_into_cycle + 1} of cycle{suffix}"
