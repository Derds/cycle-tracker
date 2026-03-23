# Moon Phase Tracker

A simple command-line tool to check the current moon phase.

## Usage

```bash
moon-phase
```

This will display:
- Current moon phase with emoji 🌑🌒🌓🌔🌕🌖🌗🌘
- Percentage of illumination
- Current day in the lunar cycle (29.5 days)
- Days until next full or new moon
- Your configured location
- Current date and time

## Configuration

Edit `moon_config.json` to set your location:

```json
{
  "location": {
    "name": "London",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London"
  }
}
```

### Common Locations

**London, UK:**
```json
{"name": "London", "latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London"}
```

**New York, USA:**
```json
{"name": "New York", "latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"}
```

**Sydney, Australia:**
```json
{"name": "Sydney", "latitude": -33.8688, "longitude": 151.2093, "timezone": "Australia/Sydney"}
```

**Tokyo, Japan:**
```json
{"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503, "timezone": "Asia/Tokyo"}
```

## How It Works

The moon phase is calculated using astronomical algorithms:

1. **Lunar Cycle**: The moon completes a cycle every 29.53059 days (synodic month)
2. **Known Reference**: Uses a known new moon date (January 6, 2000, 18:14 UTC)
3. **Phase Calculation**: Calculates days since the reference and determines current position in the cycle
4. **No API Required**: All calculations are done locally using mathematics

### Moon Phases

The 8 primary phases tracked:
- 🌑 **New Moon** (0% illumination)
- 🌒 **Waxing Crescent** (0-50% illumination, increasing)
- 🌓 **First Quarter** (~50% illumination)
- 🌔 **Waxing Gibbous** (50-100% illumination, increasing)
- 🌕 **Full Moon** (100% illumination)
- 🌖 **Waning Gibbous** (50-100% illumination, decreasing)
- 🌗 **Last Quarter** (~50% illumination)
- 🌘 **Waning Crescent** (0-50% illumination, decreasing)

## Example Output

```
╭─────────────────────────────────────────╮
│  🌒  Waxing Crescent                 │
│                                         │
│  Illumination:  24.2%                  │
│  Day  4.8 of 29.5 day cycle        │
│                                         │
│  Next Full Moon: in  9.9 days       │
│                                         │
│  📍 London                             │
│  🕐 2026-03-23 12:08                   │
╰─────────────────────────────────────────╯
```

## Installation

Link to your PATH for easy access:

```bash
# From the cycle-tracker directory
ln -s "$(pwd)/moon-phase" /usr/local/bin/moon-phase
```

Or add to `~/bin`:

```bash
ln -s "$(pwd)/moon-phase" ~/bin/moon-phase
```

## Integration with Cycle Tracker

The moon phase tracker is designed to work alongside the cycle tracker, allowing you to:

- Compare your cycle phase with the moon phase
- Observe any patterns or correlations over time
- Track both cycles independently

Future features may include automatic correlation analysis between menstrual cycles and moon phases.

## Accuracy

The calculations are based on astronomical algorithms and provide accurate moon phase information. Small variations may occur due to:
- Geographic location (moon rises/sets at different times)
- Atmospheric conditions
- Precision of mathematical approximations

For most practical purposes, the accuracy is more than sufficient.

## Notes

- The moon phase is the same worldwide at any given moment
- Location mainly affects what time you see the moon rise and set
- The lunar cycle is approximately 29.5 days (slightly variable)
- This is independent of time zones (calculations use UTC internally)
