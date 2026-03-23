#!/usr/bin/env python3
"""
Cycle Tracker - A menstrual cycle phase tracking tool
"""

import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".cycle_tracker_data.csv"
DEFAULT_MENSTRUAL_DAYS = 5
DEFAULT_CYCLE_LENGTH = 28

PHASE_VISUALS = {
    'menstrual': '◯',      # Empty circle
    'follicular': '◔',     # Quarter filled
    'luteal': '◕',         # Three-quarters filled
    'complete': '●'        # Full circle
}

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
                'menstrual_days': int(row['menstrual_days'])
            })
    return cycles

def save_cycle(start_date, end_date=None, menstrual_days=DEFAULT_MENSTRUAL_DAYS):
    """Save a new cycle to CSV file"""
    file_exists = DATA_FILE.exists()
    
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'menstrual_days'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
            'menstrual_days': menstrual_days
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
        writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'menstrual_days'])
        writer.writeheader()
        for cycle in cycles:
            writer.writerow({
                'start_date': cycle['start_date'].strftime('%Y-%m-%d'),
                'end_date': cycle['end_date'].strftime('%Y-%m-%d') if cycle['end_date'] else '',
                'menstrual_days': cycle['menstrual_days']
            })

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
    """Show current cycle status and phase"""
    today = datetime.now().date()
    cycles = load_cycles()
    
    if not cycles:
        print("No cycle data. Use 'cycle-tracker start' to begin tracking.")
        return
    
    phase, info = get_current_phase(today)
    
    if phase:
        visual = PHASE_VISUALS.get(phase, '')
        print(f"{visual}  Current phase: {phase}")
        print(info)
        
        # Show when menstrual phase will end
        current_cycle = cycles[-1]
        avg_menstrual_days = calculate_average_menstrual_days(cycles)
        menstrual_days = current_cycle.get('menstrual_days', avg_menstrual_days)
        menstrual_end = current_cycle['start_date'] + timedelta(days=menstrual_days - 1)
        
        if today <= menstrual_end:
            days_left = (menstrual_end - today).days
            if days_left == 0:
                print(f"Menstrual phase ends today ({menstrual_end.strftime('%Y-%m-%d')})")
            else:
                print(f"Menstrual phase will end in {days_left} day(s) ({menstrual_end.strftime('%Y-%m-%d')})")
    else:
        print(info)

def main():
    if len(sys.argv) < 2:
        command = "cycle-phase"
    else:
        command = sys.argv[1]
    
    if command == "start":
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
    
    elif command == "status":
        show_status()
    
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
        print("  cycle-tracker start [menstrual_days]  - Start a new cycle")
        print("  cycle-tracker end                     - End current cycle")
        print("  cycle-tracker cycle-phase             - Get current phase (menstrual/follicular/luteal)")
        print("  cycle-tracker status                  - Show detailed status")
        print("")
        print("Default command (no arguments): cycle-phase")

if __name__ == "__main__":
    main()
