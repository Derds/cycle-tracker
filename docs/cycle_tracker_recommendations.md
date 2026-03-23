# Analysis of iurteaga/menstrual_cycle_analysis and Recommendations

## What the Research Repository Does

The iurteaga repository implements **population-based generative models** for menstrual cycle prediction:

### Key Approaches:
1. **Generative Statistical Models**: Uses Poisson and Generalized Poisson distributions
2. **Self-tracking Artifact Modeling**: Accounts for missed tracking (skipped cycles)
3. **Population-level Learning**: Learns hyperparameters from large cohorts (5000+ users)
4. **Bayesian Updating**: Uses population priors, then updates with individual data

### Main Papers:
- NPJ Digital Medicine 2020: Characterization of menstrual cycles
- NeurIPS 2020 & arXiv: Generative models accounting for tracking artifacts
- JAMIA 2022: Predictive model for next cycle start date

## Can This Help Your Individual Tracker?

**YES, but with adaptation!** The research has valuable insights for individual use:

### What's Directly Applicable to Your Tracker:

#### 1. **Tracking Adherence Modeling** ⭐⭐⭐
- **The Problem**: Users forget to track cycles → data gaps → bad predictions
- **Their Solution**: Models explicitly account for "skipped cycles" (missed tracking)
- **Your Implementation**: 
  - Add confidence scores based on tracking consistency
  - Warn user when gaps in data reduce prediction accuracy
  - Distinguish between "true long cycle" vs "forgot to track"

#### 2. **Variability Modeling** ⭐⭐⭐
- **The Finding**: Cycle length variance is as important as mean length
- **Your Implementation**:
  - Track not just average cycle length, but variance (standard deviation)
  - Use this to provide prediction ranges: "Next cycle: 26-30 days (68% confidence)"
  - Identify when a cycle is truly irregular vs normal variation

#### 3. **Sequential Prediction Updates** ⭐⭐
- **The Approach**: Update predictions daily as cycle progresses
- **Your Implementation**:
  - Day 1: "Expected cycle length: 28 days"
  - Day 20: "Expected cycle length: 27 days (updated based on current progress)"
  - Day 25: "Cycle likely to end in 1-3 days"

#### 4. **Phase-Specific Patterns** ⭐⭐
- **The Finding**: Menstrual phase length is more stable than full cycle length
- **You Already Do This!** Your tracker already adapts menstrual phase length
- **Enhancement**: Also track follicular and luteal phase lengths separately

### What's NOT Directly Applicable:

❌ **Population Hyperparameters**: The repo needs 1000s of users to learn these
❌ **Complex Bayesian Inference**: Overkill for single-user tracking
❌ **Neural Network Models**: Require lots of data per user

## Practical Enhancements for Your Tracker

### Phase 1: Easy Wins (Immediate)

```python
# 1. Add variance tracking
def calculate_cycle_statistics(cycles):
    """Calculate mean and variance for better predictions"""
    lengths = [(c['end_date'] - c['start_date']).days for c in cycles if c['end_date']]
    if not lengths:
        return DEFAULT_CYCLE_LENGTH, 5  # mean, std_dev
    
    mean = sum(lengths) / len(lengths)
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    std_dev = variance ** 0.5
    
    return round(mean), round(std_dev)

# 2. Confidence-based predictions
def predict_with_confidence(cycles, today):
    """Provide prediction ranges, not just point estimates"""
    mean, std = calculate_cycle_statistics(cycles)
    
    # 68% confidence interval (±1 std dev)
    lower = mean - std
    upper = mean + std
    
    return {
        'expected': mean,
        'range': (lower, upper),
        'confidence': '68%'
    }

# 3. Tracking quality score
def get_tracking_quality(cycles):
    """Score tracking consistency (0-100)"""
    if not cycles:
        return 0
    
    # Check for gaps, regular updates, etc.
    completed = sum(1 for c in cycles if c['end_date'])
    score = (completed / len(cycles)) * 100
    
    return round(score)
```

### Phase 2: Medium Complexity

```python
# 4. Daily prediction updates
def update_prediction_daily(current_cycle, historical_cycles, days_elapsed):
    """Update cycle end prediction as days progress"""
    avg_length = calculate_average_cycle_length(historical_cycles)
    
    # Bayesian-like update: as we progress, narrow the range
    days_remaining = avg_length - days_elapsed
    confidence_factor = days_elapsed / avg_length
    
    # Tighter predictions as we get closer to expected end
    adjusted_std = base_std * (1 - confidence_factor)
    
    return {
        'days_remaining': days_remaining,
        'confidence': confidence_factor * 100,
        'range': (days_remaining - adjusted_std, days_remaining + adjusted_std)
    }

# 5. Separate phase length tracking
def track_phase_lengths(cycles):
    """Track follicular and luteal phase separately"""
    for cycle in cycles:
        if cycle['end_date']:
            cycle_length = (cycle['end_date'] - cycle['start_date']).days
            menstrual_end = cycle['start_date'] + timedelta(days=cycle['menstrual_days'])
            
            # Follicular: start to ~day 14 (ovulation)
            follicular_length = 14
            
            # Luteal: day 14 to end (typically more stable)
            luteal_length = cycle_length - follicular_length
            
            cycle['luteal_days'] = luteal_length
```

### Phase 3: Advanced Features

```python
# 6. Anomaly detection
def detect_irregular_cycle(current_length, historical_cycles):
    """Identify truly irregular cycles vs normal variation"""
    mean, std = calculate_cycle_statistics(historical_cycles)
    
    # More than 2 standard deviations = irregular
    z_score = abs(current_length - mean) / std
    
    if z_score > 2:
        return True, f"This cycle is {z_score:.1f} std deviations from your average"
    return False, "Within normal variation"

# 7. Missed tracking detection
def detect_missed_tracking(cycles):
    """Identify potential missed cycles"""
    for i, cycle in enumerate(cycles[:-1]):
        if not cycle['end_date']:
            continue
        
        next_cycle = cycles[i + 1]
        gap_days = (next_cycle['start_date'] - cycle['end_date']).days
        
        avg_length = calculate_average_cycle_length(cycles)
        
        # If gap is ~2x normal cycle, user might have missed tracking one
        if gap_days > avg_length * 1.5:
            yield {
                'warning': f"Gap of {gap_days} days detected",
                'possible_missed_cycles': gap_days // avg_length,
                'dates': (cycle['end_date'], next_cycle['start_date'])
            }
```

## Recommended Roadmap

### Now (Keep It Simple)
1. ✅ Basic cycle tracking (you have this!)
2. ✅ Average calculations (you have this!)
3. ⬜ Add variance/std dev to predictions
4. ⬜ Prediction ranges instead of point estimates
5. ⬜ Tracking quality score

### Soon (Add Intelligence)
1. Daily prediction updates (gets smarter as cycle progresses)
2. Separate luteal phase tracking (it's more stable!)
3. Simple anomaly detection (flag unusual cycles)
4. Missed tracking warnings

### Later (Advanced)
1. Confidence intervals that narrow over time
2. Symptom tracking (correlate with phases)
3. Multi-cycle pattern detection
4. Export data for personal analysis

## Key Insight from the Research

The most important finding: **The variability between cycles is just as important as the average**.

Your tracker currently uses just the mean. Adding standard deviation would make it much more useful:

**Instead of:**
"Your next cycle will start in 28 days"

**You could say:**
"Your next cycle will likely start in 26-30 days (68% confidence)
Based on 6 previous cycles (tracking quality: 85%)"

This is honest, useful, and doesn't require population data!

## Bottom Line

The research repo is primarily for **population-level insights**, but the statistical approaches (handling variance, tracking adherence, sequential updates) are **highly applicable to individual tracking**.

You don't need 5000 users—you can implement sophisticated individual-level prediction with just **3-6 cycles of good data** per person.
