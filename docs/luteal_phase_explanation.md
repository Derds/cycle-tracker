# Luteal Phase Tracking - Explained

## The Three Phases of a Menstrual Cycle

1. **Menstrual Phase** (Days 1-5): Bleeding occurs
2. **Follicular Phase** (Days 1-14): From start of period to ovulation
   - Note: Includes menstrual phase
   - Variable length - can be 7-21+ days
3. **Luteal Phase** (Days 14-28): From ovulation to next period
   - More STABLE - typically 12-16 days
   - Less variable than follicular phase

## Why Track Luteal Phase Separately?

### Key Research Finding:
The luteal phase length is more **consistent** than overall cycle length because:
- Controlled by progesterone (more stable hormone)
- Less affected by stress, illness, travel
- Varies only by ~1-2 days for most people

### Example:
Person with variable cycles:
- Cycle 1: 26 days (Follicular: 12 days, Luteal: 14 days)
- Cycle 2: 30 days (Follicular: 16 days, Luteal: 14 days)
- Cycle 3: 28 days (Follicular: 14 days, Luteal: 14 days)

**Observation**: Luteal phase = always 14 days!
**Variation comes from follicular phase**

## Better Predictions

### Without Luteal Tracking:
"Your average cycle is 28 days ± 2 days"

### With Luteal Tracking:
"Your luteal phase is always 14 days. Your follicular phase varies 12-16 days.
Next cycle will likely be 26-30 days."

More precise because you know which part varies!

## Implementation Approach

We'll track:
- When ovulation likely occurred (~day 14 or by counting back luteal length from end)
- Follicular length (start to ovulation)
- Luteal length (ovulation to end)

Then use the **stable luteal phase** for better predictions.

This is computationally cheap - just some arithmetic on dates!
