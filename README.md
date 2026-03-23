# Cycle Tracker

A command-line menstrual cycle phase tracking tool with statistical predictions.

For girls who hate their data being stolen for advertising ✨🩸

## Features

### Cycle Tracking
- Track cycle phases: menstrual, follicular, and luteal
- **Prediction ranges with confidence intervals** (not just averages!)
- **Tracking quality assessment** to understand prediction accuracy
- **Daily updated predictions** that improve as cycle progresses
- **Luteal phase tracking** (the more stable part of your cycle)
- User-controlled cycle start and end dates
- CSV-based data storage for historical tracking
- Automatic calculation of patterns from your historical data

### Moon Phase Tracking 🌙
- Check current moon phase with a single command
- See illumination percentage and days in lunar cycle
- Calculate days until next full or new moon
- No internet required - uses mathematical calculations
- Configurable location (defaults to London)

### Combined Cycle & Moon View 🩸🌙 (Optional)
- See both cycle and moon phase together
- Analyze correlations between your cycle and moon phases
- Discover if your cycle aligns with lunar cycles
- Statistical breakdown by cycle phase
- Completely optional - cycle tracker works independently

See [MOON_PHASE.md](MOON_PHASE.md) for moon tracker documentation.  
See [CYCLE_MOON.md](CYCLE_MOON.md) for combined tracker documentation.

### Statistical Approach

This tracker uses research-based statistical methods adapted for individual use:
- Variance-based prediction ranges (±1 std dev = 68% confidence)
- Tracking adherence modeling  
- Sequential prediction updates
- Phase-specific pattern recognition

Methods inspired by Urteaga et al. (2021-2022) menstrual cycle prediction research.  
See [CITATIONS.md](CITATIONS.md) for detailed research credits.

## Installation

Make the script executable:

```bash
chmod +x cycle_tracker.py
```

Create symlinks for easy access:

```bash
# From the cycle-tracker directory
ln -s "$(pwd)/cycle-tracker" /usr/local/bin/cycle-tracker
ln -s "$(pwd)/moon-phase" /usr/local/bin/moon-phase
ln -s "$(pwd)/cycle-moon" /usr/local/bin/cycle-moon
```

Or add to your PATH in `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$PATH:/path/to/cycle-tracker"
```

## Usage

### Cycle Tracker Commands

#### Initialize data file (first time setup)
```bash
cycle-tracker setup
```

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

Displays:
- Current phase with visual indicator
- Days into cycle and menstrual phase end date
- **Cycle length statistics** (average ± variation)
- **Predicted cycle end range** with confidence level
- **Tracking quality score** (0-100)
- Luteal phase length (if enough data)

### Predict next cycle
```bash
cycle-tracker predict
```

Shows prediction for the next cycle with:
- Expected start date
- Likely date range (68% confidence interval)
- Based on your historical patterns
- Luteal phase insights

### Moon Phase Commands 🌙

#### Check current moon phase
```bash
moon-phase
```

Shows:
- Current moon phase with emoji (🌑🌒🌓🌔🌕🌖🌗🌘)
- Illumination percentage
- Day in lunar cycle (29.5 days)
- Days until next full or new moon
- Your location and current time

#### Configure location
Edit `moon_config.json`:
```json
{
  "location": {
    "name": "Your City",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London"
  }
}
```

See [MOON_PHASE.md](MOON_PHASE.md) for more details.

### Combined Cycle & Moon Commands 🩸🌙

#### View both cycles together
```bash
cycle-moon
```

Shows your current menstrual cycle phase and moon phase side-by-side.

#### Analyze correlations
```bash
cycle-moon analyze
```

Analyzes your historical data to find patterns:
- Which moon phases occur during each cycle phase
- Percentage breakdowns
- Notable patterns (if any)

Requires at least 2 completed cycles. See [CYCLE_MOON.md](CYCLE_MOON.md) for details.

**Note**: This is optional! The cycle tracker works completely independently.

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

Cycle data is stored in `.cycle_tracker_data.csv` in the same directory as the script with the following fields:
- `start_date`: When the cycle began
- `end_date`: When the cycle ended (empty if ongoing)
- `menstrual_days`: Length of menstrual phase for this cycle

Run `cycle-tracker setup` to initialize the data file if needed.

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
# Initialize the data file (first time only)
$ cycle-tracker setup
✓ Data file created at: /path/to/cycle-tracker/.cycle_tracker_data.csv

# Start tracking your first cycle
$ cycle-tracker start
New cycle started on 2026-03-23
Menstrual phase: 5 days (ends around 2026-03-27)

# Check current phase
$ cycle-tracker cycle-phase
◯ menstrual

# Get detailed status
$ cycle-tracker status
╭─────────────────────────────────────────────────╮
│  ◯  Current Phase: MENSTRUAL                    │
│                                                 │
│  Day 1 of menstrual phase (typically 5 days)    │
│  Menstrual phase ends in 4 day(s) (2026-03-27)  │
╰─────────────────────────────────────────────────╯

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

- Future cycle predictions
- Moon phase correlation

## Testing

Run the test suite to verify cycle length predictions:

```bash
python3 test_cycle_tracker.py
```

The tests verify:
- Average cycle length calculation from historical data
- Cycle prediction accuracy (e.g., 26-day average → 26-day predictions)
- Menstrual phase length calculations
- Default values when no historical data exists
