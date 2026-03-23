# Cycle Tracker

A command-line menstrual cycle phase tracking tool for girls who hate their data being tracked ✨

## Features

- Track cycle phases: menstrual, follicular, and luteal
- User-controlled cycle start and end dates
- CSV-based data storage for historical tracking
- Automatic calculation of average menstrual phase length from historical data
- Notifications about when cycles are due, overdue, or early
- Information about when menstrual phase will end

## Installation

Make the script executable:

```bash
chmod +x cycle_tracker.py
```

Create a symlink for easy access:

```bash
# From the cycle-tracker directory
ln -s "$(pwd)/cycle-tracker" /usr/local/bin/cycle-tracker
```

Or add to your PATH in `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$PATH:/path/to/cycle-tracker"
```

## Usage

### Start a new cycle
```bash
cycle-tracker start
```

Start a cycle with custom menstrual phase length:
```bash
cycle-tracker start 4
```

### Get current cycle phase
```bash
cycle-tracker cycle-phase
```
Returns: `◯ menstrual`, `◔ follicular`, or `◕ luteal`

Visual indicators:
- `◯` Empty circle = Menstrual phase
- `◔` Quarter filled = Follicular phase  
- `◕` Three-quarters filled = Luteal phase
- `●` Full circle = Complete cycle

This is the default command, so you can also just run:
```bash
cycle-tracker
```

### End current cycle
```bash
cycle-tracker end
```

### Show detailed status
```bash
cycle-tracker status
```

## How It Works

### Cycle Phases

1. **Menstrual Phase**: First 4-5 days of the cycle (default 5 days, adjustable)
   - The tracker uses historical data to calculate average menstrual phase length
   - Can be customized when starting a new cycle

2. **Follicular Phase**: Days 1-14 of the cycle
   - Includes the menstrual phase
   - Continues until ovulation (around day 14)

3. **Luteal Phase**: Day 14 onwards
   - From ovulation to the end of the cycle
   - Typically lasts about 14 days

### Data Storage

Cycle data is stored in `~/.cycle_tracker_data.csv` with the following fields:
- `start_date`: When the cycle began
- `end_date`: When the cycle ended (empty if ongoing)
- `menstrual_days`: Length of menstrual phase for this cycle

### Cycle Tracking Logic

- The tracker will NOT start a new cycle automatically
- User must explicitly begin each cycle with `cycle-tracker start`
- If a cycle is not ended, the tracker assumes a default cycle length (28 days) for predictions
- Historical data is used to:
  - Calculate average menstrual phase length
  - Calculate average cycle length
  - Predict when the next cycle is due

### Notifications

The tracker informs you:
- If the next cycle beginning is due, overdue (>2 days late), or early
- When the menstrual phase is expected to end
- Current day of the cycle

## Example Workflow

```bash
# Start tracking your first cycle
$ cycle-tracker start
New cycle started on 2026-03-23
Menstrual phase: 5 days (ends around 2026-03-27)

# Check current phase
$ cycle-tracker cycle-phase
◯ menstrual

# Get detailed status
$ cycle-tracker status
◯  Current phase: menstrual
Day 1 of menstrual phase (typically 5 days)
Menstrual phase will end in 4 day(s) (2026-03-27)

# End the cycle when it completes
$ cycle-tracker end
Cycle ended on 2026-04-20
Cycle length: 28 days

# Start the next cycle
$ cycle-tracker start
New cycle started on 2026-04-21
Menstrual phase: 5 days (ends around 2026-04-25)
```

## Future Features (Planned)

- Testing with historical data
- Future cycle predictions
- Moon phase correlation
