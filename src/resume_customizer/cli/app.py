# ABOUTME: Click CLI application for resume customization
# ABOUTME: Provides command-line interface with argument parsing and progress display

"""Command-line interface for the resume customizer."""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import click
from pydantic import ValidationError

from resume_customizer.config import Settings
from resume_customizer.core.customizer import ResumeCustomizer
from resume_customizer.utils.logging import get_logger
from resume_customizer.cli.progress import ProgressDisplay, ProgressStep, create_progress_callback
from resume_customizer.cost_tracker import CostTracker


logger = get_logger(__name__)


@click.group()
@click.version_option(version='0.1.0', prog_name='resume-customizer')
def cli() -> None:
    """AI-powered resume customization tool using Claude Code SDK."""
    pass


@cli.command()
@click.option(
    '--resume', '-r',
    type=click.Path(exists=False),
    required=True,
    help='Path to your resume file (markdown format)'
)
@click.option(
    '--job', '-j',
    type=click.Path(exists=False),
    required=True,
    help='Path to the job description file (markdown format)'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output path for customized resume (default: customized_[timestamp].md)'
)
@click.option(
    '--iterations', '-i',
    type=click.IntRange(1, 10),
    default=3,
    help='Number of refinement iterations (1-10, default: 3)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed progress information'
)
@click.option(
    '--skip-budget-check',
    is_flag=True,
    help='Skip budget validation before API calls'
)
def customize(
    resume: str,
    job: str,
    output: Optional[str],
    iterations: int,
    verbose: bool,
    skip_budget_check: bool
) -> None:
    """Customize a resume for a specific job application.
    
    This command reads your resume and a job description, then uses Claude
    to create a customized version that highlights relevant experience and
    includes important keywords.
    
    Example:
        resume-customizer customize -r resume.md -j job.md -o custom.md
    """
    # Validate input files exist
    if not Path(resume).exists():
        click.echo(click.style('✗ Error: Resume file not found: ', fg='red') + resume, err=True)
        sys.exit(1)
    
    if not Path(job).exists():
        click.echo(click.style('✗ Error: Job description file not found: ', fg='red') + job, err=True)
        sys.exit(1)
    
    # Generate default output path if not provided
    if not output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = f'customized_{timestamp}.md'
        click.echo(f'Using default output path: {output}')
    
    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        click.echo(
            click.style('✗ Error: ', fg='red') + 
            'ANTHROPIC_API_KEY environment variable not set.\n' +
            'Please set it with: export ANTHROPIC_API_KEY="your-api-key"',
            err=True
        )
        sys.exit(1)
    
    try:
        # Initialize cost tracker
        cost_tracker = CostTracker()
        
        # Check budget before proceeding (unless skipped)
        if not skip_budget_check:
            can_proceed, warnings = cost_tracker.can_make_api_call()
            if not can_proceed:
                click.echo(click.style('✗ Budget Check Failed:', fg='red', bold=True))
                for warning in warnings:
                    click.echo(f'  {warning}')
                click.echo('\nUse --skip-budget-check to override budget limits.')
                sys.exit(1)
            elif warnings:
                click.echo(click.style('⚠️  Budget Warnings:', fg='yellow', bold=True))
                for warning in warnings:
                    click.echo(f'  {warning}')
                click.echo()
        
        # Create settings
        settings = Settings(max_iterations=iterations)
        
        # Create customizer
        customizer = ResumeCustomizer(settings)
        
        # Show initial message
        click.echo(click.style('Resume Customizer', fg='green', bold=True))
        click.echo(f'Resume: {resume}')
        click.echo(f'Job Description: {job}')
        click.echo(f'Output: {output}')
        click.echo(f'Iterations: {iterations}')
        click.echo()
        
        # Use ProgressDisplay for better progress tracking
        with ProgressDisplay(verbose=verbose) as progress:
            # Create progress callback
            progress_callback = create_progress_callback(progress)
            
            # Start with initialization
            progress.update(ProgressStep.INITIALIZING)
            
            # Run async function
            result = asyncio.run(
                customizer.customize(
                    resume_path=resume,
                    job_description_path=job,
                    output_path=output,
                    progress_callback=progress_callback
                )
            )
            
            # Mark as completed
            progress.update(ProgressStep.COMPLETED)
        
        # Show success message
        click.echo()
        click.echo(click.style('✓ Success!', fg='green', bold=True))
        click.echo(f'Customized resume saved to: {result}')
        
    except ValidationError as e:
        click.echo(click.style('✗ Configuration Error: ', fg='red') + str(e), err=True)
        sys.exit(1)
    
    except FileNotFoundError as e:
        click.echo(click.style('✗ File Error: ', fg='red') + str(e), err=True)
        sys.exit(1)
    
    except Exception as e:
        click.echo(click.style('✗ Error: ', fg='red') + str(e), err=True)
        logger.error(f"Customization failed: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.group()
def cost() -> None:
    """Cost tracking and budget management commands."""
    pass


@cost.command('status')
def cost_status() -> None:
    """Show current cost and budget status."""
    tracker = CostTracker()
    tracker.display_status()


@cost.command('set-budget')
@click.option('--daily', type=float, help='Set daily budget in USD')
@click.option('--monthly', type=float, help='Set monthly budget in USD')
def cost_set_budget(daily: Optional[float], monthly: Optional[float]) -> None:
    """Set daily or monthly spending budget."""
    if not daily and not monthly:
        click.echo(click.style('✗ Error: ', fg='red') + 'Please specify --daily or --monthly budget amount')
        sys.exit(1)
    
    tracker = CostTracker()
    
    if daily:
        tracker.set_daily_budget(daily)
    
    if monthly:
        tracker.set_monthly_budget(monthly)


@cost.command('export')
@click.argument('format', type=click.Choice(['csv', 'json']))
@click.argument('output-file', type=click.Path())
@click.option('--days', type=int, help='Export data from last N days only')
def cost_export(format: str, output_file: str, days: Optional[int]) -> None:
    """Export usage data to CSV or JSON format."""
    tracker = CostTracker()
    
    if format == 'csv':
        tracker.export_csv(output_file, days)
    elif format == 'json':
        tracker.export_json(output_file, days)


@cost.command('summary')
@click.option('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
def cost_summary(days: int) -> None:
    """Show usage summary for specified period."""
    tracker = CostTracker()
    summary = tracker.get_usage_summary(days)
    
    click.echo(click.style(f'📊 Usage Summary - Last {days} Days', fg='blue', bold=True))
    click.echo('=' * 50)
    click.echo(f'Total API Calls: {summary["total_calls"]}')
    click.echo(f'Total Cost: ${summary["total_cost"]:.4f}')
    click.echo(f'Total Input Tokens: {summary["total_input_tokens"]:,}')
    click.echo(f'Total Output Tokens: {summary["total_output_tokens"]:,}')
    click.echo(f'Daily Average Cost: ${summary["daily_average"]:.4f}')
    
    if summary['by_model']:
        click.echo(click.style('\n📱 By Model:', fg='cyan'))
        for model, stats in summary['by_model'].items():
            model_name = model.replace('claude-3-', '').replace('-20240229', '').replace('-20240307', '').replace('-20241022', '')
            click.echo(f'   {model_name.title()}: {stats["calls"]} calls, ${stats["cost"]:.4f}')
    
    if summary['by_operation']:
        click.echo(click.style('\n⚙️  By Operation:', fg='cyan'))
        for operation, stats in summary['by_operation'].items():
            click.echo(f'   {operation.title()}: {stats["calls"]} calls, ${stats["cost"]:.4f}')


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()