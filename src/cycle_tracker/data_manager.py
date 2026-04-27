"""
Data models and storage for cycle tracker.

Handles CSV reading/writing and data validation.
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Data file is stored in project root
SCRIPT_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_FILE = SCRIPT_DIR / ".cycle_tracker_data.csv"

DEFAULT_PERIOD_LENGTH = 5
DEFAULT_CYCLE_LENGTH = 28
# NOTE: Follicular phase length is estimated at ~14 days (ovulation midpoint).
# This is hardcoded because precise ovulation tracking requires symptom monitoring
# (basal body temperature, cervical mucus, LH tests) which is beyond scope.
# TODO: Consider making this user-configurable in config for better personalization.
DEFAULT_FOLLICULAR_PHASE_LENGTH = 14

# Outlier detection thresholds
MIN_CYCLE_LENGTH = 18  # Cycles shorter than this are likely errors
MAX_CYCLE_LENGTH = 45  # Cycles longer than this are likely errors or missed periods
MIN_PERIOD_LENGTH = 2
MAX_PERIOD_LENGTH = 10


class Cycle:
    """Represents a single menstrual cycle"""
    
    def __init__(self, start_date, end_date=None, period_end_date=None, period_length=None):
        self.start_date = start_date
        self.end_date = end_date
        self.period_end_date = period_end_date
        self.period_length = period_length
    
    @property
    def cycle_length(self) -> Optional[int]:
        """Calculate full cycle length (inclusive of both start and end dates)"""
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
    @property
    def is_complete(self) -> bool:
        """Check if cycle is complete (has end date)"""
        return self.end_date is not None
    
    @property
    def is_outlier(self) -> bool:
        """Check if this cycle is an outlier (unusually short or long)"""
        if not self.is_complete:
            return False
        
        length = self.cycle_length
        return length < MIN_CYCLE_LENGTH or length > MAX_CYCLE_LENGTH
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CSV writing"""
        return {
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else '',
            'period_end_date': self.period_end_date.strftime('%Y-%m-%d') if self.period_end_date else '',
            'period_length': self.period_length if self.period_length else ''
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Cycle':
        """Create Cycle from dictionary"""
        return cls(
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            period_end_date=datetime.strptime(data['period_end_date'], '%Y-%m-%d').date() if data.get('period_end_date') else None,
            period_length=int(data['period_length']) if data.get('period_length') and data['period_length'] else None
        )


def setup_data_file() -> bool:
    """Initialize the data file if it doesn't exist"""
    if not DATA_FILE.exists():
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'period_end_date', 'period_length'])
            writer.writeheader()
        print(f"✓ Data file created at: {DATA_FILE}")
        return True
    else:
        print(f"✓ Data file already exists at: {DATA_FILE}")
        return False


def load_cycles() -> List[Cycle]:
    """Load all cycles from CSV file"""
    if not DATA_FILE.exists():
        return []
    
    cycles = []
    with open(DATA_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cycle = Cycle.from_dict(row)
                cycles.append(cycle)
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid row: {e}")
                continue
    
    return cycles


def save_cycles(cycles: List[Cycle]):
    """Save all cycles to CSV file"""
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'period_end_date', 'period_length'])
        writer.writeheader()
        for cycle in cycles:
            writer.writerow(cycle.to_dict())


def add_cycle(start_date, period_length=None) -> Cycle:
    """Add a new cycle and auto-complete the previous one"""
    cycles = load_cycles()
    
    # Auto-complete previous cycle
    if cycles and not cycles[-1].is_complete:
        cycles[-1].end_date = start_date - timedelta(days=1)
    
    # Create new cycle
    new_cycle = Cycle(start_date, period_length=period_length)
    cycles.append(new_cycle)
    
    save_cycles(cycles)
    return new_cycle


def update_period_end(period_end_date) -> Optional[int]:
    """Update when the period ended for the current cycle"""
    cycles = load_cycles()
    
    if not cycles:
        raise ValueError("No cycles to update")
    
    current = cycles[-1]
    
    if current.period_end_date:
        raise ValueError(f"Period already marked as ended on {current.period_end_date.strftime('%Y-%m-%d')}")
    
    # Calculate and validate period length
    period_length = (period_end_date - current.start_date).days + 1
    
    if period_length < MIN_PERIOD_LENGTH or period_length > MAX_PERIOD_LENGTH:
        raise ValueError(f"Period length of {period_length} days seems unusual (expected {MIN_PERIOD_LENGTH}-{MAX_PERIOD_LENGTH} days)")
    
    current.period_end_date = period_end_date
    current.period_length = period_length
    
    save_cycles(cycles)
    return period_length


def edit_cycle(n: int, start_date=None, end_date=None, period_end_date=None) -> 'Cycle':
    """
    Edit a recent cycle in-place. n=1 is the last cycle, n=2 is second-to-last.
    Only fields passed as non-None are updated.
    Recalculates period_length when period_end_date or start_date changes.
    If start_date changes, the preceding cycle's end_date is updated to maintain continuity.
    """
    cycles = load_cycles()

    if not cycles:
        raise ValueError("No cycles recorded yet")

    if n < 1 or n > len(cycles):
        raise ValueError(f"No cycle at position {n} (only {len(cycles)} cycle(s) recorded)")

    cycle = cycles[-n]

    if start_date is not None:
        cycle.start_date = start_date
        # Keep the preceding cycle's end_date contiguous with this start
        if n < len(cycles):
            cycles[-(n + 1)].end_date = start_date - timedelta(days=1)

    if end_date is not None:
        cycle.end_date = end_date

    if period_end_date is not None:
        cycle.period_end_date = period_end_date

    # Recalculate period_length whenever start or period_end changes
    if cycle.period_end_date:
        period_length = (cycle.period_end_date - cycle.start_date).days + 1
        if period_length < MIN_PERIOD_LENGTH or period_length > MAX_PERIOD_LENGTH:
            raise ValueError(
                f"Period length of {period_length} days seems unusual "
                f"(expected {MIN_PERIOD_LENGTH}–{MAX_PERIOD_LENGTH} days)"
            )
        cycle.period_length = period_length

    save_cycles(cycles)
    return cycle


def get_valid_cycles(cycles: List[Cycle], exclude_outliers=True) -> List[Cycle]:
    """
    Get valid completed cycles, optionally excluding outliers.
    
    Outliers are cycles that are unusually short (<18 days) or long (>45 days),
    likely due to missed tracking or data entry errors.
    """
    valid = [c for c in cycles if c.is_complete]
    
    if exclude_outliers:
        valid = [c for c in valid if not c.is_outlier]
    
    return valid
