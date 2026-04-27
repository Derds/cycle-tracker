#!/usr/bin/env python3
"""
Cycle Tracker - Main CLI Interface

A privacy-first menstrual cycle tracker with statistical predictions.

Statistical methods inspired by research from:
Urteaga et al. (2021-2022) - Menstrual cycle prediction with self-tracking data
https://github.com/iurteaga/menstrual_cycle_analysis

Key concepts adapted for individual use:
- Variance-based prediction ranges
- Tracking quality assessment
- Sequential prediction updates  
- Phase-specific pattern recognition
- Outlier detection and handling
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src/cycle_tracker to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from data_manager import (
    setup_data_file,
    load_cycles,
    add_cycle,
    update_period_end,
    edit_cycle,
    DEFAULT_PERIOD_LENGTH
)
from statistics import (
    calculate_average_period_length,
    calculate_cycle_statistics,
    get_valid_cycles
)
from predictions import get_current_phase, predict_phase_on_date
from display import (
    show_status,
    show_calendar_view,
    show_prediction,
    PHASE_VISUALS
)
from graph import graph_cycle_history


def parse_date(date_str: str):
    """Parse a date string in several common formats. Returns a date object."""
    for fmt in ['%Y-%m-%d', '%d %B %Y', '%d %b %Y', '%B %d %Y', '%b %d %Y']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Could not parse date '{date_str}'. Try: 2026-04-20, 20 Apr 2026, Apr 20 2026")


def print_help():
    """Print comprehensive help text"""
    print("╭────────────────────────────────────────────────────────╮")
    print("│  CYCLE TRACKER - Help & Usage Guide                   │")
    print("╰────────────────────────────────────────────────────────╯\n")
    
    print("━━━ Basic Commands ━━━\n")
    print("  cycle-tracker setup")
    print("    Initialize data file (first time only)\n")
    
    print("  cycle-tracker start [period_length] [--date DATE]")
    print("    Start a new cycle when your period begins")
    print("    Automatically ends previous cycle")
    print("    Optional: Specify expected period length in days")
    print("    Optional: --date DATE to log a past cycle start\n")
    
    print("  cycle-tracker edit [N] [--start DATE] [--end DATE] [--period-end DATE]")
    print("    Edit a recent cycle (N=1 last, N=2 second-to-last; default N=1)")
    print("    Any combination of fields can be updated in one command")
    print("    Recalculates period length when start/period-end changes")
    print("    Example: cycle-tracker edit --period-end 2026-04-26")
    print("    Example: cycle-tracker edit 2 --start 2026-03-21\n")

    print("  cycle-tracker end-period")
    print("    Mark when bleeding stops (recommended)")
    print("    Tracks actual period length for better predictions\n")
    
    print("  cycle-tracker")
    print("  cycle-tracker cycle-phase")
    print("    Get current phase: menstrual, follicular, or luteal\n")
    
    print("  cycle-tracker status")
    print("    Detailed view with statistics and predictions\n")
    
    print("  cycle-tracker predict")
    print("    Predict next cycle with confidence ranges\n")
    
    print("  cycle-tracker on <date>")
    print("    Predict phase on a future date")
    print("    Formats: '2026-05-09', '9 May 2026', 'May 9 2026'\n")
    
    print("  cycle-tracker calendar [+N]")
    print("    Show calendar view (N months ahead)")
    print("    Example: 'cycle-tracker calendar 1' (next month)\n")
    
    print("  cycle-tracker graph")
    print("    Visualise historical trends with ASCII graphs")
    print("    Shows cycle length and period length over time\n")
    
    print("━━━ Key Concepts ━━━\n")
    print("  Period vs Cycle:")
    print("    • Period = bleeding (typically 4-7 days)")
    print("    • Cycle = first day of period to day before next period")
    print("    • Full cycle typically 21-35 days\n")
    
    print("  Outliers:")
    print("    • Cycles <18 or >45 days excluded from statistics")
    print("    • Prevents data errors from skewing predictions")
    print("    • Improves accuracy of averages\n")
    
    print("━━━ Understanding Output ━━━\n")
    print("  Phases:")
    print("    ◯ Menstrual (bleeding)")
    print("    ◔ Follicular (post-period, pre-ovulation)")
    print("    ◕ Luteal (post-ovulation, pre-period)\n")
    
    print("  Statistics:")
    print("    '27 ± 0.8' = average 27 days, varies by ±0.8")
    print("    '68% confidence' = ±1 standard deviation range")
    print("    Quality: 🟢 80+ / 🟡 60-79 / 🔴 <60\n")
    
    print("━━━ Limitations ━━━\n")
    print("  Phase Boundaries:")
    print("    The follicular/luteal boundary (ovulation) is estimated at")
    print("    day 14 of the cycle (statistical average). For personalization,")
    print("    symptom tracking (BBT, LH tests, cervical mucus) would be needed.")
    print("    This can be made user-configurable in future versions.\n")
    
    print("  Confidence Intervals:")
    print("    Current confidence values are heuristic approximations.")
    print("    Proper statistical confidence intervals (t-distribution for")
    print("    small samples) are planned for future implementation.\n")
    
    print("For more info: README.md, CITATIONS.md")
    print("")


def main():
    """Main CLI entry point"""
    command = sys.argv[1] if len(sys.argv) > 1 else "cycle-phase"
    
    try:
        if command == "setup":
            setup_data_file()
        
        elif command == "start":
            period_length = None
            start_date = datetime.now().date()

            # Parse optional positional period_length and --date flag
            extra_args = sys.argv[2:]
            i = 0
            while i < len(extra_args):
                if extra_args[i] == '--date':
                    if i + 1 >= len(extra_args):
                        print("Error: --date requires a date value")
                        sys.exit(1)
                    start_date = parse_date(extra_args[i + 1])
                    i += 2
                else:
                    try:
                        period_length = int(extra_args[i])
                        if period_length < 1 or period_length > 15:
                            print("Error: Period length must be between 1-15 days")
                            sys.exit(1)
                    except ValueError:
                        print("Error: Period length must be a number")
                        sys.exit(1)
                    i += 1
            
            cycles = load_cycles()
            
            # Show previous cycle info if auto-completing
            if cycles and not cycles[-1].is_complete:
                prev_start = cycles[-1].start_date
                prev_length = (start_date - prev_start).days
                print(f"Previous cycle from {prev_start.strftime('%Y-%m-%d')} automatically completed.")
                print(f"That cycle was {prev_length} days long.\n")
            
            # Add new cycle
            if period_length is None:
                period_length = calculate_average_period_length(cycles) if cycles else DEFAULT_PERIOD_LENGTH
            
            new_cycle = add_cycle(start_date, period_length=period_length)
            print(f"New cycle started on {new_cycle.start_date.strftime('%Y-%m-%d')}")
            print(f"Expected period length: ~{period_length} days")
            print(f"Ends around: {(new_cycle.start_date + timedelta(days=period_length-1)).strftime('%Y-%m-%d')}")
            print("\nRemember: 'cycle-tracker end-period' when bleeding stops!")
        
        elif command == "end-period":
            today = datetime.now().date()
            period_length = update_period_end(today)
            # Success message printed by update_period_end
        
        elif command == "edit":
            # Usage: edit [N] [--start DATE] [--end DATE] [--period-end DATE]
            # N=1 (default) = last cycle, N=2 = second-to-last
            extra_args = sys.argv[2:]
            n = 1
            start_date = None
            end_date = None
            period_end_date = None

            i = 0
            if extra_args and extra_args[0].isdigit():
                n = int(extra_args[0])
                i = 1

            while i < len(extra_args):
                flag = extra_args[i]
                if flag in ('--start', '--end', '--period-end'):
                    if i + 1 >= len(extra_args):
                        print(f"Error: {flag} requires a date value")
                        sys.exit(1)
                    date_val = parse_date(extra_args[i + 1])
                    if flag == '--start':
                        start_date = date_val
                    elif flag == '--end':
                        end_date = date_val
                    else:
                        period_end_date = date_val
                    i += 2
                else:
                    print(f"Error: Unknown option '{flag}'")
                    print("Usage: cycle-tracker edit [N] [--start DATE] [--end DATE] [--period-end DATE]")
                    sys.exit(1)

            if not any([start_date, end_date, period_end_date]):
                print("Error: Nothing to update. Provide at least one of: --start, --end, --period-end")
                print("Usage: cycle-tracker edit [N] [--start DATE] [--end DATE] [--period-end DATE]")
                sys.exit(1)

            cycle = edit_cycle(n, start_date=start_date, end_date=end_date, period_end_date=period_end_date)
            label = "Last" if n == 1 else f"Cycle -{n}"
            print(f"✓ {label} cycle updated:")
            print(f"  Start:      {cycle.start_date.strftime('%Y-%m-%d')}")
            if cycle.end_date:
                print(f"  End:        {cycle.end_date.strftime('%Y-%m-%d')}")
            if cycle.period_end_date:
                print(f"  Period end: {cycle.period_end_date.strftime('%Y-%m-%d')} ({cycle.period_length} days)")

        elif command == "status":
            cycles = load_cycles()
            show_status(cycles)
        
        elif command == "predict":
            cycles = load_cycles()
            show_prediction(cycles)
        
        elif command == "on":
            if len(sys.argv) < 3:
                print("Error: Please specify a date")
                print("Examples: cycle-tracker on 2026-05-09")
                print("          cycle-tracker on 9 May 2026")
                sys.exit(1)
            
            date_str = ' '.join(sys.argv[2:])
            try:
                target_date = parse_date(date_str)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            
            cycles = load_cycles()
            phase, info = predict_phase_on_date(cycles, target_date)
            
            if phase:
                visual = PHASE_VISUALS.get(phase, '')
                print(f"\nOn {target_date.strftime('%A, %d %B %Y')}:")
                print(f"  {visual} {phase.upper()}")
                print(f"  {info}\n")
            else:
                print(f"\nOn {target_date.strftime('%A, %d %B %Y')}:")
                print(f"  {info}\n")
        
        elif command == "calendar":
            month_offset = 0
            if len(sys.argv) > 2:
                try:
                    month_offset = int(sys.argv[2])
                except ValueError:
                    print("Error: Month offset must be a number")
                    sys.exit(1)
            
            cycles = load_cycles()
            show_calendar_view(cycles, month_offset)
        
        elif command == "graph":
            cycles = load_cycles()
            graph = graph_cycle_history(cycles)
            print(graph)
        
        elif command == "cycle-phase":
            cycles = load_cycles()
            phase, info = get_current_phase(cycles)
            if phase:
                visual = PHASE_VISUALS.get(phase, '')
                print(f"{visual} {phase}")
            else:
                print("No active cycle")
                print(info)
        
        elif command in ["help", "--help", "-h"]:
            print_help()
        
        else:
            print("Cycle Tracker - Quick Help\n")
            print("Commands:")
            print("  start [len] [--date D] - Start new cycle (auto-ends previous)")
            print("  edit [N] [--start D] [--end D] [--period-end D]")
            print("                         - Edit last (N=1) or recent cycle")
            print("  end-period     - Mark when bleeding stops")
            print("  status         - Show detailed stats")
            print("  predict        - Predict next cycle")
            print("  on <date>      - Predict phase on date")
            print("  calendar [+N]  - Show calendar (N months ahead)")
            print("  graph          - View historical trends")
            print("  help           - Full documentation")
            print()
            print("Run 'cycle-tracker help' for details")
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Run 'cycle-tracker help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
