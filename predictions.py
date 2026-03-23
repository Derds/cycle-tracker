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
    Determine current cycle phase.
    
    Returns: (phase_name, description) or (None, message)
    """
    if today is None:
        today = datetime.now().date()
    
    if not cycles:
        return None, "No cycle data. Use 'cycle-tracker start' to begin tracking."
    
    current_cycle = cycles[-1]
    
    # If cycle has ended, check if new one is due
    if current_cycle.is_complete and current_cycle.end_date < today:
        return None, check_cycle_due(today, cycles)
    
    days_since_start = (today - current_cycle.start_date).days
    
    # Determine phase
    avg_period = calculate_average_period_length(cycles)
    period_days = current_cycle.period_length or avg_period
    
    if days_since_start < period_days:
        return 'menstrual', f"Day {days_since_start + 1} of menstrual phase (typically {period_days} days)"
    elif days_since_start < 14:
        return 'follicular', f"Day {days_since_start + 1} of cycle"
    else:
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
    elif days_diff <= 2:
        return f"Next cycle is due (expected around {expected_start.strftime('%Y-%m-%d')})"
    else:
        return f"Next cycle is {days_diff} days overdue (expected {expected_start.strftime('%Y-%m-%d')})"


def predict_phase_on_date(cycles, target_date) -> Tuple[Optional[str], str]:
    """Predict what phase will occur on a specific date"""
    if not cycles:
        return None, "No cycle data available."
    
    current_cycle = cycles[-1]
    today = datetime.now().date()
    
    # If target is today or during current cycle, use actual data
    if target_date <= today:
        return get_current_phase(cycles, target_date)
    
    if not current_cycle.is_complete and target_date > current_cycle.start_date:
        days_into_cycle = (target_date - current_cycle.start_date).days
        avg_period = calculate_average_period_length(cycles)
        
        if days_into_cycle < avg_period:
            return 'menstrual', f"Day {days_into_cycle + 1} of menstrual phase (estimated)"
        elif days_into_cycle < 14:
            return 'follicular', f"Day {days_into_cycle + 1} of cycle (estimated)"
        else:
            return 'luteal', f"Day {days_into_cycle + 1} of cycle (estimated)"
    
    # For future predictions
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    if not valid_cycles:
        return None, "Need at least 1 valid cycle for future predictions."
    
    mean_cycle, _ = calculate_cycle_statistics(cycles, exclude_outliers=True)
    
    # Estimate which cycle the target falls into
    if current_cycle.is_complete:
        estimate_start = current_cycle.end_date + timedelta(days=1)
    else:
        estimate_start = current_cycle.start_date + timedelta(days=int(mean_cycle))
    
    # Step through cycles until we reach target
    while estimate_start + timedelta(days=int(mean_cycle)) < target_date:
        estimate_start += timedelta(days=int(mean_cycle))
    
    days_into_cycle = (target_date - estimate_start).days
    avg_period = calculate_average_period_length(cycles)
    
    if days_into_cycle < 0:
        return None, f"Between cycles (next expected ~{estimate_start.strftime('%Y-%m-%d')})"
    elif days_into_cycle < avg_period:
        return 'menstrual', f"Likely day {days_into_cycle + 1} of menstrual phase (estimated)"
    elif days_into_cycle < 14:
        return 'follicular', f"Likely day {days_into_cycle + 1} of cycle (estimated)"
    else:
        return 'luteal', f"Likely day {days_into_cycle + 1} of cycle (estimated)"
