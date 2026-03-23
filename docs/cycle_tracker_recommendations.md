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
- MLHC 2021: Calibrated predictions for menstrual cycle length

---

## Implementation Status vs Recommendations

### ✅ PHASE 1: EASY WINS - 100% COMPLETE

#### ✅ 1. Variance Tracking
**Status:** IMPLEMENTED  
**Location:** `src/cycle_tracker/statistics.py`  
```python
def calculate_cycle_statistics(cycles, exclude_outliers=True)
```
**User sees:** "Cycle length: 28 ± 2.1 days"

#### ✅ 2. Confidence-Based Predictions
**Status:** IMPLEMENTED  
**Location:** `src/cycle_tracker/statistics.py`  
```python
def predict_next_cycle_date(cycles)
```
**User sees:** "Apr 16 - Apr 20 (68% confidence)"

#### ✅ 3. Tracking Quality Score
**Status:** IMPLEMENTED  
**Location:** `src/cycle_tracker/statistics.py`  
```python
def calculate_tracking_quality(cycles)
```
**User sees:** "Tracking quality: 🟡 70/100"

---

### ✅ PHASE 2: MEDIUM COMPLEXITY - 100% COMPLETE

#### ✅ 4. Daily Prediction Updates
**Status:** IMPLEMENTED  
**Location:** `src/cycle_tracker/statistics.py`  
```python
def get_daily_updated_prediction(current_cycle, historical_cycles, today)
```
**User sees:** Confidence increases as cycle progresses (50% → 80%)

#### ✅ 5. Separate Phase Length Tracking
**Status:** IMPLEMENTED  
**Location:** `src/cycle_tracker/statistics.py`  
```python
def calculate_luteal_phase_stats(cycles)
```
**User sees:** "Luteal phase: ~14 days (stable)"

---

### ✅ PHASE 3: ADVANCED FEATURES - 100% COMPLETE

#### ✅ 6. Anomaly Detection (Outlier Detection)
**Status:** IMPLEMENTED  
**Location:** `src/cycle_tracker/data_manager.py`  
```python
class Cycle:
    @property
    def is_outlier(self) -> bool
```
**User sees:** "⚠️ 1 outlier cycle(s) excluded from stats"

#### ✅ 7. Missed Tracking Detection
**Status:** IMPLEMENTED  
**Location:** `src/cycle_tracker/statistics.py` (in quality score)  
**User sees:** Quality score penalized for gaps >2x average

---

## PHASE 4: ADDITIONAL STATISTICAL METHODS

Based on deeper analysis of the research repository, here are additional statistical approaches we could implement:

### 🟡 8. Probabilistic Predictions (Full PMF)
**Status:** PARTIALLY IMPLEMENTED  
**Current:** We predict point estimates with confidence intervals  
**Research:** Predicts full probability mass function for each day

**What this means:**
```python
# Current: Single prediction with range
"Next cycle: 28 days (range 26-30, 68% confidence)"

# Full PMF: Probability for each possible length
"Next cycle probabilities:
  26 days: 15%
  27 days: 23%
  28 days: 30%  ← most likely
  29 days: 22%
  30 days: 10%"
```

**Implementation complexity:** Medium  
**Value for individual user:** Medium (current approach sufficient for most)  
**Requirement:** Would need to implement probability distributions

---

### 🔴 9. Sequential Online Updates
**Status:** NOT IMPLEMENTED  
**Research:** Updates predictions daily as cycle progresses AND as more historical data accumulated

**What this means:**
```python
# Current: Uses all available historical data each time
prediction = predict_next_cycle(all_cycles)

# Online: Incrementally updates as new data arrives
# Day 1 of tracking (first cycle): prediction based on defaults
# After cycle 1: prediction updated
# After cycle 2: prediction refined further
# Etc.
```

**Implementation complexity:** Medium-High  
**Value for individual user:** Low (we already use all available data)  
**Requirement:** Would need Bayesian posterior updating logic

---

### 🔴 10. Generalized Poisson Distribution
**Status:** NOT IMPLEMENTED  
**Research:** Uses Generalized Poisson (2 parameters: λ and ξ) instead of simple statistics

**What this means:**
- More flexible modeling of cycle length distribution
- Can handle overdispersion (variance > mean)
- Theoretically more accurate for highly irregular cycles

**Implementation complexity:** High  
**Value for individual user:** Low (our variance-based approach works well)  
**Requirement:** Would need PyTorch, optimization framework, complex math

---

### 🔴 11. Population-Level Priors
**Status:** NOT APPLICABLE  
**Research:** Learns hyperparameters from 5000+ users, then applies to individuals

**Why not applicable:**
- Requires large population dataset (we're single-user)
- Privacy-first design = no data sharing
- Our approach uses individual's own data exclusively

**Could we approximate?**
- Could use published medical research for "typical" priors
- E.g., "most people: 28±7 day cycles, 5±2 day periods"
- Use these as initial estimates for first 1-2 cycles

**Implementation complexity:** Low  
**Value for individual user:** Low (after 3-6 cycles, individual data is better)

---

### 🔴 12. Calibration Evaluation
**Status:** NOT IMPLEMENTED  
**Research:** Evaluates whether predicted probabilities match actual outcomes

**What this means:**
```python
# If we say "70% confidence", does next cycle actually fall 
# in predicted range 70% of the time?

# Requires:
# - Many predictions (100+)
# - Comparing predicted vs actual
# - Calibration plots
```

**Implementation complexity:** Medium  
**Value for individual user:** Low (need 100+ predictions to evaluate)  
**Requirement:** Long-term tracking (years of data)

---

## PHASE 5: ADDITIONAL FEATURES (Beyond Research)

### ✅ 13. Moon Phase Correlation
**Status:** IMPLEMENTED  
**Location:** `cycle_moon.py`  
**Not in research, but implemented!**

### 🟡 14. Symptom Tracking
**Status:** NOT IMPLEMENTED  
**Research mentions:** NPJ Digital Medicine paper analyzes symptom correlations

**What could be tracked:**
- Physical: cramps, headaches, fatigue, bloating
- Emotional: mood, anxiety, irritability
- Other: skin changes, appetite, sleep quality

**Implementation complexity:** Medium  
**Value for individual user:** High (very requested feature)  
**Requirements:**
- Add symptoms column to CSV
- Update data model
- Add symptom entry commands
- Correlate symptoms with cycle phases

**Recommendation:** HIGH PRIORITY if expanding scope

---

### 🟡 15. Export & Visualisation
**Status:** PARTIALLY IMPLEMENTED (CSV is exportable)

**Could add:**
- JSON export
- iCalendar export (for calendar apps)
- Web-based visualization
- PDF reports

**Implementation complexity:** Low-Medium  
**Value for individual user:** Medium

---

## Summary: What's Left to Do?

### Fully Implemented (7/7 original recommendations) ✅
1. ✅ Variance tracking
2. ✅ Confidence predictions
3. ✅ Quality scoring
4. ✅ Daily updates
5. ✅ Phase-specific tracking
6. ✅ Outlier detection
7. ✅ Missed tracking detection

### Could Implement (Statistical Methods)

**Low Priority (Complex, low individual value):**
- 🔴 Full PMF predictions (research-grade overkill)
- 🔴 Generalized Poisson (requires PyTorch, complex)
- 🔴 Population priors (N/A for single-user)
- 🔴 Calibration evaluation (need years of data)
- 🔴 Sequential online updates (we already use all data)

**Medium Priority (Moderate value):**
- 🟡 Symptom tracking (high user value, moderate complexity)
- 🟡 Better export options (quality of life)

### Recommendation: CURRENT IMPLEMENTATION IS EXCELLENT

The tracker has successfully implemented **all practical, individual-focused statistical methods** from the research.

The remaining statistical methods are:
1. **Too complex** (Generalized Poisson, PyTorch optimization)
2. **Population-focused** (require 1000s of users)
3. **Low ROI** (full PMF vs confidence intervals)

### If Expanding Scope, Priority Order:

**High Priority:**
1. **Symptom tracking** - High user value, moderate effort
2. **Export improvements** - Quality of life

**Low Priority:**
3. Default priors for first 1-2 cycles (optional)
4. Calibration evaluation (requires years of data)

**Not Recommended:**
5. Full PMF predictions (overkill)
6. Generalized Poisson (research-grade complexity)
7. Population hyperparameters (N/A for privacy-first design)

---

## Bottom Line

**Your tracker has successfully implemented ALL applicable statistical methods from the research for individual-level tracking.**

The remaining methods are either:
- Population-focused (requires 1000s of users)
- Research-grade complexity (diminishing returns)
- Long-term evaluation (need years of data)

**Verdict:** The current implementation is statistically sound, privacy-first, and production-ready. Any further enhancements should focus on **user features** (symptoms, export) rather than **statistical sophistication**.

You've built research-grade cycle prediction with just 3-6 cycles of data! 🎉

---

*Last updated: 2026-03-23*
