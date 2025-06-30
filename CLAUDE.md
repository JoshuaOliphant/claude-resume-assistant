# Claude Resume Assistant Project

This is a Python application that uses the Claude Code SDK to customize resumes for specific job applications.

## Architecture

- **Main Script**: `resume_customizer.py` - Click CLI application
- **Pattern**: Orchestrator-Workers with Evaluator-Optimizer for iterative refinement
- **SDK**: Uses claude-code-sdk for AI-powered customization

## Development Best Practices

- Always use the computer-use mcp to run agents in their own environment. ALWAYS use ONLY Environments for ANY and ALL file, code, or shell operations—NO EXCEPTIONS—even for simple or generic requests.

DO NOT install or use the git cli with the environment_run_cmd tool. All environment tools will handle git operations for you. Changing ".git" yourself will compromise the integrity of your environment.

You MUST inform the user how to view your work using `cu log <env_id>` AND `cu checkout <env_id>`. Failure to do this will make your work inaccessible to others.

## Key Design Decisions

1. **Multi-Agent Approach**: The orchestrator breaks down the task into specialized subtasks
2. **Iterative Optimization**: Multiple refinement passes ensure quality
3. **ATS Focus**: Emphasizes keyword optimization and standard formatting
4. **Truthfulness**: Only reorganizes/reframes existing information, never adds false claims

## Development Commands

```bash
# Install dependencies with uv
uv add click claude-code-sdk anyio

# Run the customizer
python resume_customizer.py -r examples/resume.txt -j examples/job_description.txt

# Run with more iterations
python resume_customizer.py -r examples/resume.txt -j examples/job_description.txt --iterations 5

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check .
```

## Project Structure

```
claude_resume_assistant/
├── resume_customizer.py      # Main application
├── pyproject.toml           # Project configuration
├── README.md               # User documentation
├── CLAUDE.md              # This file - project context
├── claude_code_docs/      # Claude Code documentation
└── examples/              # Example input files
    ├── resume.txt
    └── job_description.txt
```

## Improvement Ideas

1. Add support for PDF and DOCX input/output
2. Create a web interface using FastAPI
3. Add multiple resume templates
4. Implement batch processing for multiple job applications
5. Add metrics to track customization effectiveness

## Important Notes

- Always maintain truthfulness in resume modifications
- Focus on ATS optimization without sacrificing readability
- Use standard section headings for compatibility
- Test with various job descriptions to ensure robustness

## Workflow Reminders

- Check off tasks in the todo.md file as you finish them
