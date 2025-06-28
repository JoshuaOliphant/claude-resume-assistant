# Resume Customizer

An AI-powered resume customization tool that uses the Claude Code SDK to tailor resumes for specific job applications while maintaining truthfulness and ATS compatibility.

## Overview

This project demonstrates advanced agentic patterns using Claude Code SDK to automate the time-consuming process of customizing resumes for different job applications. It analyzes job requirements and intelligently reorganizes and reframes existing resume content to maximize relevance without fabricating information.

## Project Status

🚧 **Under Development** - Following Test-Driven Development (TDD) approach

See [plan.md](plan.md) for the detailed implementation plan and [todo.md](todo.md) for current progress.

## Planned Features

### Phase 1: CLI Application
- Markdown resume input/output
- Text-based job description parsing
- Intelligent content reorganization
- Keyword optimization
- ATS-friendly formatting
- Configurable optimization iterations

### Phase 2: Web Application
- FastAPI backend
- HTMX + Tailwind CSS frontend
- Real-time customization progress
- Multiple export formats
- Batch processing

## Architecture

The application uses an **Orchestrator-Workers** pattern with **Evaluator-Optimizer** for iterative refinement:

- **Orchestrator**: Coordinates the customization workflow
- **Virtual Sub-agents**: Specialized analysis for different aspects
- **Iterative Refinement**: Multiple passes for optimization
- **Truthfulness Constraint**: Only reorganizes existing information

## Getting Started

### Prerequisites
- Python 3.10+
- uv (for package management)
- Claude API key

### Installation

```bash
# Clone the repository
git clone https://github.com/JoshuaOliphant/claude-resume-assistant.git
cd claude-resume-assistant

# Install uv if not already installed
# See: https://github.com/astral-sh/uv

# Set up the project (coming soon)
uv init
uv add click pydantic claude-code-sdk
```

### Usage (Coming Soon)

```bash
# Basic usage
python -m resume_customizer -r resume.md -j job_description.txt

# With custom iterations
python -m resume_customizer -r resume.md -j job_description.txt --iterations 5

# Verbose mode
python -m resume_customizer -r resume.md -j job.txt --verbose
```

## Documentation

- [Specification](spec.md) - Detailed project requirements and design
- [Architecture](ARCHITECTURE.md) - Technical design decisions and patterns
- [Implementation Plan](plan.md) - TDD implementation roadmap
- [Progress Tracking](todo.md) - Current development status

## Contributing

This project follows Test-Driven Development. Please ensure all code has corresponding tests and follows the established patterns.

## License

MIT License - See LICENSE file for details