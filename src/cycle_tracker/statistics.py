"""
Statistical calculations for cycle predictions.

All methods inspired by Urteaga et al. (2021-2022) research,
adapted for individual tracking.
"""

import math
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
from data_manager import Cycle, get_valid_cycles, DEFAULT_PERIOD_LENGTH, DEFAULT_CYCLE_LENGTH, DEFAULT_FOLLICULAR_PHASE_LENGTH


def calculate_average_period_length(cycles: List[Cycle]) -> int:
    """Calculate average period length from historical data"""
    periods_with_length = [c for c in cycles if c.period_length]
    
    if not periods_with_length:
        return DEFAULT_PERIOD_LENGTH
    
    return round(sum(c.period_length for c in periods_with_length) / len(periods_with_length))


def calculate_average_cycle_length(cycles: List[Cycle], exclude_outliers=True) -> int:
    """Calculate average cycle length from completed cycles"""
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=exclude_outliers)
    
    if not valid_cycles:
        return DEFAULT_CYCLE_LENGTH
    
    lengths = [c.cycle_length for c in valid_cycles]
    return round(sum(lengths) / len(lengths))


def calculate_cycle_statistics(cycles: List[Cycle], exclude_outliers=True) -> Tuple[float, float]:
    """
    Calculate cycle length mean and standard deviation.
    
    Returns: (mean, std_dev) for prediction ranges
    Outliers are excluded by default to improve accuracy.
    """
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=exclude_outliers)
    
    if not valid_cycles:
        return DEFAULT_CYCLE_LENGTH, 5.0
    
    lengths = [c.cycle_length for c in valid_cycles]
    
    if len(lengths) == 1:
        return lengths[0], 3.0
    
    mean = sum(lengths) / len(lengths)
    variance = sum((x - mean) ** 2 for x in lengths) / (len(lengths) - 1)
    std_dev = math.sqrt(variance)
    
    return round(mean, 1), round(std_dev, 1)


def calculate_tracking_quality(cycles: List[Cycle]) -> int:
    """
    Calculate tracking quality score (0-100).
    
    Based on tracking adherence modelling from Urteaga et al.
    High score = consistent tracking + sufficient data, low score = gaps/missed cycles/insufficient data
    
    Scoring:
    - 40 points: Data quantity (2-3 cycles=20pts, 4-5=30pts, 6+=40pts)
    - 40 points: Period end tracking (recording when bleeding stops)
    - 10 points: No outlier cycles
    - 10 points: No large gaps (missed periods)
    """
    if len(cycles) < 2:
        return 0
    
    # Data quantity score (0-40 points)
    # More data = more reliable predictions
    completed_cycles = [c for c in cycles if c.is_complete]
    total_cycles = len(cycles)
    
    if total_cycles <= 3:
        data_score = 20  # Minimal data
    elif total_cycles <= 5:
        data_score = 30  # Moderate data
    else:
        data_score = 40  # Good data
    
    # Period end tracking score (0-40 points)
    # Only count completed cycles (current ongoing cycle doesn't count against you)
    if completed_cycles:
        tracked_periods = sum(1 for c in completed_cycles if c.period_end_date)
        tracking_rate = tracked_periods / len(completed_cycles)
    else:
        # Only one ongoing cycle = perfect so far
        tracking_rate = 1.0 if cycles[0].period_end_date else 0.0
    
    tracking_score = tracking_rate * 40
    
    # Penalty for outliers (likely data errors or missed tracking) (0-10 points)
    outlier_count = sum(1 for c in cycles if c.is_outlier)
    outlier_penalty = (outlier_count / len(cycles)) * 10
    
    # Penalty for very large gaps (>2x average = likely missed a period) (0-10 points)
    gap_penalties = 0
    avg_length = calculate_average_cycle_length(cycles, exclude_outliers=True)
    
    for i in range(len(cycles) - 1):
        gap = (cycles[i + 1].start_date - cycles[i].start_date).days
        # Only penalise gaps >2x average (e.g., >56 days for 28-day average)
        # This indicates a likely missed period, not normal variation
        if gap > avg_length * 2.0:
            gap_penalties += 1
    
    if len(cycles) > 1:
        gap_penalty = (gap_penalties / (len(cycles) - 1)) * 10
    else:
        gap_penalty = 0
    
    # Final score: data + tracking - penalties
    score = data_score + tracking_score - outlier_penalty - gap_penalty
    return max(0, min(100, round(score)))


def calculate_luteal_phase_stats(cycles: List[Cycle]) -> Tuple[int, float]:
    """
    Calculate luteal phase statistics.
    
    The luteal phase is typically more stable than overall cycle length.
    
    NOTE: This calculation uses DEFAULT_FOLLICULAR_PHASE_LENGTH (14 days) as an
    estimate for ovulation. Without symptom tracking (BBT, cervical mucus, LH tests),
    we cannot determine exact ovulation timing, so we use the statistical average.
    This may be less accurate for individuals with shorter/longer follicular phases.
    """
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    
    if len(valid_cycles) < 2:
        return 14, 1.0
    
    luteal_lengths = []
    for cycle in valid_cycles:
        # Estimate: ovulation at DEFAULT_FOLLICULAR_PHASE_LENGTH days from start
        # LIMITATION: Without symptom tracking, this is an approximation
        estimated_luteal = min(cycle.cycle_length - DEFAULT_FOLLICULAR_PHASE_LENGTH, 16)
        if estimated_luteal > 10:
            luteal_lengths.append(estimated_luteal)
    
    if not luteal_lengths:
        return 14, 1.0
    
    mean = sum(luteal_lengths) / len(luteal_lengths)
    
    if len(luteal_lengths) == 1:
        return round(mean), 1.0
    
    variance = sum((x - mean) ** 2 for x in luteal_lengths) / (len(luteal_lengths) - 1)
    std_dev = math.sqrt(variance)
    
    return round(mean), round(std_dev, 1)


def predict_next_cycle_date(cycles: List[Cycle]) -> Tuple[datetime.date, datetime.date, datetime.date]:
    """
    Predict next cycle start with confidence interval.
    
    Returns: (earliest, expected, latest) dates
    """
    if not cycles:
        return None, None, None
    
    last_cycle = cycles[-1]
    mean, std_dev = calculate_cycle_statistics(cycles, exclude_outliers=True)
    
    # Estimate when current cycle will end
    if last_cycle.is_complete:
        expected_start = last_cycle.end_date + timedelta(days=1)
    else:
        expected_start = last_cycle.start_date + timedelta(days=int(mean))
    
    # 68% confidence interval (±1 std dev)
    earliest = expected_start - timedelta(days=int(std_dev))
    latest = expected_start + timedelta(days=int(std_dev))
    
    return earliest, expected_start, latest


def get_daily_updated_prediction(current_cycle: Cycle, historical_cycles: List[Cycle], days_elapsed: int) -> Dict:
    """
    Update cycle end prediction daily as cycle progresses.
    
    Sequential prediction approach: predictions become more accurate over time.
    
    NOTE: The confidence calculation here is simplified and not statistically rigorous.
    TODO: Implement proper confidence intervals based on sample size and variance.
    The current implementation (50% + progress_factor * 40) is a heuristic that should
    be replaced with proper statistical confidence calculations (e.g., t-distribution
    for small samples, accounting for prediction uncertainty).
    """
    mean, std_dev = calculate_cycle_statistics(historical_cycles, exclude_outliers=True)
    
    expected_total_length = mean
    days_remaining = max(0, expected_total_length - days_elapsed)
    
    # Confidence increases as cycle progresses (50% → 90%)
    # FIXME: This is a heuristic approximation, not a true confidence interval
    progress_factor = min(days_elapsed / expected_total_length, 1.0)
    
    # Narrow prediction range as we progress
    adjusted_std = std_dev * (1 - progress_factor * 0.5)
    
    expected_end = current_cycle.start_date + timedelta(days=int(expected_total_length))
    earliest_end = expected_end - timedelta(days=int(adjusted_std))
    latest_end = expected_end + timedelta(days=int(adjusted_std))
    
    return {
        'days_remaining': int(days_remaining),
        'expected_end': expected_end,
        'earliest_end': earliest_end,
        'latest_end': latest_end,
        'confidence': int(50 + progress_factor * 40),  # Heuristic, not statistical
        'std_dev': adjusted_std
    }
