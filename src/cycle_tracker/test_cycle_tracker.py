#!/usr/bin/env python3
"""
Comprehensive tests for cycle tracker functionality
Tests the modular architecture: data_manager, statistics, predictions
"""

import sys
from datetime import datetime, date
from pathlib import Path
import tempfile

# Import modules from the modular architecture
sys.path.insert(0, str(Path(__file__).parent))
from data_manager import Cycle, save_cycles, load_cycles, DATA_FILE as ORIGINAL_DATA_FILE
from statistics import (
    calculate_cycle_statistics,
    calculate_average_period_length,
    calculate_tracking_quality,
    predict_next_cycle_date,
    get_valid_cycles
)
from predictions import get_current_phase, predict_phase_on_date


class TestData:
    """Helper class to create test cycles"""
    
    @staticmethod
    def create_regular_cycles():
        """Create 3 regular 28-day cycles"""
        return [
            Cycle(date(2026, 1, 1), date(2026, 1, 28), 5),   # 28 days (Jan 1-28)
            Cycle(date(2026, 1, 29), date(2026, 2, 25), 5),  # 28 days (Jan 29-Feb 25)
            Cycle(date(2026, 2, 26), date(2026, 3, 25), 6),  # 28 days (Feb 26-Mar 25)
        ]
    
    @staticmethod
    def create_varied_cycles():
        """Create cycles with varying lengths (26, 28, 30 days)"""
        return [
            Cycle(date(2026, 1, 1), date(2026, 1, 26), 5),   # 26 days
            Cycle(date(2026, 1, 27), date(2026, 2, 23), 5),  # 28 days
            Cycle(date(2026, 2, 24), date(2026, 3, 25), 5),  # 30 days
        ]
    
    @staticmethod
    def create_with_outlier():
        """Create cycles including one outlier (65 days)"""
        return [
            Cycle(date(2026, 1, 1), date(2026, 1, 28), 5),   # 28 days
            Cycle(date(2026, 1, 29), date(2026, 4, 4), 5),   # 66 days - outlier!
            Cycle(date(2026, 4, 5), date(2026, 5, 2), 6),    # 28 days
        ]
    
    @staticmethod
    def create_ongoing_cycle():
        """Create 2 complete cycles + 1 ongoing"""
        return [
            Cycle(date(2026, 1, 1), date(2026, 1, 28), 5),   # 28 days
            Cycle(date(2026, 1, 29), date(2026, 2, 25), 5),  # 28 days
            Cycle(date(2026, 2, 26), None, 5),               # Ongoing, period ended
        ]


def test_cycle_statistics():
    """Test cycle length statistics calculation"""
    print("\n📊 Testing Cycle Statistics")
    print("-" * 60)
    
    # Test 1: Regular cycles
    print("  Test 1: Regular 28-day cycles")
    cycles = TestData.create_regular_cycles()
    mean, std = calculate_cycle_statistics(cycles)
    assert mean == 28, f"Expected mean 28, got {mean}"
    assert std == 0.0, f"Expected std 0.0, got {std}"
    print(f"    ✓ Mean: {mean} days, Std: {std:.1f} days")
    
    # Test 2: Varied cycle lengths
    print("  Test 2: Varied cycle lengths (26, 28, 30)")
    cycles = TestData.create_varied_cycles()
    mean, std = calculate_cycle_statistics(cycles)
    assert mean == 28, f"Expected mean 28, got {mean}"
    assert 1.5 < std < 2.5, f"Expected std ~2.0, got {std}"
    print(f"    ✓ Mean: {mean} days, Std: {std:.1f} days")
    
    # Test 3: Outlier exclusion
    print("  Test 3: Outlier exclusion (28, 66, 28 days)")
    cycles = TestData.create_with_outlier()
    mean_with, std_with = calculate_cycle_statistics(cycles, exclude_outliers=False)
    mean_without, std_without = calculate_cycle_statistics(cycles, exclude_outliers=True)
    
    assert mean_with > 35, f"Mean with outliers should be >35, got {mean_with}"
    assert mean_without == 28, f"Mean without outliers should be 28, got {mean_without}"
    print(f"    ✓ With outliers: {mean_with:.1f} ± {std_with:.1f} days")
    print(f"    ✓ Without outliers: {mean_without} ± {std_without:.1f} days")
    
    print("  ✅ Cycle statistics tests passed!")


def test_period_length():
    """Test average period length calculation"""
    print("\n🩸 Testing Period Length Calculation")
    print("-" * 60)
    
    # Test with regular periods
    print("  Test: Regular 5-day periods")
    cycles = TestData.create_regular_cycles()
    avg_period = calculate_average_period_length(cycles)
    expected = round((5 + 5 + 6) / 3)  # Average of 5, 5, 6
    assert avg_period == expected, f"Expected {expected} days, got {avg_period}"
    print(f"    ✓ Average period length: {avg_period} days")
    
    print("  ✅ Period length tests passed!")


def test_tracking_quality():
    """Test tracking quality score"""
    print("\n📈 Testing Tracking Quality Score")
    print("-" * 60)
    
    # Test 1: Good tracking (all periods tracked, completed cycles)
    print("  Test 1: Good tracking (all periods tracked)")
    cycles = TestData.create_regular_cycles()
    quality = calculate_tracking_quality(cycles)
    assert quality >= 60, f"Expected quality ≥60, got {quality}"
    print(f"    ✓ Quality score: {quality}/100")
    
    # Test 2: With outlier
    print("  Test 2: Tracking with outlier")
    cycles = TestData.create_with_outlier()
    quality = calculate_tracking_quality(cycles)
    assert quality < 100, f"Expected quality penalty for outlier, got {quality}"
    print(f"    ✓ Quality score: {quality}/100 (penalized for outlier)")
    
    print("  ✅ Tracking quality tests passed!")


def test_phase_detection():
    """Test current phase detection"""
    print("\n🔍 Testing Phase Detection")
    print("-" * 60)
    
    # Test 1: Menstrual phase (day 3)
    print("  Test 1: Current phase - menstrual (day 3)")
    cycles = [
        Cycle(date(2026, 3, 21), None, 5),  # Started March 21, period ongoing
    ]
    phase, info = get_current_phase(cycles, today=date(2026, 3, 23))
    assert phase == 'menstrual', f"Expected menstrual, got {phase}"
    print(f"    ✓ Phase: {phase} - {info}")
    
    # Test 2: Follicular phase (day 10)
    print("  Test 2: Current phase - follicular (day 10)")
    cycles = [
        Cycle(date(2026, 3, 1), None, 5),  # Started March 1
    ]
    phase, info = get_current_phase(cycles, today=date(2026, 3, 10))
    assert phase == 'follicular', f"Expected follicular, got {phase}"
    print(f"    ✓ Phase: {phase} - {info}")
    
    # Test 3: Luteal phase (day 20)
    print("  Test 3: Current phase - luteal (day 20)")
    cycles = [
        Cycle(date(2026, 3, 1), None, 5),  # Started March 1
    ]
    phase, info = get_current_phase(cycles, today=date(2026, 3, 20))
    assert phase == 'luteal', f"Expected luteal, got {phase}"
    print(f"    ✓ Phase: {phase} - {info}")
    
    # Test 4: Historical date (previous cycle)
    print("  Test 4: Historical date - find correct cycle")
    cycles = [
        Cycle(date(2026, 2, 1), date(2026, 2, 28), 5),   # Feb cycle (28 days)
        Cycle(date(2026, 3, 1), None, 5),                # March cycle
    ]
    phase, info = get_current_phase(cycles, today=date(2026, 2, 15))
    assert phase == 'luteal', f"Expected luteal (Feb cycle day 15), got {phase}"
    print(f"    ✓ Phase: {phase} - {info}")
    
    print("  ✅ Phase detection tests passed!")


def test_future_predictions():
    """Test future date predictions"""
    print("\n🔮 Testing Future Date Predictions")
    print("-" * 60)
    
    # Test 1: Predict next cycle start
    print("  Test 1: Predict next cycle start")
    cycles = [
        Cycle(date(2026, 1, 1), date(2026, 1, 29), 5),   # 28 days
        Cycle(date(2026, 1, 30), date(2026, 2, 27), 5),  # 28 days
        Cycle(date(2026, 2, 28), None, 5),               # Ongoing from Feb 28
    ]
    
    # Predict phase on March 28 (expected next cycle start)
    phase, info = predict_phase_on_date(cycles, date(2026, 3, 28))
    assert phase in ['menstrual', 'luteal'], f"Expected menstrual or luteal, got {phase}"
    print(f"    ✓ March 28: {phase} - {info}")
    
    # Test 2: Predict phase in April
    print("  Test 2: Predict phase in distant future (April 15)")
    phase, info = predict_phase_on_date(cycles, date(2026, 4, 15))
    assert phase is not None, "Expected a phase prediction"
    print(f"    ✓ April 15: {phase} - {info}")
    
    print("  ✅ Future prediction tests passed!")


def test_next_cycle_prediction():
    """Test next cycle date prediction with confidence"""
    print("\n📅 Testing Next Cycle Date Prediction")
    print("-" * 60)
    
    print("  Test: Predict next cycle with confidence interval")
    cycles = TestData.create_regular_cycles()
    
    earliest, expected, latest = predict_next_cycle_date(cycles)
    
    assert expected is not None, "Expected date should not be None"
    assert earliest is not None, "Earliest date should not be None"
    assert latest is not None, "Latest date should not be None"
    
    print(f"    ✓ Expected: {expected}")
    print(f"    ✓ Range: {earliest} to {latest}")
    
    # Verify range is sensible
    assert earliest <= expected <= latest, "Expected date should be within range"
    
    print("  ✅ Next cycle prediction tests passed!")


def test_outlier_detection():
    """Test outlier flagging"""
    print("\n⚠️  Testing Outlier Detection")
    print("-" * 60)
    
    print("  Test: Identify outlier cycle (66 days)")
    cycles = TestData.create_with_outlier()
    
    # Check that outlier is flagged
    outliers = [c for c in cycles if c.is_outlier]
    normal = [c for c in cycles if not c.is_outlier]
    
    assert len(outliers) == 1, f"Expected 1 outlier, found {len(outliers)}"
    assert outliers[0].cycle_length == 66, "66-day cycle should be flagged"
    assert len(normal) == 2, f"Expected 2 normal cycles, found {len(normal)}"
    
    print(f"    ✓ Found {len(outliers)} outlier(s)")
    print(f"    ✓ Outlier: {outliers[0].cycle_length} days")
    
    # Verify valid cycles excludes outliers
    valid = get_valid_cycles(cycles, exclude_outliers=True)
    assert len(valid) == 2, f"Expected 2 valid cycles, got {len(valid)}"
    
    print("  ✅ Outlier detection tests passed!")


def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("🧪 CYCLE TRACKER TEST SUITE")
    print("=" * 60)
    
    try:
        test_cycle_statistics()
        test_period_length()
        test_tracking_quality()
        test_phase_detection()
        test_future_predictions()
        test_next_cycle_prediction()
        test_outlier_detection()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nSummary:")
        print("  ✓ Cycle statistics (mean, std, outlier exclusion)")
        print("  ✓ Period length calculation")
        print("  ✓ Tracking quality scoring")
        print("  ✓ Phase detection (menstrual, follicular, luteal)")
        print("  ✓ Historical date phase lookup")
        print("  ✓ Future date predictions")
        print("  ✓ Next cycle prediction with confidence")
        print("  ✓ Outlier detection and exclusion")
        print("=" * 60)
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
