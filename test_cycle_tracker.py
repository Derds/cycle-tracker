#!/usr/bin/env python3
"""
Tests for cycle tracker functionality
"""

import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

# Import the cycle tracker module
sys.path.insert(0, str(Path(__file__).parent))
import cycle_tracker

def create_test_data(temp_dir, cycles_data):
    """Create a test CSV file with cycle data"""
    test_file = Path(temp_dir) / ".cycle_tracker_data.csv"
    
    with open(test_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['start_date', 'end_date', 'menstrual_days'])
        writer.writeheader()
        for cycle in cycles_data:
            writer.writerow(cycle)
    
    return test_file

def test_cycle_length_prediction():
    """Test that average cycle length is calculated correctly from historical data"""
    print("Testing cycle length prediction...")
    
    # Create temporary directory for test data
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override the DATA_FILE path for testing
        original_data_file = cycle_tracker.DATA_FILE
        cycle_tracker.DATA_FILE = Path(temp_dir) / ".cycle_tracker_data.csv"
        
        try:
            # Test Case 1: Cycles with average length of 26 days
            print("\n  Test 1: Average cycle length of 26 days")
            cycles_data = [
                {'start_date': '2026-01-01', 'end_date': '2026-01-27', 'menstrual_days': '5'},  # 26 days
                {'start_date': '2026-01-28', 'end_date': '2026-02-23', 'menstrual_days': '5'},  # 26 days
                {'start_date': '2026-02-24', 'end_date': '2026-03-22', 'menstrual_days': '5'},  # 26 days
            ]
            create_test_data(temp_dir, cycles_data)
            
            cycles = cycle_tracker.load_cycles()
            avg_length = cycle_tracker.calculate_average_cycle_length(cycles)
            
            assert avg_length == 26, f"Expected 26 days, got {avg_length}"
            print(f"    ✓ Average cycle length: {avg_length} days")
            
            # Test Case 2: Cycles with average length of 30 days
            print("\n  Test 2: Average cycle length of 30 days")
            cycles_data = [
                {'start_date': '2026-01-01', 'end_date': '2026-01-31', 'menstrual_days': '5'},  # 30 days
                {'start_date': '2026-02-01', 'end_date': '2026-03-03', 'menstrual_days': '5'},  # 30 days
                {'start_date': '2026-03-04', 'end_date': '2026-04-03', 'menstrual_days': '4'},  # 30 days
            ]
            create_test_data(temp_dir, cycles_data)
            
            cycles = cycle_tracker.load_cycles()
            avg_length = cycle_tracker.calculate_average_cycle_length(cycles)
            
            assert avg_length == 30, f"Expected 30 days, got {avg_length}"
            print(f"    ✓ Average cycle length: {avg_length} days")
            
            # Test Case 3: Mixed cycle lengths
            print("\n  Test 3: Mixed cycle lengths (28, 26, 30 days)")
            cycles_data = [
                {'start_date': '2026-01-01', 'end_date': '2026-01-29', 'menstrual_days': '5'},  # 28 days
                {'start_date': '2026-01-30', 'end_date': '2026-02-25', 'menstrual_days': '5'},  # 26 days
                {'start_date': '2026-02-26', 'end_date': '2026-03-28', 'menstrual_days': '5'},  # 30 days
            ]
            create_test_data(temp_dir, cycles_data)
            
            cycles = cycle_tracker.load_cycles()
            avg_length = cycle_tracker.calculate_average_cycle_length(cycles)
            expected = round((28 + 26 + 30) / 3)
            
            assert avg_length == expected, f"Expected {expected} days, got {avg_length}"
            print(f"    ✓ Average cycle length: {avg_length} days")
            
            # Test Case 4: Check prediction for next cycle
            print("\n  Test 4: Predict when next cycle is due (26-day average)")
            cycles_data = [
                {'start_date': '2026-01-01', 'end_date': '2026-01-27', 'menstrual_days': '5'},  # 26 days
                {'start_date': '2026-01-28', 'end_date': '2026-02-23', 'menstrual_days': '5'},  # 26 days
                {'start_date': '2026-02-24', 'end_date': '2026-03-22', 'menstrual_days': '5'},  # 26 days, ended March 22
            ]
            create_test_data(temp_dir, cycles_data)
            
            cycles = cycle_tracker.load_cycles()
            # Expected next cycle start: March 23 (day after last cycle ended)
            today = datetime.strptime('2026-03-23', '%Y-%m-%d').date()
            message = cycle_tracker.check_cycle_due(today, cycles)
            
            print(f"    ✓ Prediction message: {message}")
            assert "due" in message.lower() or "expected" in message.lower(), "Should indicate cycle is due"
            
            # Test Case 5: Default cycle length when no completed cycles
            print("\n  Test 5: Default cycle length with no completed cycles")
            cycles_data = [
                {'start_date': '2026-03-01', 'end_date': '', 'menstrual_days': '5'},  # Ongoing cycle
            ]
            create_test_data(temp_dir, cycles_data)
            
            cycles = cycle_tracker.load_cycles()
            avg_length = cycle_tracker.calculate_average_cycle_length(cycles)
            
            assert avg_length == cycle_tracker.DEFAULT_CYCLE_LENGTH, f"Expected default {cycle_tracker.DEFAULT_CYCLE_LENGTH} days, got {avg_length}"
            print(f"    ✓ Using default cycle length: {avg_length} days")
            
            print("\n✅ All cycle length prediction tests passed!")
            
        finally:
            # Restore original DATA_FILE path
            cycle_tracker.DATA_FILE = original_data_file

def test_menstrual_days_calculation():
    """Test that average menstrual days are calculated correctly"""
    print("\nTesting menstrual days calculation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_data_file = cycle_tracker.DATA_FILE
        cycle_tracker.DATA_FILE = Path(temp_dir) / ".cycle_tracker_data.csv"
        
        try:
            # Test with varying menstrual phase lengths
            print("\n  Test: Average menstrual phase length (4, 5, 5 days)")
            cycles_data = [
                {'start_date': '2026-01-01', 'end_date': '2026-01-27', 'menstrual_days': '4'},
                {'start_date': '2026-01-28', 'end_date': '2026-02-23', 'menstrual_days': '5'},
                {'start_date': '2026-02-24', 'end_date': '', 'menstrual_days': '5'},  # Current cycle
            ]
            create_test_data(temp_dir, cycles_data)
            
            cycles = cycle_tracker.load_cycles()
            avg_menstrual = cycle_tracker.calculate_average_menstrual_days(cycles)
            expected = round((4 + 5) / 2)  # Exclude current cycle
            
            assert avg_menstrual == expected, f"Expected {expected} days, got {avg_menstrual}"
            print(f"    ✓ Average menstrual phase: {avg_menstrual} days")
            
            print("\n✅ All menstrual days calculation tests passed!")
            
        finally:
            cycle_tracker.DATA_FILE = original_data_file

if __name__ == "__main__":
    print("=" * 60)
    print("CYCLE TRACKER TESTS")
    print("=" * 60)
    
    try:
        test_cycle_length_prediction()
        test_menstrual_days_calculation()
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
