"""
Command-line interface for cost tracking and budget management.

This module provides CLI commands for managing API costs and budgets.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..cost_tracker import CostTracker


def cmd_status(args) -> None:
    """Display current cost and budget status."""
    tracker = CostTracker(args.data_file)
    tracker.display_status()


def cmd_set_budget(args) -> None:
    """Set daily or monthly budget."""
    tracker = CostTracker(args.data_file)
    
    if args.daily:
        tracker.set_daily_budget(args.daily)
    
    if args.monthly:
        tracker.set_monthly_budget(args.monthly)
    
    if not args.daily and not args.monthly:
        print("❌ Please specify --daily or --monthly budget amount")
        sys.exit(1)


def cmd_export(args) -> None:
    """Export usage data."""
    tracker = CostTracker(args.data_file)
    
    if args.format == 'csv':
        tracker.export_csv(args.output_file, args.days)
    elif args.format == 'json':
        tracker.export_json(args.output_file, args.days)
    else:
        print(f"❌ Unsupported format: {args.format}")
        sys.exit(1)


def cmd_summary(args) -> None:
    """Show usage summary for specified period."""
    tracker = CostTracker(args.data_file)
    summary = tracker.get_usage_summary(args.days)
    
    print(f"\n📊 Usage Summary - Last {args.days} Days")
    print("="*50)
    print(f"Total API Calls: {summary['total_calls']}")
    print(f"Total Cost: ${summary['total_cost']:.4f}")
    print(f"Total Input Tokens: {summary['total_input_tokens']:,}")
    print(f"Total Output Tokens: {summary['total_output_tokens']:,}")
    print(f"Daily Average Cost: ${summary['daily_average']:.4f}")
    
    if summary['by_model']:
        print(f"\n📱 By Model:")
        for model, stats in summary['by_model'].items():
            model_name = model.replace('claude-3-', '').replace('-20240229', '').replace('-20240307', '').replace('-20241022', '')
            print(f"   {model_name.title()}: {stats['calls']} calls, ${stats['cost']:.4f}")
    
    if summary['by_operation']:
        print(f"\n⚙️  By Operation:")
        for operation, stats in summary['by_operation'].items():
            print(f"   {operation.title()}: {stats['calls']} calls, ${stats['cost']:.4f}")


def cmd_record(args) -> None:
    """Record a test API call (for development/testing)."""
    tracker = CostTracker(args.data_file)
    cost = tracker.record_api_call(args.model, args.input_tokens, args.output_tokens, args.operation)
    print(f"✅ Recorded API call: ${cost:.4f}")
    
    # Show budget status after recording
    status = tracker.check_budget_status()
    if status['warnings']:
        print("\n⚠️  Budget Alerts:")
        for warning in status['warnings']:
            print(f"   {warning}")


def cmd_check_budget(args) -> None:
    """Check if an API call can be made within budget."""
    tracker = CostTracker(args.data_file)
    
    estimated_cost = None
    if args.estimate_cost:
        estimated_cost = args.estimate_cost
    elif args.model and args.input_tokens and args.output_tokens:
        estimated_cost = tracker.calculate_cost(args.model, args.input_tokens, args.output_tokens)
    
    can_proceed, warnings = tracker.can_make_api_call(estimated_cost)
    
    if can_proceed:
        print("✅ API call can proceed within budget limits")
        if estimated_cost:
            print(f"   Estimated cost: ${estimated_cost:.4f}")
    else:
        print("❌ API call would exceed budget limits:")
        for warning in warnings:
            print(f"   {warning}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for cost tracking CLI."""
    parser = argparse.ArgumentParser(
        description="Resume Customizer Cost Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current status
  python -m resume_customizer.cli.cost_cli status
  
  # Set budgets
  python -m resume_customizer.cli.cost_cli set-budget --daily 5.00
  python -m resume_customizer.cli.cost_cli set-budget --monthly 50.00
  
  # Export data
  python -m resume_customizer.cli.cost_cli export csv costs.csv --days 30
  python -m resume_customizer.cli.cost_cli export json report.json
  
  # View summaries
  python -m resume_customizer.cli.cost_cli summary --days 7
  python -m resume_customizer.cli.cost_cli summary --days 30
        """
    )
    
    # Global options
    parser.add_argument('--data-file', type=str, help='Custom path to cost data file')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current cost and budget status')
    status_parser.set_defaults(func=cmd_status)
    
    # Set budget command
    budget_parser = subparsers.add_parser('set-budget', help='Set daily or monthly budget')
    budget_parser.add_argument('--daily', type=float, help='Set daily budget in USD')
    budget_parser.add_argument('--monthly', type=float, help='Set monthly budget in USD')
    budget_parser.set_defaults(func=cmd_set_budget)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export usage data')
    export_parser.add_argument('format', choices=['csv', 'json'], help='Export format')
    export_parser.add_argument('output_file', help='Output file path')
    export_parser.add_argument('--days', type=int, help='Export data from last N days only')
    export_parser.set_defaults(func=cmd_export)
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show usage summary')
    summary_parser.add_argument('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
    summary_parser.set_defaults(func=cmd_summary)
    
    # Record command (for testing)
    record_parser = subparsers.add_parser('record', help='Record a test API call')
    record_parser.add_argument('model', choices=[
        'claude-3-opus-20240229', 
        'claude-3-sonnet-20240229', 
        'claude-3-haiku-20240307',
        'claude-3-5-sonnet-20241022'
    ], help='Claude model used')
    record_parser.add_argument('input_tokens', type=int, help='Number of input tokens')
    record_parser.add_argument('output_tokens', type=int, help='Number of output tokens')
    record_parser.add_argument('--operation', default='test', help='Operation type (default: test)')
    record_parser.set_defaults(func=cmd_record)
    
    # Check budget command
    check_parser = subparsers.add_parser('check-budget', help='Check if API call is within budget')
    check_parser.add_argument('--estimate-cost', type=float, help='Estimated cost in USD')
    check_parser.add_argument('--model', choices=[
        'claude-3-opus-20240229', 
        'claude-3-sonnet-20240229', 
        'claude-3-haiku-20240307',
        'claude-3-5-sonnet-20241022'
    ], help='Claude model for cost calculation')
    check_parser.add_argument('--input-tokens', type=int, help='Number of input tokens')
    check_parser.add_argument('--output-tokens', type=int, help='Number of output tokens')
    check_parser.set_defaults(func=cmd_check_budget)
    
    return parser


def main() -> None:
    """Main entry point for the cost tracking CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()