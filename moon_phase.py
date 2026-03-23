#!/usr/bin/env python3
"""
Moon Phase Tracker

Calculates current moon phase based on astronomical algorithms.
No external API calls - uses mathematical calculations based on date/time.
"""

import json
import math
from datetime import datetime
from pathlib import Path

# Constants
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = SCRIPT_DIR / "moon_config.json"

# Moon phase emojis
MOON_PHASES = {
    'new': '🌑',
    'waxing_crescent': '🌒',
    'first_quarter': '🌓',
    'waxing_gibbous': '🌔',
    'full': '🌕',
    'waning_gibbous': '🌖',
    'last_quarter': '🌗',
    'waning_crescent': '🌘'
}

def load_config():
    """Load location configuration"""
    if not CONFIG_FILE.exists():
        # Return default config
        return {
            'location': {
                'name': 'London',
                'latitude': 51.5074,
                'longitude': -0.1278,
                'timezone': 'Europe/London'
            }
        }
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def calculate_moon_phase(date=None):
    """
    Calculate moon phase using astronomical algorithms.
    
    Based on the lunar cycle period of 29.53059 days.
    Returns phase value from 0 (new moon) to 1 (back to new moon).
    
    Algorithm: Compare date to known new moon and calculate position in cycle.
    """
    if date is None:
        date = datetime.now()
    
    # Known new moon: January 6, 2000, 18:14 UTC
    known_new_moon = datetime(2000, 1, 6, 18, 14, 0)
    
    # Lunar cycle period (synodic month) in days
    lunar_cycle = 29.53058867
    
    # Calculate days since known new moon
    days_since = (date - known_new_moon).total_seconds() / 86400.0
    
    # Calculate position in current lunar cycle (0 to 1)
    phase_position = (days_since % lunar_cycle) / lunar_cycle
    
    return phase_position

def get_moon_phase_name(phase_position):
    """
    Convert phase position (0-1) to moon phase name.
    
    Phase divisions:
    - New Moon: 0.00 - 0.03 and 0.97 - 1.00
    - Waxing Crescent: 0.03 - 0.22
    - First Quarter: 0.22 - 0.28
    - Waxing Gibbous: 0.28 - 0.47
    - Full Moon: 0.47 - 0.53
    - Waning Gibbous: 0.53 - 0.72
    - Last Quarter: 0.72 - 0.78
    - Waning Crescent: 0.78 - 0.97
    """
    if phase_position < 0.03 or phase_position >= 0.97:
        return 'new', 'New Moon'
    elif phase_position < 0.22:
        return 'waxing_crescent', 'Waxing Crescent'
    elif phase_position < 0.28:
        return 'first_quarter', 'First Quarter'
    elif phase_position < 0.47:
        return 'waxing_gibbous', 'Waxing Gibbous'
    elif phase_position < 0.53:
        return 'full', 'Full Moon'
    elif phase_position < 0.72:
        return 'waning_gibbous', 'Waning Gibbous'
    elif phase_position < 0.78:
        return 'last_quarter', 'Last Quarter'
    else:
        return 'waning_crescent', 'Waning Crescent'

def calculate_illumination(phase_position):
    """
    Calculate percentage of moon illuminated.
    
    Uses cosine function: 0% at new, 100% at full, 0% at next new.
    """
    # Convert phase position to angle (0 to 2π)
    angle = phase_position * 2 * math.pi
    
    # Calculate illumination (50% average, ±50% variation)
    illumination = 50 * (1 - math.cos(angle))
    
    return round(illumination, 1)

def get_next_full_moon(current_date=None):
    """Calculate days until next full moon"""
    if current_date is None:
        current_date = datetime.now()
    
    phase_position = calculate_moon_phase(current_date)
    
    # Full moon is at position 0.5
    # Calculate days until position 0.5
    if phase_position < 0.5:
        days_until = (0.5 - phase_position) * 29.53058867
    else:
        days_until = (1.5 - phase_position) * 29.53058867
    
    return round(days_until, 1)

def get_next_new_moon(current_date=None):
    """Calculate days until next new moon"""
    if current_date is None:
        current_date = datetime.now()
    
    phase_position = calculate_moon_phase(current_date)
    
    # New moon is at position 0 (or 1)
    days_until = (1.0 - phase_position) * 29.53058867
    
    return round(days_until, 1)

def print_moon_status():
    """Print current moon phase information"""
    config = load_config()
    location = config['location']
    
    now = datetime.now()
    phase_position = calculate_moon_phase(now)
    phase_key, phase_name = get_moon_phase_name(phase_position)
    emoji = MOON_PHASES[phase_key]
    illumination = calculate_illumination(phase_position)
    
    # Calculate days into cycle
    days_into_cycle = phase_position * 29.53058867
    
    print("╭─────────────────────────────────────────╮")
    print(f"│  {emoji}  {phase_name:30s}  │")
    print("│                                         │")
    print(f"│  Illumination: {illumination:5.1f}%                  │")
    print(f"│  Day {days_into_cycle:4.1f} of 29.5 day cycle        │")
    print("│                                         │")
    
    # Next phase transitions
    next_full = get_next_full_moon(now)
    next_new = get_next_new_moon(now)
    
    if next_full < next_new:
        print(f"│  Next Full Moon: in {next_full:4.1f} days       │")
    else:
        print(f"│  Next New Moon: in {next_new:4.1f} days        │")
    
    print("│                                         │")
    print(f"│  📍 {location['name']:33s}  │")
    print(f"│  🕐 {now.strftime('%Y-%m-%d %H:%M'):33s}  │")
    print("╰─────────────────────────────────────────╯")

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Moon Phase Tracker")
        print()
        print("Usage: moon-phase")
        print("       Shows current moon phase")
        print()
        print("Configuration: Edit moon_config.json to set your location")
        print("Default location: London, UK")
        return
    
    print_moon_status()

if __name__ == "__main__":
    main()
