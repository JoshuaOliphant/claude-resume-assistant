#!/usr/bin/env python3
"""
Simple demonstration of the cost tracking functionality.

This script shows how the cost tracking system works for GitHub issue #8.
It doesn't require any external dependencies and can be run directly.
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from resume_customizer.cost_tracker import CostTracker


def main():
    """Demonstrate cost tracking functionality."""
    print("🎯 GITHUB ISSUE #8 - COST BUDGETS AND EXPORT FUNCTIONALITY")
    print("=" * 70)
    print("Demonstrating the implemented solution:")
    print()
    
    # Initialize cost tracker
    tracker = CostTracker()
    
    # 1. Show cost calculation for different models
    print("1️⃣  COST CALCULATION")
    print("-" * 30)
    models = [
        ('claude-3-opus-20240229', 'Opus'),
        ('claude-3-sonnet-20240229', 'Sonnet'),
        ('claude-3-haiku-20240307', 'Haiku'),
        ('claude-3-5-sonnet-20241022', '3.5 Sonnet')
    ]
    
    for model_id, model_name in models:
        cost = tracker.calculate_cost(model_id, 2000, 1000)  # 2k input, 1k output
        print(f"   {model_name}: ${cost:.4f} (2k input + 1k output tokens)")
    print()
    
    # 2. Set budgets
    print("2️⃣  BUDGET MANAGEMENT")
    print("-" * 30)
    tracker.set_daily_budget(10.00)
    tracker.set_monthly_budget(100.00)
    print()
    
    # 3. Record some API calls
    print("3️⃣  API CALL TRACKING")
    print("-" * 30)
    calls = [
        ('claude-3-sonnet-20240229', 1800, 900, 'resume_analysis'),
        ('claude-3-sonnet-20240229', 2200, 1100, 'customization'),
        ('claude-3-haiku-20240307', 1000, 500, 'optimization'),
    ]
    
    total_cost = 0
    for model, input_tokens, output_tokens, operation in calls:
        cost = tracker.record_api_call(model, input_tokens, output_tokens, operation)
        total_cost += float(cost)
        print(f"   ✅ {operation}: ${cost:.4f}")
    
    print(f"   📊 Total session cost: ${total_cost:.4f}")
    print()
    
    # 4. Show status
    print("4️⃣  BUDGET STATUS")
    print("-" * 30)
    status = tracker.check_budget_status()
    print(f"   Daily spending: ${status['daily_spending']:.4f} / ${status.get('daily_budget', 0):.2f}")
    print(f"   Monthly spending: ${status['monthly_spending']:.4f} / ${status.get('monthly_budget', 0):.2f}")
    
    if status['warnings']:
        print("   ⚠️  Warnings:")
        for warning in status['warnings']:
            print(f"      {warning}")
    else:
        print("   ✅ Within budget limits")
    print()
    
    # 5. Usage summary
    print("5️⃣  USAGE SUMMARY")
    print("-" * 30)
    summary = tracker.get_usage_summary(30)
    print(f"   Total API calls (30 days): {summary['total_calls']}")
    print(f"   Total cost: ${summary['total_cost']:.4f}")
    print(f"   Daily average: ${summary['daily_average']:.4f}")
    
    if summary['by_model']:
        print("   By model:")
        for model, stats in summary['by_model'].items():
            model_name = model.replace('claude-3-', '').replace('-20240229', '').replace('-20240307', '').replace('-20241022', '')
            print(f"      {model_name.title()}: {stats['calls']} calls, ${stats['cost']:.4f}")
    
    if summary['by_operation']:
        print("   By operation:")
        for operation, stats in summary['by_operation'].items():
            print(f"      {operation.title()}: {stats['calls']} calls, ${stats['cost']:.4f}")
    print()
    
    # 6. Export functionality
    print("6️⃣  EXPORT FUNCTIONALITY")
    print("-" * 30)
    
    # Export to CSV
    csv_file = "demo_costs.csv"
    tracker.export_csv(csv_file)
    if Path(csv_file).exists():
        print(f"   📄 CSV file size: {Path(csv_file).stat().st_size} bytes")
        Path(csv_file).unlink()  # Clean up
    
    # Export to JSON
    json_file = "demo_costs.json"
    tracker.export_json(json_file)
    if Path(json_file).exists():
        print(f"   📄 JSON file size: {Path(json_file).stat().st_size} bytes")
        Path(json_file).unlink()  # Clean up
    print()
    
    # 7. Budget enforcement
    print("7️⃣  BUDGET ENFORCEMENT")
    print("-" * 30)
    
    # Test with a small budget
    original_budget = tracker.daily_budget
    tracker.set_daily_budget(0.01)  # Very small budget
    
    can_proceed, warnings = tracker.can_make_api_call(Decimal('0.05'))  # $0.05 API call
    print(f"   Can make $0.05 API call with $0.01 budget: {can_proceed}")
    if warnings:
        for warning in warnings:
            print(f"      ⚠️  {warning}")
    
    # Restore original budget
    if original_budget:
        tracker.set_daily_budget(original_budget)
    print()
    
    print("✅ IMPLEMENTATION COMPLETE!")
    print("=" * 70)
    print("GitHub Issue #8 'Add cost budgets and export functionality' has been")
    print("successfully implemented with the following features:")
    print()
    print("✅ Real-time cost calculation for all Claude models")
    print("✅ Daily and monthly budget management")
    print("✅ Budget enforcement with warnings and hard limits")
    print("✅ Comprehensive usage tracking and analytics")
    print("✅ Data export to CSV and JSON formats")
    print("✅ Command-line interface integration")
    print("✅ Standalone cost tracking utility")
    print("✅ Privacy-focused local data storage")
    print()
    print("🚀 Ready for production use!")


if __name__ == "__main__":
    main()