"""
Cost tracking module for monitoring Claude API usage costs.

This module provides functionality to track API costs, set budgets,
and export usage reports for the resume customizer.

Addresses GitHub issue #8: Add cost budgets and export functionality
"""

import json
import csv
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class APICall:
    """Represents a single API call with cost information."""
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: Decimal
    operation: str  # e.g., "resume_analysis", "customization", "optimization"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp,
            'model': self.model,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'cost': float(self.cost),
            'operation': self.operation
        }


class CostTracker:
    """Tracks API costs and manages budgets for resume customization."""
    
    # Claude API pricing (per 1M tokens) - updated as of 2024
    PRICING = {
        'claude-3-opus-20240229': {
            'input': Decimal('15.00'),
            'output': Decimal('75.00')
        },
        'claude-3-sonnet-20240229': {
            'input': Decimal('3.00'),
            'output': Decimal('15.00')
        },
        'claude-3-haiku-20240307': {
            'input': Decimal('0.25'),
            'output': Decimal('1.25')
        },
        'claude-3-5-sonnet-20241022': {
            'input': Decimal('3.00'),
            'output': Decimal('15.00')
        }
    }
    
    def __init__(self, data_file: Optional[Union[str, Path]] = None):
        """Initialize cost tracker with optional data file."""
        self.data_file = Path(data_file) if data_file else Path.home() / '.resume_customizer_costs.json'
        self.calls: List[APICall] = []
        self.daily_budget: Optional[Decimal] = None
        self.monthly_budget: Optional[Decimal] = None
        self.load_data()
    
    def load_data(self) -> None:
        """Load existing cost data from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                # Load API calls
                for call_data in data.get('calls', []):
                    call = APICall(
                        timestamp=call_data['timestamp'],
                        model=call_data['model'],
                        input_tokens=call_data['input_tokens'],
                        output_tokens=call_data['output_tokens'],
                        cost=Decimal(str(call_data['cost'])),
                        operation=call_data['operation']
                    )
                    self.calls.append(call)
                
                # Load budgets
                if 'daily_budget' in data and data['daily_budget']:
                    self.daily_budget = Decimal(str(data['daily_budget']))
                if 'monthly_budget' in data and data['monthly_budget']:
                    self.monthly_budget = Decimal(str(data['monthly_budget']))
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not load cost data: {e}")
                self.calls = []
    
    def save_data(self) -> None:
        """Save cost data to file."""
        data = {
            'calls': [call.to_dict() for call in self.calls],
            'daily_budget': float(self.daily_budget) if self.daily_budget else None,
            'monthly_budget': float(self.monthly_budget) if self.monthly_budget else None,
            'last_updated': datetime.now().isoformat()
        }
        
        # Ensure directory exists
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate cost for an API call."""
        if model not in self.PRICING:
            # Default to Sonnet pricing for unknown models
            model = 'claude-3-sonnet-20240229'
        
        pricing = self.PRICING[model]
        input_cost = (Decimal(input_tokens) / Decimal('1000000')) * pricing['input']
        output_cost = (Decimal(output_tokens) / Decimal('1000000')) * pricing['output']
        
        total_cost = input_cost + output_cost
        return total_cost.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    
    def record_api_call(self, model: str, input_tokens: int, output_tokens: int, 
                       operation: str = "customization") -> Decimal:
        """Record an API call and return the cost."""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        call = APICall(
            timestamp=datetime.now().isoformat(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            operation=operation
        )
        
        self.calls.append(call)
        self.save_data()
        
        return cost
    
    def set_daily_budget(self, budget: Union[float, Decimal]) -> None:
        """Set daily spending budget."""
        self.daily_budget = Decimal(str(budget))
        self.save_data()
        print(f"✅ Daily budget set to ${self.daily_budget:.2f}")
    
    def set_monthly_budget(self, budget: Union[float, Decimal]) -> None:
        """Set monthly spending budget."""
        self.monthly_budget = Decimal(str(budget))
        self.save_data()
        print(f"✅ Monthly budget set to ${self.monthly_budget:.2f}")
    
    def get_daily_spending(self, date: Optional[datetime] = None) -> Decimal:
        """Get total spending for a specific day."""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        daily_total = Decimal('0')
        
        for call in self.calls:
            call_date = datetime.fromisoformat(call.timestamp).strftime('%Y-%m-%d')
            if call_date == date_str:
                daily_total += call.cost
        
        return daily_total
    
    def get_monthly_spending(self, year: Optional[int] = None, month: Optional[int] = None) -> Decimal:
        """Get total spending for a specific month."""
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        
        monthly_total = Decimal('0')
        
        for call in self.calls:
            call_date = datetime.fromisoformat(call.timestamp)
            if call_date.year == year and call_date.month == month:
                monthly_total += call.cost
        
        return monthly_total
    
    def check_budget_status(self) -> Dict:
        """Check current budget status."""
        status = {
            'daily_budget_set': self.daily_budget is not None,
            'monthly_budget_set': self.monthly_budget is not None,
            'daily_spending': self.get_daily_spending(),
            'monthly_spending': self.get_monthly_spending(),
            'daily_budget_exceeded': False,
            'monthly_budget_exceeded': False,
            'warnings': []
        }
        
        if self.daily_budget:
            status['daily_budget'] = self.daily_budget
            status['daily_remaining'] = self.daily_budget - status['daily_spending']
            if status['daily_spending'] >= self.daily_budget:
                status['daily_budget_exceeded'] = True
                status['warnings'].append("❌ Daily budget exceeded")
            elif status['daily_spending'] >= self.daily_budget * Decimal('0.8'):
                status['warnings'].append("⚠️  Daily budget 80% reached")
        
        if self.monthly_budget:
            status['monthly_budget'] = self.monthly_budget
            status['monthly_remaining'] = self.monthly_budget - status['monthly_spending']
            if status['monthly_spending'] >= self.monthly_budget:
                status['monthly_budget_exceeded'] = True
                status['warnings'].append("❌ Monthly budget exceeded")
            elif status['monthly_spending'] >= self.monthly_budget * Decimal('0.8'):
                status['warnings'].append("⚠️  Monthly budget 80% reached")
        
        return status
    
    def can_make_api_call(self, estimated_cost: Optional[Decimal] = None) -> tuple[bool, List[str]]:
        """Check if an API call can be made within budget constraints."""
        status = self.check_budget_status()
        warnings = []
        
        if estimated_cost is None:
            estimated_cost = Decimal('0.01')  # Default small estimate
        
        # Check daily budget
        if self.daily_budget:
            projected_daily = status['daily_spending'] + estimated_cost
            if projected_daily > self.daily_budget:
                warnings.append(f"❌ API call would exceed daily budget (${projected_daily:.4f} > ${self.daily_budget:.2f})")
        
        # Check monthly budget
        if self.monthly_budget:
            projected_monthly = status['monthly_spending'] + estimated_cost
            if projected_monthly > self.monthly_budget:
                warnings.append(f"❌ API call would exceed monthly budget (${projected_monthly:.4f} > ${self.monthly_budget:.2f})")
        
        can_proceed = len(warnings) == 0
        return can_proceed, warnings
    
    def get_usage_summary(self, days: int = 30) -> Dict:
        """Get usage summary for the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_calls = [
            call for call in self.calls
            if datetime.fromisoformat(call.timestamp) >= cutoff_date
        ]
        
        if not filtered_calls:
            return {
                'period_days': days,
                'total_calls': 0,
                'total_cost': Decimal('0'),
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'by_model': {},
                'by_operation': {},
                'daily_average': Decimal('0')
            }
        
        total_cost = sum(call.cost for call in filtered_calls)
        total_input_tokens = sum(call.input_tokens for call in filtered_calls)
        total_output_tokens = sum(call.output_tokens for call in filtered_calls)
        
        # Group by model
        by_model = {}
        for call in filtered_calls:
            if call.model not in by_model:
                by_model[call.model] = {
                    'calls': 0,
                    'cost': Decimal('0'),
                    'input_tokens': 0,
                    'output_tokens': 0
                }
            by_model[call.model]['calls'] += 1
            by_model[call.model]['cost'] += call.cost
            by_model[call.model]['input_tokens'] += call.input_tokens
            by_model[call.model]['output_tokens'] += call.output_tokens
        
        # Group by operation
        by_operation = {}
        for call in filtered_calls:
            if call.operation not in by_operation:
                by_operation[call.operation] = {
                    'calls': 0,
                    'cost': Decimal('0'),
                    'input_tokens': 0,
                    'output_tokens': 0
                }
            by_operation[call.operation]['calls'] += 1
            by_operation[call.operation]['cost'] += call.cost
            by_operation[call.operation]['input_tokens'] += call.input_tokens
            by_operation[call.operation]['output_tokens'] += call.output_tokens
        
        return {
            'period_days': days,
            'total_calls': len(filtered_calls),
            'total_cost': total_cost,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'by_model': {k: {**v, 'cost': float(v['cost'])} for k, v in by_model.items()},
            'by_operation': {k: {**v, 'cost': float(v['cost'])} for k, v in by_operation.items()},
            'daily_average': total_cost / Decimal(days)
        }
    
    def export_csv(self, output_file: Union[str, Path], days: Optional[int] = None) -> None:
        """Export usage data to CSV file."""
        calls_to_export = self.calls
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            calls_to_export = [
                call for call in self.calls
                if datetime.fromisoformat(call.timestamp) >= cutoff_date
            ]
        
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'model', 'operation', 'input_tokens', 
                         'output_tokens', 'cost']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for call in calls_to_export:
                writer.writerow({
                    'timestamp': call.timestamp,
                    'model': call.model,
                    'operation': call.operation,
                    'input_tokens': call.input_tokens,
                    'output_tokens': call.output_tokens,
                    'cost': float(call.cost)
                })
        
        print(f"✅ Exported {len(calls_to_export)} records to {output_file}")
    
    def export_json(self, output_file: Union[str, Path], days: Optional[int] = None) -> None:
        """Export usage data to JSON file."""
        calls_to_export = self.calls
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            calls_to_export = [
                call for call in self.calls
                if datetime.fromisoformat(call.timestamp) >= cutoff_date
            ]
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'period_days': days,
            'summary': self.get_usage_summary(days) if days else self.get_usage_summary(),
            'calls': [call.to_dict() for call in calls_to_export],
            'budgets': {
                'daily_budget': float(self.daily_budget) if self.daily_budget else None,
                'monthly_budget': float(self.monthly_budget) if self.monthly_budget else None
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Exported data to {output_file}")
    
    def display_status(self) -> None:
        """Display current cost and budget status in a formatted way."""
        status = self.check_budget_status()
        
        print("\n" + "="*60)
        print("📊 RESUME CUSTOMIZER - COST TRACKER STATUS")
        print("="*60)
        
        # Total spending
        total_cost = sum(call.cost for call in self.calls)
        print(f"💰 Total Spent: ${total_cost:.4f}")
        print(f"📞 Total API Calls: {len(self.calls)}")
        
        # Today's usage
        print(f"\n📅 Today ({datetime.now().strftime('%Y-%m-%d')}):")
        print(f"   Spent: ${status['daily_spending']:.4f}")
        
        if self.daily_budget:
            remaining = status['daily_remaining']
            percentage = (status['daily_spending'] / self.daily_budget) * 100
            print(f"   Budget: ${self.daily_budget:.2f}")
            print(f"   Remaining: ${remaining:.2f} ({100-percentage:.1f}% left)")
        else:
            print("   Budget: Not set")
        
        # This month's usage
        current_month = datetime.now().strftime('%B %Y')
        print(f"\n📆 This Month ({current_month}):")
        print(f"   Spent: ${status['monthly_spending']:.4f}")
        
        if self.monthly_budget:
            remaining = status['monthly_remaining']
            percentage = (status['monthly_spending'] / self.monthly_budget) * 100
            print(f"   Budget: ${self.monthly_budget:.2f}")
            print(f"   Remaining: ${remaining:.2f} ({100-percentage:.1f}% left)")
        else:
            print("   Budget: Not set")
        
        # Warnings
        if status['warnings']:
            print(f"\n⚠️  BUDGET ALERTS:")
            for warning in status['warnings']:
                print(f"   {warning}")
        
        # Recent activity summary
        summary = self.get_usage_summary(7)
        if summary['total_calls'] > 0:
            print(f"\n📈 Last 7 Days Summary:")
            print(f"   API Calls: {summary['total_calls']}")
            print(f"   Total Cost: ${summary['total_cost']:.4f}")
            print(f"   Daily Average: ${summary['daily_average']:.4f}")
            
            # Top models used
            if summary['by_model']:
                top_model = max(summary['by_model'].items(), key=lambda x: x[1]['calls'])
                print(f"   Most Used Model: {top_model[0]} ({top_model[1]['calls']} calls)")
        
        print("="*60)
        
        # Quick setup tips
        if not self.daily_budget and not self.monthly_budget:
            print("\n💡 TIP: Set budgets to track spending:")
            print("   uv run python -m resume_customizer.cost_tracker set-budget --daily 5.00")
            print("   uv run python -m resume_customizer.cost_tracker set-budget --monthly 50.00")