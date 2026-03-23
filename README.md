# Cycle Tracker

A privacy-first, command-line menstrual cycle tracker with statistical predictions.

**For those who hate their data being stolen for advertising** ✨🩸

## Quick Start

```bash
# 1. Setup
cycle-tracker setup

# 2. Start tracking when your period begins
cycle-tracker start

# 3. Mark when bleeding stops (optional but recommended)
cycle-tracker end-period

# 4. When next period starts, just run 'start' again
#    (it will automatically end the previous cycle)
cycle-tracker start
```

**Key:** Just use `start` each time your period begins. No need for separate `end` command!

See [detailed usage](#usage) below.

## Features

### 🩸 Cycle Tracking
- Track phases: menstrual, follicular, luteal
- **Auto-complete previous cycle** when you start a new one
- **Period end tracking** (bleeding vs full cycle)
- **Prediction ranges** (not just averages!)
- **Confidence intervals** (68% confidence)
- **Quality scores** (0-100)
- Daily updated predictions
- Luteal phase insights
- **Calendar view** with phase predictions
- **Future date predictions** (what phase will I be in on X date?)
- **Historical trend graphs** (ASCII charts in your terminal)

### 🌙 Moon Phase (Optional)
- Check current moon phase
- Days until next full/new moon
- No internet required

### 🩸🌙 Combined Analysis (Optional)
- View both cycles together
- Analyse correlations
- Pattern detection

**All optional!** The cycle tracker works completely independently.

## Project Structure

```
cycle-tracker/
├── README.md                    # Main documentation
├── cycle-tracker                # CLI wrapper for cycle tracker
├── moon-phase                   # CLI wrapper for moon phase
├── cycle-moon                   # CLI wrapper for combined view
├── cycle_moon.py                # Combined tracker implementation
│
├── src/
│   ├── cycle_tracker/           # Core cycle tracker modules
│   │   ├── cycle_tracker.py     # Main CLI
│   │   ├── data_manager.py      # Data models & storage
│   │   ├── statistics.py        # Statistical calculations
│   │   ├── predictions.py       # Phase detection logic
│   │   └── display.py           # Output formatting
│   │
│   └── moon_tracker/            # Moon phase tracker
│       └── moon_phase.py        # Moon calculations
│
└── docs/                        # Documentation
    ├── CITATIONS.md             # Research credits
    ├── CODE_STRUCTURE.md        # Architecture docs
    ├── CYCLE_MOON.md            # Combined tracker guide
    ├── MOON_PHASE.md            # Moon tracker guide
    └── NEXT_STEPS.md            # Future enhancements
```

**Data files** (git-ignored):
- `.cycle_tracker_data.csv` - Your cycle data (in project root)
- `src/moon_tracker/moon_config.json` - Moon tracker location config (optional)

## Installation

<details>
<summary>📦 Click to expand installation instructions</summary>

### Requirements
- Python 3.7+
- macOS, Linux, or WSL

### Setup

1. **Make scripts executable:**
   ```bash
   cd cycle-tracker
   chmod +x cycle-tracker moon-phase cycle-moon
   ```

2. **Add to PATH** (choose one):

   **Option A: Link to /usr/local/bin**
   ```bash
   ln -s "$(pwd)/cycle-tracker" /usr/local/bin/cycle-tracker
   ln -s "$(pwd)/moon-phase" /usr/local/bin/moon-phase
   ln -s "$(pwd)/cycle-moon" /usr/local/bin/cycle-moon
   ```

   **Option B: Add to ~/bin**
   ```bash
   mkdir -p ~/bin
   ln -s "$(pwd)/cycle-tracker" ~/bin/cycle-tracker
   ln -s "$(pwd)/moon-phase" ~/bin/moon-phase
   ln -s "$(pwd)/cycle-moon" ~/bin/cycle-moon
   
   # Add to ~/.zshrc or ~/.bashrc:
   echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

</details>

## Usage

### Basic Commands

```bash
# Initialize (first time only)
cycle-tracker setup

# Start a new cycle (when period/bleeding begins)
# This automatically ends the previous cycle!
cycle-tracker start

# Mark when bleeding stops (optional but recommended)
cycle-tracker end-period

# Check current phase
cycle-tracker              # Quick: menstrual/follicular/luteal
cycle-tracker status       # Detailed with statistics

# Predict next cycle
cycle-tracker predict

# Check phase on a specific date
cycle-tracker on 9 May 2026
cycle-tracker on 2026-05-09

# View calendar with predictions
cycle-tracker calendar     # This month
cycle-tracker calendar 1   # Next month
cycle-tracker calendar 2   # Two months ahead

# View historical trends (graphs)
cycle-tracker graph

# Get help
cycle-tracker help
```

**Simplified workflow:** Just use `cycle-tracker start` each time your period begins. It will automatically complete the previous cycle!

### What You Get

**Simple view:**
```bash
$ cycle-tracker
◯ menstrual
```

**Detailed view:**
```bash
$ cycle-tracker status
╭──────────────────────────────────────────────────╮
│  ◯  Current Phase: MENSTRUAL                     │
│                                                  │
│  Day 1 of menstrual phase (typically 5 days)     │
│  Menstrual phase ends in 4 day(s) (2026-03-27)   │
│                                                  │
│  Cycle length: 27 ± 0.8 days (avg ± variation)   │
│  Expected end: Apr 19 - Apr 19 (50% confidence)  │
│  Tracking quality: 🟢 85/100                      │
│  Your luteal phase: ~13 days (stable)            │
╰──────────────────────────────────────────────────╯
```

<details>
<summary>🌙 Moon Phase Commands (Optional)</summary>

```bash
# Check current moon phase
moon-phase

# Configure your location
cp src/moon_tracker/moon_config.json.example src/moon_tracker/moon_config.json
# Edit src/moon_tracker/moon_config.json with your city coordinates
```

See [docs/MOON_PHASE.md](docs/MOON_PHASE.md) for details.

</details>

<details>
<summary>🩸🌙 Combined Tracker (Optional)</summary>

```bash
# View both cycles together
cycle-moon

# Analyse correlations (requires 2+ completed cycles)
cycle-moon analyse
```

See [docs/CYCLE_MOON.md](docs/CYCLE_MOON.md) for details.

</details>

<details>
<summary>📊 Visualising Your Data</summary>

View historical trends with ASCII graphs:

```bash
cycle-tracker graph
```

Shows:
- **Cycle length over time** with trend line
- **Period length over time** with trend line  
- Summary statistics
- Trend interpretation (stable/increasing/decreasing)

Example output:
```
╭─────────────────────────────────────────────────╮
│         Cycle Length Over Time                  │
├─────────────────────────────────────────────────┤
│  30 │          ●      ●                         │
│  28 │      ●      ●──────●──────                │
│  26 │  ●──────                      ●           │
│  24 │                                   ●       │
├─────┼─────────────────────────────────────────┤
│      Jun 25        Oct 25        Feb 26        │
╰─────────────────────────────────────────────────╯

● Data points     ─ Trend line
Days: 25-31 days (avg: 28.3)
Trend: stable
```

Perfect for spotting patterns and changes over time!

</details>

## How It Works

### Statistical Predictions

This tracker uses research-based methods adapted for individual use:
- **Variance modeling**: Tracks variation, not just average
- **Confidence intervals**: Shows prediction ranges (±1 std dev = 68%)
- **Quality assessment**: Warns when data is insufficient
- **Sequential updates**: Predictions improve as cycle progresses

**Research credits:** Methods inspired by [Urteaga et al. (2021-2022)](docs/CITATIONS.md) menstrual cycle prediction research.

### Data Storage

- Stored locally in `.cycle_tracker_data.csv` (in the script directory)
- CSV format: `start_date, end_date, menstrual_days`
- No cloud, no accounts, no tracking
- Your data never leaves your device

### Moon Calculations

- Uses astronomical algorithms (no API calls)
- Based on lunar cycle: 29.53059 days
- Reference point: Jan 6, 2000 new moon
- Accurate worldwide

## Documentation

- **[docs/CITATIONS.md](docs/CITATIONS.md)** - Research attribution
- **[docs/MOON_PHASE.md](docs/MOON_PHASE.md)** - Moon tracker guide
- **[docs/CYCLE_MOON.md](docs/CYCLE_MOON.md)** - Combined tracker guide
- **[docs/CODE_STRUCTURE.md](docs/CODE_STRUCTURE.md)** - Architecture documentation
- **[docs/NEXT_STEPS.md](docs/NEXT_STEPS.md)** - Planned enhancements
- **[CYCLE_MOON.md](CYCLE_MOON.md)** - Combined tracker guide

## Testing

Run the comprehensive test suite:

```bash
python3 src/cycle_tracker/test_cycle_tracker.py
```

Tests cover:
- ✓ Cycle statistics (mean, standard deviation, outlier exclusion)
- ✓ Period length calculation
- ✓ Tracking quality scoring  
- ✓ Phase detection (menstrual, follicular, luteal)
- ✓ Historical date phase lookup
- ✓ Future date predictions
- ✓ Next cycle prediction with confidence intervals
- ✓ Outlier detection and exclusion

All tests use synthetic data and run in seconds. No real data required.

## Why Use This?

✅ **Privacy-first**: No data collection, works offline  
✅ **Honest predictions**: Shows uncertainty, not false precision  
✅ **Research-based**: Adapted from peer-reviewed methods  
✅ **Educational**: Explains the science (and myths)  
✅ **Modular**: Use what you want, ignore the rest  

## Contributing

This is a personal project, but suggestions welcome! Open an issue or PR.

## License

MIT License - Use freely, modify as needed

---

**Note:** This is not medical advice. Consult healthcare professionals for medical concerns.
