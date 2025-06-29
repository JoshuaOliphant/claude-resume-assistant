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


logger = get_logger(__name__)


@click.group()
@click.version_option(version='0.1.0', prog_name='resume-customizer')
def cli():
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
def customize(
    resume: str,
    job: str,
    output: Optional[str],
    iterations: int,
    verbose: bool
):
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
        # Create settings
        settings = Settings(max_iterations=iterations)
        
        # Create customizer
        customizer = ResumeCustomizer(settings)
        
        # Progress callback for verbose mode
        def progress_callback(message: str):
            if verbose:
                click.echo(click.style('→ ', fg='blue') + message)
        
        # Show initial message
        click.echo(click.style('Resume Customizer', fg='green', bold=True))
        click.echo(f'Resume: {resume}')
        click.echo(f'Job Description: {job}')
        click.echo(f'Output: {output}')
        click.echo(f'Iterations: {iterations}')
        click.echo()
        
        # Run customization with progress spinner
        with click.progressbar(
            length=1,
            label='Customizing resume',
            bar_template='%(label)s  %(bar)s',
            show_percent=False,
            show_pos=False
        ) as bar:
            # Run async function
            result = asyncio.run(
                customizer.customize(
                    resume_path=resume,
                    job_description_path=job,
                    output_path=output,
                    progress_callback=progress_callback
                )
            )
            bar.update(1)
        
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


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()