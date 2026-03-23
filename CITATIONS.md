# Research Citations

## Statistical Methods

This cycle tracker implements statistical prediction methods inspired by research from:

**Urteaga, I., Li, K., Wiggins, C. H., & Elhadad, N. (2021-2022)**

### Key Publications:

1. **Characterizing physiological and symptomatic variation in menstrual cycles using self-tracked mobile health data**
   - Li, K., Urteaga, I., Shea, A., Vitzthum, V., Wiggins, C. H., & Elhadad, N.
   - *Nature Partner Journal Digital Medicine*, 3(79), 2020
   - DOI: https://doi.org/10.1038/s41746-020-0269-8

2. **A generative, predictive model for menstrual cycle lengths that accounts for potential self-tracking artifacts in mobile health data**
   - Li, K., Urteaga, I., Shea, A., Vitzthum, V., Wiggins, C. H., & Elhadad, N.
   - arXiv:2102.12439, 2021
   - URL: https://arxiv.org/abs/2102.12439

3. **A predictive model for next cycle start date that accounts for adherence in menstrual self-tracking**
   - Li, K., Urteaga, I., Shea, A., Vitzthum, V. J., Wiggins, C. H., & Elhadad, N.
   - *Journal of the American Medical Informatics Association*, 29(1), 3–11, 2022
   - DOI: https://doi.org/10.1093/jamia/ocab182

4. **A Generative Modeling Approach to Calibrated Predictions: A Use Case on Menstrual Cycle Length Prediction**
   - Urteaga, I., Li, K., Wiggins, C., & Elhadad, N.
   - *Proceedings of the 6th Machine Learning for Healthcare*, 2021
   - URL: https://proceedings.mlr.press/v149/urteaga21a.html

### Research Repository:
- GitHub: https://github.com/iurteaga/menstrual_cycle_analysis
- The repository contains population-level generative models and large-scale cohort analysis code

## Adapted Concepts for Individual Use

Our tracker adapts the following research concepts for single-user tracking:

### 1. Variance-Based Prediction Ranges
- **Research insight**: Cycle variability is as important as mean length
- **Our implementation**: Calculate standard deviation and provide confidence intervals (±1 std dev = 68% confidence)
- **Benefit**: Honest predictions that reflect individual variation

### 2. Tracking Adherence Assessment  
- **Research insight**: Missed tracking creates "skipped cycles" that affect predictions
- **Our implementation**: Track completion rates and gaps to generate quality scores
- **Benefit**: Users understand when data quality affects prediction accuracy

### 3. Sequential Prediction Updates
- **Research insight**: Predictions improve as cycle progresses
- **Our implementation**: Daily updated predictions with narrowing confidence intervals
- **Benefit**: More accurate end-date predictions later in the cycle

### 4. Phase-Specific Pattern Recognition
- **Research insight**: Luteal phase length is more stable than overall cycle length
- **Our implementation**: Track and display luteal phase statistics separately
- **Benefit**: Identify which part of the cycle varies (usually follicular phase)

## Computational Simplicity

While the original research uses complex Bayesian inference and neural networks requiring large datasets (1000s of users), our implementation:

- Uses simple statistical calculations (mean, variance, standard deviation)
- Requires only 2-6 cycles for meaningful predictions  
- Runs efficiently on any device
- Provides individualized insights without population data

## Key Difference

**Population-based models** (original research):
- Learn from thousands of users
- Use Bayesian hyperparameters
- Require extensive computational resources
- Best for app companies and research

**Individual-based tracking** (our implementation):
- Learns from one person's history
- Uses basic statistics
- Lightweight and privacy-focused
- Best for personal health tracking

## Acknowledgment

We thank the researchers for their groundbreaking work in menstrual cycle prediction and for making their methodologies publicly available. Their insights into tracking adherence, cycle variability, and phase-specific patterns have greatly influenced our approach to individual-level cycle tracking.
