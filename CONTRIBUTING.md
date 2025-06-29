# Contributing to Resume Customizer

Thank you for your interest in contributing to Resume Customizer! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Issues

Before creating an issue, please check if it already exists. When creating a new issue:

1. Use a clear and descriptive title
2. Provide a detailed description of the problem
3. Include steps to reproduce the issue
4. Add relevant labels (bug, enhancement, documentation, etc.)
5. Include your environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

1. Use the issue tracker with the "enhancement" label
2. Provide a clear use case
3. Explain why this enhancement would be useful
4. Consider the project scope and goals

### Pull Requests

We follow a Test-Driven Development (TDD) approach. All contributions must:

1. Include tests for new functionality
2. Pass all existing tests
3. Follow the existing code style
4. Update documentation as needed

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Setting Up Your Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/claude-resume-assistant.git
   cd claude-resume-assistant
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. Set up pre-commit hooks (optional but recommended):
   ```bash
   uv add --group dev pre-commit
   uv run pre-commit install
   ```

## Development Workflow

### Test-Driven Development (TDD)

We strictly follow TDD principles:

1. **Write a failing test first**
   ```python
   # tests/unit/test_new_feature.py
   def test_new_feature():
       result = new_feature()
       assert result == expected_value
   ```

2. **Run the test to confirm it fails**
   ```bash
   uv run pytest tests/unit/test_new_feature.py
   ```

3. **Write minimal code to make the test pass**
   ```python
   # src/resume_customizer/new_feature.py
   def new_feature():
       return expected_value
   ```

4. **Run the test again to confirm it passes**
   ```bash
   uv run pytest tests/unit/test_new_feature.py
   ```

5. **Refactor while keeping tests green**

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=resume_customizer

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run tests matching a pattern
uv run pytest -k "test_validation"

# Run tests with output
uv run pytest -v -s
```

### Code Style

We use standard Python conventions:

- Follow PEP 8
- Use type hints where appropriate
- Add docstrings to all public functions and classes
- Keep functions focused and small
- Use descriptive variable names

Example:
```python
from typing import Optional, Dict, Any

def process_resume(
    resume_path: str,
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Process a resume file and return the processed content.
    
    Args:
        resume_path: Path to the resume file
        options: Optional processing options
        
    Returns:
        Processed resume content as a string
        
    Raises:
        FileNotFoundError: If resume file doesn't exist
        ValueError: If resume format is invalid
    """
    # Implementation here
    pass
```

### Commit Messages

Follow the Conventional Commits specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Examples:
```
feat: add PDF export functionality
fix: handle Unicode characters in resume parsing
docs: update API documentation for customizer
test: add integration tests for CLI commands
```

## Testing Guidelines

### Unit Tests

- Test individual functions and classes in isolation
- Mock external dependencies
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

```python
def test_resume_parser_extracts_contact_info(self):
    # Arrange
    resume_content = "John Doe\njohn@example.com"
    
    # Act
    parser = ResumeParser()
    contact_info = parser.extract_contact_info(resume_content)
    
    # Assert
    assert contact_info.name == "John Doe"
    assert contact_info.email == "john@example.com"
```

### Integration Tests

- Test component interactions
- Use real file I/O when testing file operations
- Test error scenarios
- Verify end-to-end workflows

### Performance Considerations

- Keep tests fast (< 1 second per unit test)
- Use fixtures to avoid repeated setup
- Mark slow tests with `@pytest.mark.slow`

## Documentation

### Code Documentation

- Add docstrings to all public APIs
- Include type hints
- Provide usage examples in docstrings
- Keep docstrings up-to-date with code changes

### User Documentation

When adding new features:

1. Update the README.md with usage examples
2. Add entries to the appropriate documentation files
3. Update CLI help text if applicable
4. Consider adding a tutorial or guide for complex features

## Review Process

### Before Submitting a PR

1. Run all tests: `uv run pytest`
2. Check code coverage: `uv run pytest --cov=resume_customizer`
3. Run linting: `uv run ruff check .`
4. Update documentation
5. Ensure commit messages follow conventions
6. Rebase on main if needed

### PR Review Criteria

Your PR will be reviewed for:

- Test coverage (aim for >90% for new code)
- Code quality and style consistency
- Documentation completeness
- Performance impact
- Security considerations
- Backwards compatibility

### After Your PR is Merged

- Delete your feature branch
- Update your local main branch
- Celebrate your contribution! 🎉

## Security

### Reporting Security Issues

Please DO NOT create public issues for security vulnerabilities. Instead:

1. Email security concerns to: security@example.com
2. Include detailed steps to reproduce
3. Allow time for the issue to be addressed before public disclosure

### Security Best Practices

- Never commit API keys or secrets
- Validate all user inputs
- Use secure defaults
- Follow the principle of least privilege
- Keep dependencies updated

## Getting Help

- Check existing issues and discussions
- Read the documentation thoroughly
- Ask questions in GitHub Discussions
- Join our community chat (if available)

## Recognition

Contributors will be recognized in:

- The project README
- Release notes
- Special thanks section

Thank you for contributing to Resume Customizer! Your efforts help make the project better for everyone.