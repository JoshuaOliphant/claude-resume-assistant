# Resume Customizer

An AI-powered resume customization tool that uses the Claude Code SDK to tailor resumes for specific job applications while maintaining truthfulness and ATS compatibility.

## Overview

Resume Customizer automates the time-consuming process of tailoring your resume for different job applications. It uses Claude's advanced language understanding to:

- Analyze job requirements and extract key skills and keywords
- Reorganize and reframe your existing experience to highlight relevance
- Optimize for Applicant Tracking Systems (ATS)
- Maintain 100% truthfulness - only uses information from your original resume

## Key Features

✨ **Intelligent Customization** - Analyzes both resume and job description to create the perfect match  
🎯 **ATS Optimization** - Ensures your resume passes automated screening systems  
🔄 **Iterative Refinement** - Multiple optimization passes for the best results  
🚀 **Fast Processing** - Get a customized resume in seconds  
📊 **Progress Tracking** - Real-time updates on the customization process  
🔒 **Privacy First** - Your data is processed securely and never stored  

## Architecture

The application uses an **Orchestrator-Workers** pattern with embedded sub-agents:

```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Claude Code   │────▶│   Orchestrator   │────▶│ Customized      │
│      SDK        │     │   (with embedded │     │ Resume Output   │
└─────────────────┘     │   sub-agents)    │     └─────────────────┘
                        └──────────────────┘
                                │
                    ┌───────────┴────────────┐
                    ▼                        ▼
            ┌───────────────┐       ┌────────────────┐
            │ Resume Input  │       │ Job Description│
            └───────────────┘       └────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Claude API key from [Anthropic](https://console.anthropic.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-resume-assistant.git
cd claude-resume-assistant

# Install dependencies using uv
uv sync

# Set your Claude API key
export ANTHROPIC_API_KEY='your-api-key-here'
# Or create a .env file:
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### Basic Usage

```bash
# Customize your resume for a specific job
uv run python resume_customizer.py --resume examples/resume.txt --job examples/job_description.txt

# Specify output file
uv run python resume_customizer.py -r my_resume.md -j job_posting.txt -o tailored_resume.md

# Use more iterations for better optimization (1-10)
uv run python resume_customizer.py -r resume.md -j job.txt --iterations 5

# Enable verbose mode to see detailed progress
uv run python resume_customizer.py -r resume.md -j job.txt --verbose
```

### Using as a CLI Tool

If installed via pip or uv tool:

```bash
# After installation
resume-customizer customize -r resume.md -j job.md

# With all options
resume-customizer customize \
    --resume my_resume.md \
    --job dream_job.txt \
    --output customized_resume.md \
    --iterations 5 \
    --verbose
```

## Example

Given a software engineer resume and a FinTech backend role job posting:

**Input Resume Excerpt:**

```text
Sarah Johnson
Full-Stack Software Engineer

WORK EXPERIENCE
Senior Software Engineer - TechVentures Inc.
• Led team of 5 engineers in microservices migration
• Implemented CI/CD pipeline using Jenkins and GitLab
• Reduced API response time by 45% through optimization
```

**Input Job Description Excerpt:**

```text
Senior Backend Engineer - FinTech Platform
We need an experienced backend engineer for payment processing infrastructure...
Required: Python, PostgreSQL, payment systems experience, security focus
```

**Output (Customized) Resume Excerpt:**

```text
Sarah Johnson
Senior Backend Engineer

WORK EXPERIENCE  
Senior Software Engineer - TechVentures Inc.
• Architected secure microservices handling financial transactions
• Optimized PostgreSQL queries reducing payment processing time by 45%
• Implemented comprehensive CI/CD with security scanning for compliance
```

## Input Formats

### Resume Format

- Supports plain text (.txt) and Markdown (.md) files
- Should include standard sections: Contact Info, Summary, Experience, Education, Skills
- See `examples/resume.txt` for a complete example

### Job Description Format

- Plain text or Markdown file containing the job posting
- Include company description, role responsibilities, and requirements
- See `examples/job_description.txt` for a complete example

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your-api-key-here

# Optional
RESUME_CUSTOMIZER_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
RESUME_CUSTOMIZER_MAX_ITERATIONS=3  # Default number of iterations
```

### Settings File

Create `.resume_customizer.yaml` in your home directory:

```yaml
api_key: your-api-key-here  # Can also use env var
max_iterations: 3
model: claude-3-opus-20240229
log_level: INFO
```

## Advanced Usage

### Python API

```python
from resume_customizer import ResumeCustomizer
from resume_customizer.config import Settings

# Initialize with custom settings
settings = Settings(max_iterations=5)
customizer = ResumeCustomizer(settings)

# Customize resume
result = await customizer.customize(
    resume_path="my_resume.md",
    job_description_path="job_posting.txt",
    output_path="customized_resume.md"
)

print(f"Customization complete: {result}")
```

### Batch Processing

```python
# Process multiple job applications
jobs = ["job1.txt", "job2.txt", "job3.txt"]

for job in jobs:
    output = f"resume_for_{Path(job).stem}.md"
    await customizer.customize(
        resume_path="my_resume.md",
        job_description_path=job,
        output_path=output
    )
```

## Development

### Project Structure

```text
claude-resume-assistant/
├── src/resume_customizer/
│   ├── cli/              # Command-line interface
│   ├── core/             # Core business logic
│   ├── models/           # Data models
│   └── utils/            # Utilities
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── examples/             # Example files
└── docs/                 # Documentation
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit

# Run with coverage
uv run pytest --cov=resume_customizer

# Run integration tests (requires API key)
uv run pytest tests/integration -m integration
```

### Contributing

We follow Test-Driven Development (TDD) practices. Please ensure:

1. Write tests before implementing features
2. All tests pass before submitting PR
3. Code follows existing style conventions
4. Documentation is updated as needed

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Performance

- **Processing Time**: 10-30 seconds per resume (depends on length and iterations)
- **API Usage**: Approximately 1-3 API calls per customization
- **Concurrent Processing**: Supports batch processing multiple resumes

## Troubleshooting

### Common Issues

#### "API key not found" error

```bash
# Set the API key
export ANTHROPIC_API_KEY='your-key'
# Or add to .env file
```

#### "File not found" error

- Ensure file paths are correct (relative to current directory)
- Check file extensions (.txt or .md)

#### Output seems generic

- Try increasing iterations: `--iterations 5`
- Ensure job description includes specific requirements
- Verify resume has relevant experience to highlight

### Debug Mode

```bash
# Enable debug logging
export RESUME_CUSTOMIZER_LOG_LEVEL=DEBUG
uv run python resume_customizer.py -r resume.md -j job.txt -v
```

## Security & Privacy

- **No Data Storage**: Resumes and job descriptions are processed in memory only
- **Secure API Communication**: All API calls use HTTPS
- **Local Processing**: Files never leave your machine except for API calls
- **API Key Safety**: Never commit API keys to version control

## Roadmap

- [ ] Web interface with real-time preview
- [ ] Support for PDF input/output
- [ ] Multiple resume templates
- [ ] LinkedIn profile import
- [ ] Cover letter generation
- [ ] Interview preparation based on customization

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:

- [Claude Code SDK](https://github.com/anthropics/claude-code-sdk) by Anthropic
- [Click](https://click.palletsprojects.com/) for CLI
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [uv](https://github.com/astral-sh/uv) for blazing-fast Python package management

## Support

- 📧 Email: <support@example.com>
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/claude-resume-assistant/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/claude-resume-assistant/discussions)

---

Made with ❤️ by the Claude Resume Assistant team
