#!/usr/bin/env python3
"""
Combined Cycle & Moon Phase Tracker

Shows both menstrual cycle phase and moon phase in a single view.
Analyses correlations between cycle phases and moon phases over time.

This is an optional add-on - the main cycle tracker works independently.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add module directories to path
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR / "src" / "cycle_tracker"))
sys.path.insert(0, str(SCRIPT_DIR / "src" / "moon_tracker"))

# Import modular components
from data_manager import load_cycles
from predictions import get_current_phase
from statistics import get_valid_cycles, calculate_average_period_length
import moon_phase

def get_combined_visual():
    """Create a combined visual display of both cycles"""
    today = datetime.now().date()
    
    # Get cycle info
    cycles = load_cycles()
    if cycles:
        cycle_phase, cycle_info = get_current_phase(cycles, today)
        
        # Customize cycle_info to show actual average instead of "typically"
        from statistics import calculate_average_period_length
        avg_period = calculate_average_period_length(cycles)
        
        # Replace "typically X days" with actual average
        if "typically" in cycle_info and cycle_phase == 'menstrual':
            # Extract day number from cycle_info
            import re
            match = re.search(r'Day (\d+) of menstrual phase', cycle_info)
            if match:
                day_num = match.group(1)
                cycle_info = f"Day {day_num} of menstrual phase (avg {avg_period} days)"
    else:
        cycle_phase = None
        cycle_info = "No cycle data"
    
    # Get moon info
    moon_position = moon_phase.calculate_moon_phase()
    moon_key, moon_name = moon_phase.get_moon_phase_name(moon_position)
    moon_emoji = moon_phase.MOON_PHASES[moon_key]
    moon_illumination = moon_phase.calculate_illumination(moon_position)
    
    # Get cycle visual
    if cycle_phase:
        from display import PHASE_VISUALS
        cycle_emoji = PHASE_VISUALS.get(cycle_phase, '○')
        cycle_display = f"{cycle_emoji} {cycle_phase.upper()}"
    else:
        cycle_emoji = '○'
        cycle_display = "No active cycle"
    
    # Build display
    lines = [
        "╭────────────────────────────────────────────────────────╮",
        "│  🩸 CYCLE & MOON TRACKER 🌙                            │",
        "├────────────────────────────────────────────────────────┤",
        f"│  Menstrual Cycle: {cycle_display:38s} │",
    ]
    
    if cycle_phase:
        lines.append(f"│    {cycle_info:50s} │")
    else:
        lines.append(f"│    {cycle_info:50s} │")
    
    lines.extend([
        "│                                                        │",
        f"│  Moon Phase: {moon_emoji} {moon_name:38s} │",
        f"│    {moon_illumination:5.1f}% illuminated                                │",
        "╰────────────────────────────────────────────────────────╯"
    ])
    
    return '\n'.join(lines)

def analyse_cycle_moon_correlation():
    """
    Analyse correlation between cycle phases and moon phases.
    
    Shows which moon phases you're typically in during each cycle phase.
    """
    cycles = load_cycles()
    if not cycles or len(cycles) < 2:
        return None
    
    # Track which moon phases occur during which cycle phases
    correlations = {
        'menstrual': defaultdict(int),
        'follicular': defaultdict(int),
        'luteal': defaultdict(int)
    }
    
    total_days = {
        'menstrual': 0,
        'follicular': 0,
        'luteal': 0
    }
    
    # Analyse each completed cycle
    for cycle in cycles:
        if not cycle.is_complete:
            continue
        
        start = cycle.start_date
        end = cycle.end_date
        period_days = cycle.period_length or 5
        cycle_length = cycle.cycle_length
        
        # Skip outliers
        if cycle.is_outlier:
            continue
        
        # Menstrual phase (first N days)
        for day in range(period_days):
            if day >= cycle_length:
                break
            date = start + timedelta(days=day)
            moon_pos = moon_phase.calculate_moon_phase(datetime.combine(date, datetime.min.time()))
            moon_key, _ = moon_phase.get_moon_phase_name(moon_pos)
            correlations['menstrual'][moon_key] += 1
            total_days['menstrual'] += 1
        
        # Follicular phase (after menstrual up to day 14)
        follicular_start = period_days
        follicular_end = min(14, cycle_length)
        for day in range(follicular_start, follicular_end):
            date = start + timedelta(days=day)
            moon_pos = moon_phase.calculate_moon_phase(datetime.combine(date, datetime.min.time()))
            moon_key, _ = moon_phase.get_moon_phase_name(moon_pos)
            correlations['follicular'][moon_key] += 1
            total_days['follicular'] += 1
        
        # Luteal phase (day 14 onwards to end of cycle)
        luteal_start = 14
        if luteal_start < cycle_length:
            for day in range(luteal_start, cycle_length):
                date = start + timedelta(days=day)
                moon_pos = moon_phase.calculate_moon_phase(datetime.combine(date, datetime.min.time()))
                moon_key, _ = moon_phase.get_moon_phase_name(moon_pos)
                correlations['luteal'][moon_key] += 1
                total_days['luteal'] += 1
    
    return correlations, total_days

def print_correlation_analysis():
    """Print detailed correlation analysis"""
    result = analyse_cycle_moon_correlation()
    
    if not result:
        print("Need at least 2 completed cycles for correlation analysis.")
        return
    
    correlations, total_days = result
    
    print("\n╭────────────────────────────────────────────────────────╮")
    print("│  🔍 CYCLE & MOON CORRELATION ANALYSIS                  │")
    print("╰────────────────────────────────────────────────────────╯\n")
    
    # Summary of analysed cycles
    cycles = load_cycles()
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    
    if not valid_cycles:
        print("⚠️  No valid cycles found for analysis")
        print("    Need at least 2 completed cycles between 18-45 days")
        return
    
    print(f"Analysed {len(valid_cycles)} valid cycles\n")
    
    # For each cycle phase, show most common moon phases
    for cycle_phase in ['menstrual', 'follicular', 'luteal']:
        if total_days[cycle_phase] == 0:
            continue
        
        print(f"━━━ During {cycle_phase.upper()} phase ━━━")
        print(f"Total days analysed: {total_days[cycle_phase]}\n")
        
        # Calculate percentages
        phase_counts = correlations[cycle_phase]
        sorted_phases = sorted(phase_counts.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_phases:
            for moon_key, count in sorted_phases[:3]:  # Top 3
                percentage = (count / total_days[cycle_phase]) * 100
                emoji = moon_phase.MOON_PHASES[moon_key]
                _, moon_name = moon_phase.get_moon_phase_name(0.5 if moon_key == 'full' else 0.0)
                # Get proper name
                for pos in [0.01, 0.1, 0.25, 0.45, 0.5, 0.6, 0.75, 0.9]:
                    key, name = moon_phase.get_moon_phase_name(pos)
                    if key == moon_key:
                        moon_name = name
                        break
                
                print(f"  {emoji} {moon_name:20s} {percentage:5.1f}% ({count} days)")
        print()
    
    # Cycle Start Moon Phase Analysis
    print("━━━ Cycle Start Moon Phase ━━━")
    print("What moon phase do your cycles typically begin on?\n")
    
    # Analyse moon phase at start of each cycle
    cycle_start_moons = defaultdict(int)
    valid_cycle_count = 0
    
    for cycle in get_valid_cycles(cycles, exclude_outliers=True):
        if cycle.start_date:
            moon_pos = moon_phase.calculate_moon_phase(datetime.combine(cycle.start_date, datetime.min.time()))
            moon_key, _ = moon_phase.get_moon_phase_name(moon_pos)
            cycle_start_moons[moon_key] += 1
            valid_cycle_count += 1
    
    if valid_cycle_count > 0:
        sorted_start_moons = sorted(cycle_start_moons.items(), key=lambda x: x[1], reverse=True)
        
        for moon_key, count in sorted_start_moons:
            percentage = (count / valid_cycle_count) * 100
            emoji = moon_phase.MOON_PHASES[moon_key]
            # Get proper name
            for pos in [0.01, 0.1, 0.25, 0.45, 0.5, 0.6, 0.75, 0.9]:
                key, name = moon_phase.get_moon_phase_name(pos)
                if key == moon_key:
                    moon_name = name
                    break
            
            print(f"  {emoji} {moon_name:20s} {percentage:5.1f}% ({count}/{valid_cycle_count} cycles)")
        
        # Highlight new vs full moon, and most common overall
        new_moon_count = cycle_start_moons.get('new', 0)
        full_moon_count = cycle_start_moons.get('full', 0)
        most_common = sorted_start_moons[0] if sorted_start_moons else None
        
        print()
        
        # First show the overall most common phase
        if most_common:
            moon_key, count = most_common
            percentage = (count / valid_cycle_count) * 100
            emoji = moon_phase.MOON_PHASES[moon_key]
            # Get proper name
            for pos in [0.01, 0.1, 0.25, 0.45, 0.5, 0.6, 0.75, 0.9]:
                key, name = moon_phase.get_moon_phase_name(pos)
                if key == moon_key:
                    phase_name = name
                    break
            
            if percentage >= 30:  # Strong pattern
                print(f"  ✨ Strong pattern: You often start cycles during {emoji} {phase_name}")
                print(f"     ({count}/{valid_cycle_count} cycles = {percentage:.0f}%)")
        
        # Then compare new vs full moon specifically
        if new_moon_count > 0 or full_moon_count > 0:
            print()
            print("  New Moon 🌑 vs Full Moon 🌕:")
            if new_moon_count > full_moon_count and new_moon_count > 0:
                print(f"     Lean towards NEW MOON ({new_moon_count} vs {full_moon_count})")
            elif full_moon_count > new_moon_count and full_moon_count > 0:
                print(f"     Lean towards FULL MOON ({full_moon_count} vs {new_moon_count})")
            elif new_moon_count == full_moon_count and new_moon_count > 0:
                print(f"     Equal split ({new_moon_count} each)")
            else:
                print(f"     Neither dominates ({new_moon_count} new, {full_moon_count} full)")
    else:
        print("  Not enough data to analyse cycle start patterns")
    
    print()
    
    # Interesting patterns
    print("━━━ Patterns ━━━")
    
    # Check if there's a dominant pattern
    for cycle_phase in ['menstrual', 'follicular', 'luteal']:
        if total_days[cycle_phase] == 0:
            continue
        
        phase_counts = correlations[cycle_phase]
        if phase_counts:
            max_moon = max(phase_counts.items(), key=lambda x: x[1])
            max_percentage = (max_moon[1] / total_days[cycle_phase]) * 100
            
            if max_percentage > 30:  # If one moon phase dominates >30%
                emoji = moon_phase.MOON_PHASES[max_moon[0]]
                print(f"  • Your {cycle_phase} phase often coincides with {emoji} moon phases")
    
    print("\n💡 Note: Correlation does not imply causation!")
    print("   These patterns may be coincidental.\n")

def print_simple_view():
    """Print simple combined view"""
    print(get_combined_visual())
    print()
    
    # Add quick stats if we have data
    cycles = load_cycles()
    valid_cycles = get_valid_cycles(cycles, exclude_outliers=True)
    if valid_cycles and len(valid_cycles) >= 2:
        print("Run 'cycle-moon analyse' for correlation analysis")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'analyse' or command == 'analyze':  # Accept both spellings
            print_simple_view()
            print_correlation_analysis()
        elif command in ['--help', '-h']:
            print("Combined Cycle & Moon Tracker")
            print()
            print("Usage:")
            print("  cycle-moon           - Show current cycle and moon phase")
            print("  cycle-moon analyse   - Show correlation analysis")
            print()
            print("This tool combines data from cycle-tracker and moon-phase")
            print("to show both phases together and analyse patterns.")
        else:
            print(f"Unknown command: {command}")
            print("Use 'cycle-moon --help' for usage information")
    else:
        print_simple_view()

if __name__ == "__main__":
    main()
