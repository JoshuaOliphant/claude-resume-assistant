# Integration Tests

This directory contains integration tests that use the real Claude Code SDK to understand how it actually behaves with file operations.

## Running Integration Tests

### Prerequisites

1. You need a valid Anthropic API key
2. Set the `ANTHROPIC_API_KEY` environment variable:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```
   Or use the `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   source .env
   ```

### Running Tests

From the project root:

```bash
# Run all integration tests
uv run pytest tests/integration -m integration -v

# Run with output
uv run pytest tests/integration -m integration -v -s

# Run specific test
uv run pytest tests/integration/test_claude_integration.py::TestClaudeIntegration::test_basic_file_operations -v -s

# Use the convenience script
uv run python tests/integration/run_integration_tests.py
```

### Skipping Integration Tests

When running the full test suite, integration tests are automatically skipped if no API key is set:

```bash
# Run only unit tests
uv run pytest -m "not integration"
```

## Test Coverage

The integration tests cover:

1. **Basic File Operations** - Verifies Claude can read input files and write output
2. **Keyword Integration** - Checks that Claude integrates job-specific keywords
3. **Error Handling** - Tests behavior with non-existent files
4. **Directory Creation** - Verifies output directories are created as needed
5. **Minimal Input** - Tests behavior with very simple input files
6. **Progress Tracking** - Detailed tracking of Claude's progress messages
7. **Multiple Iterations** - Verifies the iteration behavior

## Important Notes

- These tests make real API calls to Claude
- Each test run will consume API credits
- Tests may take 10-30 seconds each depending on API response time
- The actual output will vary between runs (Claude is non-deterministic)
- Tests verify behavior and structure rather than exact output

## Debugging

To see detailed output from Claude:

```bash
# Run with print statements visible
uv run pytest tests/integration -m integration -v -s --tb=short
```

The tests include progress callbacks that print Claude's messages for debugging.