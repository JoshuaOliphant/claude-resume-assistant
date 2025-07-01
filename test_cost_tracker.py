#!/usr/bin/env python3
"""
Test script for the cost tracking functionality.

This script demonstrates the features implemented for GitHub issue #8:
- Cost tracking and calculation
- Budget management
- Export functionality
- Usage summaries

Run this script to test the cost tracking features:
    python test_cost_tracker.py
"""

import sys
import os
from pathlib import Path
from decimal import Decimal

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from resume_customizer.cost_tracker import CostTracker


def test_cost_calculation():
    """Test cost calculation for different models."""
    print("🧮 Testing Cost Calculation")
    print("=" * 40)
    
    tracker = CostTracker()
    
    # Test different models
    models = [
        'claude-3-opus-20240229',
        'claude-3-sonnet-20240229', 
        'claude-3-haiku-20240307',
        'claude-3-5-sonnet-20241022'
    ]
    
    input_tokens = 1000
    output_tokens = 500
    
    for model in models:
        cost = tracker.calculate_cost(model, input_tokens, output_tokens)
        model_name = model.replace('claude-3-', '').replace('-20240229', '').replace('-20240307', '').replace('-20241022', '')
        print(f"   {model_name.title()}: ${cost:.4f} (1k in, 500 out tokens)")
    
    print()


def test_budget_management():
    """Test budget setting and checking."""
    print("💰 Testing Budget Management")
    print("=" * 40)
    
    tracker = CostTracker()
    
    # Set budgets
    print("Setting budgets...")
    tracker.set_daily_budget(5.00)
    tracker.set_monthly_budget(50.00)
    
    # Check status
    status = tracker.check_budget_status()
    print(f"Daily spending: ${status['daily_spending']:.4f}")
    print(f"Monthly spending: ${status['monthly_spending']:.4f}")
    
    if status['warnings']:
        print("Warnings:")
        for warning in status['warnings']:
            print(f"  {warning}")
    
    print()


def test_api_call_recording():
    """Test recording API calls."""
    print("📞 Testing API Call Recording")
    print("=" * 40)
    
    tracker = CostTracker()
    
    # Record some test API calls
    test_calls = [
        ('claude-3-sonnet-20240229', 1500, 800, 'resume_analysis'),
        ('claude-3-sonnet-20240229', 2000, 1200, 'customization'),
        ('claude-3-haiku-20240307', 800, 400, 'optimization'),
    ]
    
    total_cost = Decimal('0')
    for model, input_tokens, output_tokens, operation in test_calls:
        cost = tracker.record_api_call(model, input_tokens, output_tokens, operation)
        total_cost += cost
        print(f"   Recorded {operation}: ${cost:.4f}")
    
    print(f"   Total recorded: ${total_cost:.4f}")
    print()


def test_usage_summary():
    """Test usage summary generation."""
    print("📊 Testing Usage Summary")
    print("=" * 40)
    
    tracker = CostTracker()
    summary = tracker.get_usage_summary(30)
    
    print(f"Total calls (30 days): {summary['total_calls']}")
    print(f"Total cost: ${summary['total_cost']:.4f}")
    print(f"Daily average: ${summary['daily_average']:.4f}")
    
    if summary['by_model']:
        print("\nBy Model:")
        for model, stats in summary['by_model'].items():
            model_name = model.replace('claude-3-', '').replace('-20240229', '').replace('-20240307', '').replace('-20241022', '')
            print(f"   {model_name.title()}: {stats['calls']} calls, ${stats['cost']:.4f}")
    
    if summary['by_operation']:
        print("\nBy Operation:")
        for operation, stats in summary['by_operation'].items():
            print(f"   {operation.title()}: {stats['calls']} calls, ${stats['cost']:.4f}")
    
    print()


def test_export_functionality():
    """Test data export functionality."""
    print("📁 Testing Export Functionality")
    print("=" * 40)
    
    tracker = CostTracker()
    
    # Test CSV export
    csv_file = "test_costs.csv"
    tracker.export_csv(csv_file, days=30)
    
    if Path(csv_file).exists():
        print(f"   CSV export successful: {csv_file}")
        # Clean up
        Path(csv_file).unlink()
    
    # Test JSON export
    json_file = "test_costs.json"
    tracker.export_json(json_file, days=30)
    
    if Path(json_file).exists():
        print(f"   JSON export successful: {json_file}")
        # Clean up
        Path(json_file).unlink()
    
    print()


def test_budget_enforcement():
    """Test budget enforcement and warnings."""
    print("⚠️  Testing Budget Enforcement")
    print("=" * 40)
    
    tracker = CostTracker()
    
    # Set a very low daily budget for testing
    tracker.set_daily_budget(0.01)
    
    # Check if we can make an API call
    can_proceed, warnings = tracker.can_make_api_call(Decimal('0.02'))
    
    print(f"Can make API call (estimated $0.02): {can_proceed}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  {warning}")
    
    # Reset budget for normal use
    tracker.set_daily_budget(5.00)
    print()


def main():
    """Run all tests."""
    print("🧪 COST TRACKER FUNCTIONALITY TEST")
    print("=" * 60)
    print("Testing GitHub issue #8 implementation:")
    print("- Cost budgets and export functionality")
    print("=" * 60)
    print()
    
    try:
        test_cost_calculation()
        test_budget_management()
        test_api_call_recording()
        test_usage_summary()
        test_export_functionality()
        test_budget_enforcement()
        
        print("✅ All tests completed successfully!")
        print("\n💡 To use the cost tracker:")
        print("   python cost_tracker_cli.py status")
        print("   python cost_tracker_cli.py set-budget --daily 5.00")
        print("   python cost_tracker_cli.py export csv costs.csv")
        print("   python resume_customizer.py cost status")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()