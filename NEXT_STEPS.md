# Next Steps - Future Improvements

## Planned Enhancements

### Phase 1: Core Features ✅ COMPLETED

- [x] Basic cycle tracking
- [x] Statistical predictions with confidence intervals
- [x] Variance-based prediction ranges
- [x] Tracking quality scores
- [x] Daily updated predictions
- [x] Luteal phase tracking
- [x] Moon phase tracker
- [x] Combined cycle/moon analysis
- [x] Research attribution
- [x] Calendar view with predictions
- [x] Future date predictions
- [x] Comprehensive help system
- [x] Auto-complete previous cycle on new start
- [x] Period end tracking separate from cycle
- [x] **Modular code architecture** (clean, maintainable)
- [x] **Outlier detection** (excludes cycles <18 or >45 days)
- [x] **Input validation** (prevents bad data)
- [x] **Error handling** (graceful, helpful messages)

### Phase 2: Data Model Simplification

#### Status: PARTIALLY COMPLETED ✅
- [x] Refactored into clean modules
- [x] Cycle class with validation
- [x] Outlier handling
- [x] Better data validation
- [ ] Full CSV schema simplification (deferred)

The code is now well-organized in 5 modules instead of 1 monolith.
Further CSV simplification can wait.

### Phase 3: Data Export & Visualisation

#### Export Functionality
- [ ] Export cycle data to JSON
- [ ] Export to CSV for external analysis
- [ ] Generate reports (text/markdown format)
- [ ] Backup/restore functionality

#### Basic Visualization
- [ ] ASCII calendar view showing cycle days
- [ ] Simple bar chart of cycle lengths
- [ ] Moon phase timeline
- [ ] Combined cycle/moon visualization

**Complexity:** Low  
**Dependencies:** None (use ASCII art) or matplotlib for charts  
**Why:** Help users visualize patterns over time

### Phase 3: Advanced Predictions

#### Pattern Detection
- [ ] Detect cycle length trends (getting longer/shorter)
- [ ] Identify irregular cycles (anomaly detection)
- [ ] Seasonal pattern analysis
- [ ] Multi-cycle pattern recognition

#### Enhanced Predictions
- [ ] Predict ovulation based on luteal phase stability
- [ ] Fertility window estimation (educational only!)
- [ ] Long-term cycle forecasting (next 3-6 months)
- [ ] Prediction accuracy scoring (how well past predictions matched reality)

**Complexity:** Medium  
**Dependencies:** More statistical functions  
**Why:** More accurate predictions as data accumulates

### Phase 4: Symptom Tracking (Optional)

#### Basic Symptom Logging
- [ ] Log symptoms per day (mood, energy, pain levels)
- [ ] Predefined symptom list + custom entries
- [ ] Symptom trends by cycle phase
- [ ] Correlation with moon phases

#### Symptom Analysis
- [ ] Most common symptoms per phase
- [ ] Symptom severity tracking
- [ ] Pattern detection (e.g., "headaches always luteal phase")
- [ ] Export symptom data

**Complexity:** Medium  
**Dependencies:** Extend CSV schema  
**Why:** Holistic tracking, pattern awareness

**Note:** Keep optional - not everyone wants to track symptoms

### Phase 5: Advanced Moon Analysis

#### Enhanced Moon Features
- [ ] Moon rise/set times (location-specific)
- [ ] Lunar eclipse predictions
- [ ] Moon sign tracking (astrological, optional)
- [ ] Historical moon phase lookup

#### Advanced Correlations
- [ ] Statistical significance testing (chi-square test)
- [ ] Long-term pattern stability analysis
- [ ] Cycle length variation by moon phase
- [ ] Generate correlation confidence scores

**Complexity:** Medium-High  
**Dependencies:** More astronomical calculations  
**Why:** For those deeply interested in moon correlations

### Phase 6: User Experience Improvements

#### Better Output
- [ ] Color support (if terminal supports it)
- [ ] Customizable display formats
- [ ] Interactive mode (guided setup)
- [ ] Progress bars for longer operations

#### Configuration
- [ ] User preferences file (defaults, display options)
- [ ] Multiple profiles (track for multiple people)
- [ ] Custom phase definitions
- [ ] Configurable prediction algorithms

**Complexity:** Low-Medium  
**Dependencies:** Config file management  
**Why:** More personalized experience

### Phase 7: Data Analysis Tools

#### Retrospective Analysis
- [ ] "Cycle report" command (summary of all tracked cycles)
- [ ] Average cycle stats over different time periods
- [ ] Compare current cycle to historical average
- [ ] Identify most/least regular periods

#### Advanced Statistics
- [ ] Cycle length distribution analysis
- [ ] Moving averages
- [ ] Trend analysis (linear regression)
- [ ] Outlier detection and explanation

**Complexity:** Medium  
**Dependencies:** More statistical functions  
**Why:** Understand long-term patterns

### Phase 8: Integration & Automation

#### Reminders
- [ ] Desktop notifications (when cycle is due)
- [ ] Reminder to track cycle end
- [ ] Warning about low tracking quality
- [ ] Notification when prediction confidence is low

#### Import/Export
- [ ] Import from other apps (Clue, Flo, etc.)
- [ ] Export to calendar format (iCal)
- [ ] Sync between devices (via file sharing, no cloud)
- [ ] Import historical data from CSV

**Complexity:** Medium-High  
**Dependencies:** Platform-specific notification APIs  
**Why:** Better integration with daily workflow

### Phase 9: Educational Content

#### Built-in Help
- [ ] Explain cycle phases in detail
- [ ] Educational content about fertility
- [ ] Myth-busting about moon cycles
- [ ] Links to medical resources

#### Terminology
- [ ] Glossary command
- [ ] Explain statistical terms
- [ ] Guide to understanding predictions
- [ ] FAQ section

**Complexity:** Low  
**Dependencies:** Just documentation  
**Why:** Empower users with knowledge

### Phase 10: Advanced Features (Far Future)

#### Machine Learning (Optional)
- [ ] Personal prediction model (learns your unique patterns)
- [ ] Symptom prediction based on phase
- [ ] Cycle irregularity prediction
- [ ] Lifestyle factor correlation

**Complexity:** High  
**Dependencies:** ML libraries (scikit-learn)  
**Why:** Highly personalized predictions  
**Caveat:** Only useful with lots of data (1+ year)

#### Community Features (Privacy-Preserving)
- [ ] Anonymous aggregate statistics
- [ ] Compare your cycle to population averages
- [ ] Differential privacy for data sharing
- [ ] Opt-in research participation

**Complexity:** Very High  
**Dependencies:** Backend infrastructure  
**Why:** Research contribution while preserving privacy  
**Caveat:** Major project, may not align with privacy-first goals

## Prioritization Criteria

When deciding what to build next, consider:

1. **User Value**: Does it help users understand their bodies better?
2. **Privacy**: Does it maintain data sovereignty?
3. **Complexity**: Can it be done with simple code?
4. **Independence**: Does it keep tools modular/optional?
5. **Science**: Is it based on research or evidence?

## Recommended Next Steps

### Short Term (Next 1-2 months)
1. **Export functionality** - Let users back up their data
2. **ASCII visualizations** - Simple cycle calendar view
3. **Improved help text** - Make commands more discoverable

### Medium Term (3-6 months)
1. **Symptom tracking** (optional module)
2. **Advanced pattern detection**
3. **Better predictions** as data accumulates

### Long Term (6+ months)
1. **Visualization tools** (if there's interest)
2. **Import from other apps**
3. **Desktop notifications**

## Non-Goals

Things we explicitly **won't** build:

❌ **Cloud sync** - Defeats privacy purpose  
❌ **Mobile app** - CLI focus  
❌ **Account system** - No accounts, no tracking  
❌ **Ads or monetization** - Free and open source  
❌ **Social features** - Personal tool only  
❌ **AI predictions** - Keep it simple and explainable  

## Contributing

If you want to implement any of these features:

1. Open an issue to discuss approach
2. Keep code simple and efficient
3. Maintain modularity (features should be optional)
4. Add tests for new functionality
5. Update documentation

## Current Status

**What works now:**
- ✅ Full cycle tracking with statistics
- ✅ Moon phase calculations
- ✅ Combined analysis
- ✅ Comprehensive documentation
- ✅ Research attribution
- ✅ Privacy-preserving design

**What needs work:**
- Better onboarding experience
- More visualization options
- Export/backup functionality
- Symptom tracking

**Overall:** Solid foundation, ready for enhancements!
