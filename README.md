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

# 4. Check status anytime
cycle-tracker status

# 5. End cycle when next period starts
cycle-tracker end
cycle-tracker start  # Start the new cycle
```

**Important:** Don't end the cycle when your period ends! Wait until your next period starts.

See [detailed usage](#usage) below.

## Features

### 🩸 Cycle Tracking
- Track phases: menstrual, follicular, luteal
- **Prediction ranges** (not just averages!)
- **Confidence intervals** (68% confidence)
- **Quality scores** (0-100)
- Daily updated predictions
- Luteal phase insights

### 🌙 Moon Phase (Optional)
- Check current moon phase
- Days until next full/new moon
- No internet required

### 🩸🌙 Combined Analysis (Optional)
- View both cycles together
- Analyse correlations
- Pattern detection

**All optional!** The cycle tracker works completely independently.

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
cycle-tracker start

# Mark when bleeding stops (optional but recommended)
cycle-tracker end-period

# Check current phase
cycle-tracker              # Quick: menstrual/follicular/luteal
cycle-tracker status       # Detailed with statistics

# End cycle when NEXT period starts (not when bleeding stops!)
cycle-tracker end

# Predict next cycle
cycle-tracker predict
```

**Key Concept:** A menstrual cycle runs from the first day of one period to the day before the next period starts (typically 21-35 days). Don't confuse this with your period length (typically 4-7 days).

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
cp moon_config.json.example moon_config.json
# Edit moon_config.json with your city coordinates
```

See [MOON_PHASE.md](MOON_PHASE.md) for details.

</details>

<details>
<summary>🩸🌙 Combined Tracker (Optional)</summary>

```bash
# View both cycles together
cycle-moon

# Analyse correlations (requires 2+ completed cycles)
cycle-moon analyse
```

See [CYCLE_MOON.md](CYCLE_MOON.md) for details.

</details>

## How It Works

### Statistical Predictions

This tracker uses research-based methods adapted for individual use:
- **Variance modeling**: Tracks variation, not just average
- **Confidence intervals**: Shows prediction ranges (±1 std dev = 68%)
- **Quality assessment**: Warns when data is insufficient
- **Sequential updates**: Predictions improve as cycle progresses

**Research credits:** Methods inspired by [Urteaga et al. (2021-2022)](CITATIONS.md) menstrual cycle prediction research.

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

- **[CITATIONS.md](CITATIONS.md)** - Research attribution
- **[MOON_PHASE.md](MOON_PHASE.md)** - Moon tracker guide
- **[CYCLE_MOON.md](CYCLE_MOON.md)** - Combined tracker guide

## Testing

```bash
python3 test_cycle_tracker.py
```

Tests include:
- Cycle length predictions
- Variance calculations
- Menstrual phase averaging

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
