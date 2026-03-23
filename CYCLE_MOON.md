# Combined Cycle & Moon Tracker

An optional tool that shows both your menstrual cycle phase and moon phase together, plus analyses correlations between them.

## Features

- **Combined view**: See both cycles side-by-side with visual indicators
- **Correlation analysis**: Discover patterns between your cycle and moon phases
- **Optional add-on**: Main cycle tracker works independently

## Usage

### Simple View

```bash
cycle-moon
```

Shows:
- Current menstrual cycle phase with emoji
- Current moon phase with emoji  
- Illumination percentage
- Reminder about analysis command

Example output:
```
╭────────────────────────────────────────────────────────╮
│  🩸 CYCLE & MOON TRACKER 🌙                            │
├────────────────────────────────────────────────────────┤
│  Menstrual Cycle: ◯ MENSTRUAL                            │
│    Day 1 of menstrual phase (typically 5 days)        │
│                                                        │
│  Moon Phase: 🌒 Waxing Crescent                        │
│     24.3% illuminated                                │
╰────────────────────────────────────────────────────────╯
```

### Correlation Analysis

```bash
cycle-moon analyse
```

Analyses your historical data to show:
- Which moon phases occur most during each cycle phase
- Percentage breakdown for menstrual, follicular, and luteal phases
- Any interesting patterns (e.g., "period often starts around full moon")
- Number of cycles analysed

Example output:
```
╭────────────────────────────────────────────────────────╮
│  🔍 CYCLE & MOON CORRELATION ANALYSIS                  │
╰────────────────────────────────────────────────────────╯

Analysed 4 completed cycles

━━━ During MENSTRUAL phase ━━━
Total days analysed: 19

  🌔 Waxing Gibbous        78.9% (15 days)
  🌓 First Quarter         15.8% (3 days)
  🌕 Full Moon              5.3% (1 days)

━━━ During FOLLICULAR phase ━━━
Total days analysed: 37

  🌖 Waning Gibbous        56.8% (21 days)
  🌕 Full Moon             16.2% (6 days)
  🌔 Waxing Gibbous        16.2% (6 days)

━━━ During LUTEAL phase ━━━
Total days analysed: 52

  🌘 Waning Crescent       40.4% (21 days)
  🌒 Waxing Crescent       32.7% (17 days)
  🌑 New Moon              13.5% (7 days)

━━━ Patterns ━━━
  • Your menstrual phase often coincides with 🌔 moon phases
  • Your follicular phase often coincides with 🌖 moon phases
  • Your luteal phase often coincides with 🌘 moon phases

💡 Note: Correlation does not imply causation!
   These patterns may be coincidental.
```

## Requirements

- At least 2 completed cycles for correlation analysis
- Both `cycle-tracker` and `moon-phase` tools installed
- **Important**: Cycles must track the full menstrual cycle (not just your period!)

### What is a Full Cycle?

A menstrual cycle is counted from:
- **Day 1**: First day of your period (bleeding starts)
- **End**: The day BEFORE your next period starts

**Example:**
- Period starts: June 1st → `cycle-tracker start`
- Period ends: June 6th (but don't end the cycle yet!)
- Next period starts: June 29th → `cycle-tracker end` then `cycle-tracker start`
- This cycle was 28 days long (June 1 to June 28)

**Common mistake:** Ending the cycle when your period ends (5-7 days) instead of when the next one starts. This makes analysis impossible because the follicular and luteal phases are missing!

## How It Works

### Combined View
1. Fetches current cycle phase from cycle tracker
2. Calculates current moon phase
3. Displays both in a unified interface

### Correlation Analysis
1. Iterates through all completed cycles in your history
2. For each day of each cycle, determines:
   - Which cycle phase you were in (menstrual/follicular/luteal)
   - Which moon phase it was
3. Counts occurrences and calculates percentages
4. Identifies patterns (e.g., >30% occurrence = notable pattern)

## Installation

Link to your PATH:

```bash
# From the cycle-tracker directory
ln -s "$(pwd)/cycle-moon" /usr/local/bin/cycle-moon
```

Or use directly:
```bash
./cycle-moon
```

## Understanding the Results

### What the Analysis Shows

The correlation analysis tells you:
- **Historical patterns**: Which moon phases you've historically been in during each cycle phase
- **Percentages**: How often each combination occurs
- **Dominant patterns**: If one moon phase consistently aligns with a cycle phase (>30%)

### Example Interpretations

**Pattern found:**
> "Your menstrual phase often coincides with 🌕 full moon (45% of the time)"

This means: In your tracked cycles, your period started around the full moon almost half the time.

**No strong pattern:**
> All moon phases evenly distributed (12-15% each)

This means: Your cycle doesn't seem to align with any particular moon phase.

## Scientific Context

### The Myth vs Reality

**The Myth**: Menstrual cycles are synchronized with moon cycles
- Both average ~29 days
- Historical cultural beliefs
- Anecdotal reports

**The Reality**: No proven scientific link
- Cycle lengths vary widely (21-35 days)
- Moon cycle is constant (29.53 days)
- Studies show no significant correlation
- Personal patterns may be coincidental

### Why Track It Anyway?

1. **Personal curiosity**: Some people find patterns meaningful
2. **Individual variation**: Your body might have unique patterns
3. **Data-driven understanding**: Observe your own experience
4. **Cultural/spiritual interest**: Many traditions track lunar cycles

### What This Tool Does

✅ Shows you YOUR patterns
✅ Provides statistical breakdown
✅ Reminds you correlation ≠ causation
❌ Doesn't claim moon causes cycle changes
❌ Doesn't make predictions based on moon

## Privacy & Data

- All analysis done locally
- No data sent anywhere
- Uses your existing cycle data
- Combines with mathematical moon calculations
- No cloud storage or accounts

## Tips

- **Need more data**: Analysis improves with more completed cycles (6+ is ideal)
- **Track consistently**: Gaps in cycle tracking affect correlation accuracy
- **Be skeptical**: Look for patterns, but don't read too much into them
- **Just for fun**: This is an exploratory tool, not medical advice

## Limitations

- Requires at least 2 completed cycles
- Correlation analysis is descriptive, not predictive
- Small sample sizes may show random patterns
- Doesn't account for lifestyle factors that affect both cycles

## Future Enhancements

Potential additions:
- Visual timeline showing both cycles
- Export correlation data
- Compare specific date ranges
- Track changes in patterns over time
- Statistical significance testing

## Optional Tool

Remember: This is completely optional! The main `cycle-tracker` works perfectly fine without any moon phase tracking. Use `cycle-moon` only if you're curious about potential correlations.
