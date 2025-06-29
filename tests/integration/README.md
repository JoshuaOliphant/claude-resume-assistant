# Integration Tests

This directory contains comprehensive integration tests that verify the complete functionality of the resume customizer, including real Claude API calls, file operations, and end-to-end workflows.

## Running Integration Tests

### Prerequisites

1. You need a valid Anthropic API key
2. Install development dependencies:
   ```bash
   uv add --group dev psutil
   ```
3. Set the `ANTHROPIC_API_KEY` environment variable:
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

# Run specific test module
uv run pytest tests/integration/test_cli_workflow.py -v -s

# Run specific test
uv run pytest tests/integration/test_claude_integration.py::TestClaudeIntegration::test_basic_file_operations -v -s

# Run excluding slow tests
uv run pytest tests/integration -m "integration and not slow" -v

# Use the convenience script
uv run python tests/integration/run_integration_tests.py
```

### Skipping Integration Tests

When running the full test suite, integration tests are automatically skipped if no API key is set:

```bash
# Run only unit tests
uv run pytest -m "not integration"
```

## Test Modules

### 1. **test_claude_integration.py**
Original integration tests covering:
- Basic file operations with Claude SDK
- Keyword integration from job descriptions
- Error handling for missing files
- Directory creation
- Minimal input handling
- Progress tracking
- Multiple iteration behavior

### 2. **test_cli_workflow.py**
Full CLI workflow tests:
- Complete command-line execution
- Verbose mode operation
- Default output path generation
- Multiple iterations
- Error handling
- Progress display
- Special character handling
- Performance benchmarks

### 3. **test_file_operations.py**
File I/O operation tests:
- UTF-8 encoding support
- Large file handling
- Directory creation
- Relative/absolute paths
- Symbolic links
- File permissions
- Concurrent access
- Various file extensions

### 4. **test_api_integration.py**
Claude API behavior tests:
- API response structure
- Complex prompts
- Retry behavior
- Long content handling
- Parallel requests
- Special instructions
- Error messages
- Rate limiting

### 5. **test_quality_validation.py**
Output quality validation:
- ATS compliance checking
- Keyword integration scoring
- Content preservation
- Formatting consistency
- Length appropriateness
- Job-specific customization
- Iteration improvement
- Edge case handling

### 6. **test_error_scenarios.py**
Error handling tests:
- Network errors
- Timeouts
- Malformed input
- Disk space issues
- Interruption handling
- Concurrent access errors
- Invalid API keys
- Unicode errors

### 7. **test_performance_benchmarks.py**
Performance measurement:
- Baseline performance metrics
- Iteration scaling
- Input size scaling
- Concurrent performance
- Memory usage profiling
- Stress testing
- Benchmark summary generation

### 8. **fixtures.py**
Shared test fixtures:
- Sample resumes (entry/mid/senior level)
- Sample job descriptions
- Edge case resumes
- Performance tracking
- Quality validation utilities

## Important Notes

- These tests make real API calls to Claude
- Each test run will consume API credits
- Tests may take 10-30 seconds each depending on API response time
- The actual output will vary between runs (Claude is non-deterministic)
- Tests verify behavior and structure rather than exact output
- Performance benchmarks save results to `benchmark_results/` directory

## Debugging

To see detailed output:

```bash
# Run with print statements visible
uv run pytest tests/integration -m integration -v -s --tb=short

# Run with specific log level
uv run pytest tests/integration -m integration -v -s --log-cli-level=DEBUG
```

## Test Markers

- `@pytest.mark.integration` - All integration tests
- `@pytest.mark.slow` - Slow-running tests (benchmarks)
- `@pytest.mark.asyncio` - Async test functions

## Coverage

The integration test suite provides comprehensive coverage of:
- All major user workflows
- Error conditions and edge cases
- Performance characteristics
- Quality metrics
- File system operations
- API interactions
- CLI functionality