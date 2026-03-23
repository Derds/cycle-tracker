#!/usr/bin/env python3
"""
Cycle Tracker - A menstrual cycle phase tracking tool

Statistical methods inspired by research from:
Urteaga et al. (2021-2022) - Menstrual cycle prediction with self-tracking data
https://github.com/iurteaga/menstrual_cycle_analysis

Key concepts adapted for individual use:
- Variance-based prediction ranges
- Tracking quality assessment  
- Sequential prediction updates
- Phase-specific pattern recognition
"""

import csv
import sys
import math
from datetime import datetime, timedelta
from pathlib import Path

# Get the directory where the script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_FILE = SCRIPT_DIR / ".cycle_tracker_data.csv"
DEFAULT_MENSTRUAL_DAYS = 5
DEFAULT_CYCLE_LENGTH = 28

PHASE_VISUALS = {
    'menstrual': '◯',      # Empty circle
    'follicular': '◔',     # Quarter filled
    'luteal': '◕',         # Three-quarters filled
    'complete': '●'        # Full circle
}

def print_box(lines):
    """Print text in a nice box"""
    if not lines:
        return
    
    max_width = max(len(line) for line in lines)
    border_width = max_width + 4
    
    print("╭" + "─" * border_width + "╮")
    for line in lines:
        padding = max_width - len(line)
        print(f"│  {line}{' ' * padding}  │")
    print("╰" + "─" * border_width + "╯")

def setup_data_file():
    """Initialize the data file if it doesn't exist"""
    if not DATA_FILE.exists():
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'menstrual_days', 'period_end_date'])
            writer.writeheader()
        print(f"✓ Data file created at: {DATA_FILE}")
        return True
    else:
        print(f"✓ Data file already exists at: {DATA_FILE}")
        return False

def load_cycles():
    """Load cycle data from CSV file"""
    if not DATA_FILE.exists():
        return []
    
    cycles = []
    with open(DATA_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cycles.append({
                'start_date': datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                'end_date': datetime.strptime(row['end_date'], '%Y-%m-%d').date() if row['end_date'] else None,
                'menstrual_days': int(row['menstrual_days']),
                'period_end_date': datetime.strptime(row['period_end_date'], '%Y-%m-%d').date() if row.get('period_end_date') else None
            })
    return cycles

def save_cycle(start_date, end_date=None, menstrual_days=DEFAULT_MENSTRUAL_DAYS, period_end_date=None):
    """Save a new cycle to CSV file"""
    file_exists = DATA_FILE.exists()
    
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'menstrual_days', 'period_end_date'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
            'menstrual_days': menstrual_days,
            'period_end_date': period_end_date.strftime('%Y-%m-%d') if period_end_date else ''
        })

def update_last_cycle_end(end_date):
    """Update the end date of the most recent cycle"""
    cycles = load_cycles()
    if not cycles:
        print("Error: No cycles to update")
        return
    
    cycles[-1]['end_date'] = end_date
    
    # Rewrite the entire file
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'menstrual_days', 'period_end_date'])
        writer.writeheader()
        for cycle in cycles:
            writer.writerow({
                'start_date': cycle['start_date'].strftime('%Y-%m-%d'),
                'end_date': cycle['end_date'].strftime('%Y-%m-%d') if cycle['end_date'] else '',
                'menstrual_days': cycle['menstrual_days'],
                'period_end_date': cycle.get('period_end_date').strftime('%Y-%m-%d') if cycle.get('period_end_date') else ''
            })

def update_period_end(period_end_date):
    """Update when the period (bleeding) ended"""
    cycles = load_cycles()
    if not cycles:
        print("Error: No cycles to update")
        return
    
    if cycles[-1]['end_date']:
        print("Error: Cycle already ended. Cannot update period end date.")
        return
    
    cycles[-1]['period_end_date'] = period_end_date
    
    # Calculate actual period length
    period_length = (period_end_date - cycles[-1]['start_date']).days + 1
    
    # Rewrite the entire file
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'menstrual_days', 'period_end_date'])
        writer.writeheader()
        for cycle in cycles:
            writer.writerow({
                'start_date': cycle['start_date'].strftime('%Y-%m-%d'),
                'end_date': cycle['end_date'].strftime('%Y-%m-%d') if cycle['end_date'] else '',
                'menstrual_days': cycle['menstrual_days'],
                'period_end_date': cycle.get('period_end_date').strftime('%Y-%m-%d') if cycle.get('period_end_date') else ''
            })
    
    print(f"Period ended on {period_end_date.strftime('%Y-%m-%d')}")
    print(f"Period length: {period_length} days")

def calculate_average_menstrual_days(cycles):
    """Calculate average menstrual phase length from historical data"""
    if len(cycles) < 2:
        return DEFAULT_MENSTRUAL_DAYS
    
    total = sum(c['menstrual_days'] for c in cycles[:-1])
    return round(total / len(cycles[:-1]))

def calculate_average_cycle_length(cycles):
    """Calculate average cycle length from completed cycles"""
    completed_cycles = [c for c in cycles if c['end_date']]
    if not completed_cycles:
        return DEFAULT_CYCLE_LENGTH
    
    lengths = [(c['end_date'] - c['start_date']).days for c in completed_cycles]
    return round(sum(lengths) / len(lengths))

def calculate_cycle_statistics(cycles):
    """
    Calculate cycle length statistics including variance.
    
    Returns: (mean, std_dev) for better prediction ranges
    Inspired by variance modeling in Urteaga et al. research
    """
    completed_cycles = [c for c in cycles if c['end_date']]
    if not completed_cycles:
        return DEFAULT_CYCLE_LENGTH, 5.0
    
    lengths = [(c['end_date'] - c['start_date']).days for c in completed_cycles]
    
    if len(lengths) == 1:
        return lengths[0], 3.0  # Default std dev for single cycle
    
    mean = sum(lengths) / len(lengths)
    variance = sum((x - mean) ** 2 for x in lengths) / (len(lengths) - 1)
    std_dev = math.sqrt(variance)
    
    return round(mean, 1), round(std_dev, 1)

def calculate_tracking_quality(cycles):
    """
    Calculate tracking quality score (0-100).
    
    Based on: tracking adherence modeling from Urteaga et al.
    High score = consistent tracking, low score = gaps/missed cycles
    """
    if not cycles:
        return 0
    
    # Count completed cycles
    completed = sum(1 for c in cycles if c['end_date'])
    completion_rate = completed / len(cycles)
    
    # Check for gaps between cycles
    gap_penalties = 0
    if len(cycles) > 1:
        avg_length = calculate_average_cycle_length(cycles)
        for i in range(len(cycles) - 1):
            if cycles[i]['end_date']:
                gap = (cycles[i + 1]['start_date'] - cycles[i]['end_date']).days
                # Penalize large gaps (possible missed cycles)
                if gap > avg_length * 0.5:  # More than 50% of cycle length
                    gap_penalties += 1
        
        gap_penalty = (gap_penalties / (len(cycles) - 1)) * 30
    else:
        gap_penalty = 0
    
    # Score: 70% completion rate, 30% gap penalty
    score = (completion_rate * 70) - gap_penalty
    return max(0, min(100, round(score)))

def calculate_luteal_phase_stats(cycles):
    """
    Calculate luteal phase statistics.
    
    The luteal phase (ovulation to next period) is more stable than overall cycle.
    Research shows it varies by only 1-2 days for most individuals.
    
    We estimate ovulation at day 14 (standard) or work backwards from cycle end.
    """
    completed_cycles = [c for c in cycles if c['end_date']]
    if len(completed_cycles) < 2:
        return 14, 1.0  # Default luteal length and std dev
    
    luteal_lengths = []
    for cycle in completed_cycles:
        cycle_length = (cycle['end_date'] - cycle['start_date']).days
        # Estimate: ovulation ~14 days from start, luteal = remainder
        # Or: work backwards assuming 14-day luteal (more accurate)
        estimated_luteal = min(cycle_length - 14, 16)  # Cap at 16 days
        if estimated_luteal > 10:  # Only count reasonable estimates
            luteal_lengths.append(estimated_luteal)
    
    if not luteal_lengths:
        return 14, 1.0
    
    mean = sum(luteal_lengths) / len(luteal_lengths)
    
    if len(luteal_lengths) == 1:
        return round(mean), 1.0
    
    variance = sum((x - mean) ** 2 for x in luteal_lengths) / (len(luteal_lengths) - 1)
    std_dev = math.sqrt(variance)
    
    return round(mean), round(std_dev, 1)

def predict_next_cycle_with_confidence(cycles, last_cycle_end):
    """
    Predict next cycle start with confidence interval.
    
    Returns prediction range based on cycle variance.
    Uses 68% confidence interval (±1 standard deviation).
    """
    mean, std_dev = calculate_cycle_statistics(cycles)
    
    expected_start = last_cycle_end + timedelta(days=1)
    
    # 68% confidence interval
    earliest = expected_start + timedelta(days=int(-std_dev))
    latest = expected_start + timedelta(days=int(std_dev))
    
    return {
        'expected': expected_start,
        'earliest': earliest,
        'latest': latest,
        'confidence': 68,
        'mean_cycle': mean,
        'std_dev': std_dev
    }

def get_daily_updated_prediction(current_cycle_start, historical_cycles, days_elapsed):
    """
    Update cycle end prediction daily as the cycle progresses.
    
    Sequential prediction approach from Urteaga et al.:
    Predictions become more accurate as we get closer to cycle end.
    """
    mean, std_dev = calculate_cycle_statistics(historical_cycles)
    
    # Expected days remaining
    expected_total_length = mean
    days_remaining = max(0, expected_total_length - days_elapsed)
    
    # Confidence increases as cycle progresses
    # At day 1: low confidence, at day 28: high confidence
    progress_factor = min(days_elapsed / expected_total_length, 1.0)
    
    # Narrow the prediction range as we progress
    adjusted_std = std_dev * (1 - progress_factor * 0.5)
    
    expected_end = current_cycle_start + timedelta(days=int(expected_total_length))
    earliest_end = expected_end - timedelta(days=int(adjusted_std))
    latest_end = expected_end + timedelta(days=int(adjusted_std))
    
    return {
        'days_remaining': int(days_remaining),
        'expected_end': expected_end,
        'earliest_end': earliest_end,
        'latest_end': latest_end,
        'confidence': int(50 + progress_factor * 40),  # 50-90%
        'adjusted_std': round(adjusted_std, 1)
    }

def get_current_phase(today=None):
    """Determine current cycle phase"""
    if today is None:
        today = datetime.now().date()
    
    cycles = load_cycles()
    if not cycles:
        return None, "No cycle data. Use 'cycle-tracker start' to begin tracking."
    
    current_cycle = cycles[-1]
    
    # If current cycle has ended, user needs to start a new one
    if current_cycle['end_date'] and current_cycle['end_date'] < today:
        return None, check_cycle_due(today, cycles)
    
    days_since_start = (today - current_cycle['start_date']).days
    
    # Determine phase based on days since cycle start
    avg_menstrual_days = calculate_average_menstrual_days(cycles)
    menstrual_days = current_cycle.get('menstrual_days', avg_menstrual_days)
    
    if days_since_start < menstrual_days:
        return 'menstrual', f"Day {days_since_start + 1} of menstrual phase (typically {menstrual_days} days)"
    elif days_since_start < 14:
        return 'follicular', f"Day {days_since_start + 1} of cycle"
    else:
        return 'luteal', f"Day {days_since_start + 1} of cycle"

def check_cycle_due(today, cycles):
    """Check if a new cycle is due, overdue, or early"""
    if not cycles:
        return "No previous cycles recorded."
    
    last_cycle = cycles[-1]
    
    # If last cycle doesn't have end date, estimate it
    if not last_cycle['end_date']:
        avg_cycle_length = calculate_average_cycle_length(cycles[:-1])
        expected_end = last_cycle['start_date'] + timedelta(days=avg_cycle_length)
    else:
        avg_cycle_length = calculate_average_cycle_length(cycles)
        expected_end = last_cycle['end_date']
    
    expected_start = expected_end + timedelta(days=1)
    days_diff = (today - expected_start).days
    
    if days_diff < -2:
        return f"Next cycle expected in {abs(days_diff)} days (around {expected_start.strftime('%Y-%m-%d')})"
    elif days_diff <= 2:
        return f"Next cycle is due (expected around {expected_start.strftime('%Y-%m-%d')})"
    else:
        return f"Next cycle is {days_diff} days overdue (expected {expected_start.strftime('%Y-%m-%d')})"

def start_cycle(menstrual_days=None):
    """Start a new cycle"""
    today = datetime.now().date()
    cycles = load_cycles()
    
    # Check if there's an ongoing cycle
    if cycles and not cycles[-1]['end_date']:
        print(f"Warning: Current cycle started on {cycles[-1]['start_date'].strftime('%Y-%m-%d')} is not ended.")
        print("Automatically ending previous cycle.")
        update_last_cycle_end(today - timedelta(days=1))
    
    if menstrual_days is None:
        menstrual_days = calculate_average_menstrual_days(cycles) if cycles else DEFAULT_MENSTRUAL_DAYS
    
    save_cycle(today, menstrual_days=menstrual_days)
    print(f"New cycle started on {today.strftime('%Y-%m-%d')}")
    print(f"Menstrual phase: {menstrual_days} days (ends around {(today + timedelta(days=menstrual_days-1)).strftime('%Y-%m-%d')})")

def end_cycle():
    """End the current cycle"""
    today = datetime.now().date()
    cycles = load_cycles()
    
    if not cycles:
        print("Error: No cycle to end. Start a cycle first.")
        return
    
    if cycles[-1]['end_date']:
        print(f"Error: Current cycle already ended on {cycles[-1]['end_date'].strftime('%Y-%m-%d')}")
        return
    
    update_last_cycle_end(today)
    cycle_length = (today - cycles[-1]['start_date']).days
    print(f"Cycle ended on {today.strftime('%Y-%m-%d')}")
    print(f"Cycle length: {cycle_length} days")

def show_status():
    """Show current cycle status and phase with statistical predictions"""
    today = datetime.now().date()
    cycles = load_cycles()
    
    if not cycles:
        print("No cycle data. Use 'cycle-tracker start' to begin tracking.")
        return
    
    phase, info = get_current_phase(today)
    
    if phase:
        visual = PHASE_VISUALS.get(phase, '')
        current_cycle = cycles[-1]
        days_elapsed = (today - current_cycle['start_date']).days
        
        lines = [
            f"{visual}  Current Phase: {phase.upper()}",
            "",
            info
        ]
        
        # Menstrual phase info
        avg_menstrual_days = calculate_average_menstrual_days(cycles)
        menstrual_days = current_cycle.get('menstrual_days', avg_menstrual_days)
        menstrual_end = current_cycle['start_date'] + timedelta(days=menstrual_days - 1)
        
        if today <= menstrual_end:
            days_left = (menstrual_end - today).days
            if days_left == 0:
                lines.append(f"Menstrual phase ends today ({menstrual_end.strftime('%Y-%m-%d')})")
            else:
                lines.append(f"Menstrual phase ends in {days_left} day(s) ({menstrual_end.strftime('%Y-%m-%d')})")
        
        # Show actual period length if recorded
        if current_cycle.get('period_end_date'):
            actual_period_length = (current_cycle['period_end_date'] - current_cycle['start_date']).days + 1
            lines.append(f"Period length: {actual_period_length} days (ended {current_cycle['period_end_date'].strftime('%Y-%m-%d')})")
        
        # Enhanced predictions with confidence intervals (if enough data)
        completed_cycles = [c for c in cycles if c['end_date']]
        if len(completed_cycles) >= 2:
            lines.append("")
            
            # Daily updated prediction
            prediction = get_daily_updated_prediction(current_cycle['start_date'], completed_cycles, days_elapsed)
            
            mean, std_dev = calculate_cycle_statistics(cycles)
            lines.append(f"Cycle length: {mean:.0f} ± {std_dev:.1f} days (avg ± variation)")
            
            if prediction['days_remaining'] > 0:
                earliest = prediction['earliest_end'].strftime('%b %d')
                latest = prediction['latest_end'].strftime('%b %d')
                lines.append(f"Expected end: {earliest} - {latest} ({prediction['confidence']}% confidence)")
            else:
                lines.append(f"Cycle may end soon (expected range passed)")
            
            # Tracking quality
            quality = calculate_tracking_quality(cycles)
            quality_emoji = "🟢" if quality >= 80 else "🟡" if quality >= 60 else "🔴"
            lines.append(f"Tracking quality: {quality_emoji} {quality}/100")
            
            # Luteal phase info (if enough data)
            if len(completed_cycles) >= 3:
                luteal_mean, luteal_std = calculate_luteal_phase_stats(cycles)
                lines.append(f"Your luteal phase: ~{luteal_mean} days (stable)")
        
        print_box(lines)
    else:
        print(info)

def main():
    if len(sys.argv) < 2:
        command = "cycle-phase"
    else:
        command = sys.argv[1]
    
    if command == "setup":
        setup_data_file()
    
    elif command == "start":
        menstrual_days = None
        if len(sys.argv) > 2:
            try:
                menstrual_days = int(sys.argv[2])
            except ValueError:
                print("Error: Menstrual days must be a number")
                sys.exit(1)
        start_cycle(menstrual_days)
    
    elif command == "end":
        end_cycle()
    
    elif command == "end-period":
        # Mark when bleeding stopped
        today = datetime.now().date()
        cycles = load_cycles()
        
        if not cycles:
            print("Error: No cycle to update. Start a cycle first.")
        elif cycles[-1]['end_date']:
            print("Error: Cycle already ended. Use this command during an active cycle.")
        elif cycles[-1].get('period_end_date'):
            print(f"Error: Period already marked as ended on {cycles[-1]['period_end_date'].strftime('%Y-%m-%d')}")
        else:
            update_period_end(today)
    
    elif command == "status":
        show_status()
    
    elif command == "predict":
        # Show prediction for next cycle
        cycles = load_cycles()
        if not cycles:
            print("No cycle data available. Start tracking to see predictions.")
        elif not cycles[-1]['end_date']:
            print("Current cycle is ongoing. Use 'status' to see current cycle predictions.")
        else:
            completed = [c for c in cycles if c['end_date']]
            if len(completed) < 2:
                print("Need at least 2 completed cycles for predictions.")
            else:
                prediction = predict_next_cycle_with_confidence(cycles, cycles[-1]['end_date'])
                mean, std_dev = calculate_cycle_statistics(cycles)
                quality = calculate_tracking_quality(cycles)
                
                lines = [
                    "📅 Next Cycle Prediction",
                    "",
                    f"Expected start: {prediction['expected'].strftime('%Y-%m-%d')}",
                    f"Likely range: {prediction['earliest'].strftime('%b %d')} - {prediction['latest'].strftime('%b %d')}",
                    f"Confidence: {prediction['confidence']}% (±1 std dev)",
                    "",
                    f"Based on {len(completed)} cycles:",
                    f"  Average length: {mean:.1f} days",
                    f"  Variation: ±{std_dev:.1f} days",
                    f"  Tracking quality: {quality}/100"
                ]
                
                # Add luteal phase info if enough data
                if len(completed) >= 3:
                    luteal_mean, luteal_std = calculate_luteal_phase_stats(cycles)
                    lines.extend([
                        "",
                        f"Your luteal phase: {luteal_mean} ± {luteal_std:.1f} days",
                        "(Luteal phase is typically more stable)"
                    ])
                
                print_box(lines)
    
    elif command == "cycle-phase":
        phase, info = get_current_phase()
        if phase:
            visual = PHASE_VISUALS.get(phase, '')
            print(f"{visual} {phase}")
        else:
            print("No active cycle")
            print(info)
    
    else:
        print("Cycle Tracker Usage:")
        print("  cycle-tracker setup                   - Initialize data file")
        print("  cycle-tracker start [menstrual_days]  - Start a new cycle")
        print("  cycle-tracker end-period              - Mark when period (bleeding) ends")
        print("  cycle-tracker end                     - End current cycle (when next period starts)")
        print("  cycle-tracker cycle-phase             - Get current phase (menstrual/follicular/luteal)")
        print("  cycle-tracker status                  - Show detailed status with predictions")
        print("  cycle-tracker predict                 - Predict next cycle with confidence ranges")
        print("")
        print("Default command (no arguments): cycle-phase")
        print("")
        print("Note: A full cycle = from first day of period to day before next period (21-35 days)")

if __name__ == "__main__":
    main()
