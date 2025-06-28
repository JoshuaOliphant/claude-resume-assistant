# Resume Customizer TDD Implementation Plan

## Overview

This plan breaks down the Resume Customizer application into small, testable chunks that build incrementally. Each step follows TDD principles: write failing tests first, implement minimal code to pass, then refactor.

## High-Level Architecture Breakdown

### Phase 1: CLI Application Foundation
1. **Project Setup & Configuration**
   - Basic project structure
   - Dependency management
   - Settings configuration

2. **Core Domain Models**
   - Resume representation
   - Job description representation
   - Customization result model

3. **File I/O Layer**
   - Resume file reader
   - Job description reader
   - Output writer

4. **Claude Code SDK Integration**
   - SDK setup and configuration
   - Basic prompt construction
   - Response handling

5. **Customization Engine**
   - Orchestrator prompt builder
   - Sub-agent prompts
   - Result extraction

6. **CLI Interface**
   - Command structure
   - Option parsing
   - Output formatting

7. **Integration & Polish**
   - End-to-end workflow
   - Error handling
   - Performance optimization

### Phase 2: Web Application (Future)
- FastAPI backend
- HTMX frontend
- Real-time updates

## Detailed Implementation Steps

### Iteration 1: Project Foundation

#### Step 1.1: Initialize Project Structure
- Set up Python project with uv
- Create basic directory structure
- Configure pyproject.toml
- Set up testing framework

#### Step 1.2: Create Settings Module
- Implement Pydantic settings class
- Add environment variable support
- Create configuration validation
- Test configuration loading

#### Step 1.3: Set Up Logging
- Configure structured logging
- Add log levels
- Create log formatters
- Test logging output

### Iteration 2: Domain Models

#### Step 2.1: Resume Model
- Create Resume dataclass
- Add section parsing
- Implement validation
- Test model creation and validation

#### Step 2.2: Job Description Model
- Create JobDescription dataclass
- Add requirement extraction
- Implement keyword parsing
- Test parsing and extraction

#### Step 2.3: Customization Result Model
- Create CustomizationResult dataclass
- Add change tracking
- Implement formatting preservation
- Test result generation

### Iteration 3: File I/O

#### Step 3.1: Markdown Reader
- Create MarkdownReader class
- Implement file parsing
- Add error handling
- Test various markdown formats

#### Step 3.2: Text File Reader
- Create TextFileReader class
- Implement plain text parsing
- Add encoding detection
- Test different encodings

#### Step 3.3: Output Writer
- Create OutputWriter class
- Implement markdown generation
- Add formatting preservation
- Test output generation

### Iteration 4: Claude Code SDK Setup

#### Step 4.1: SDK Configuration
- Create ClaudeClient wrapper
- Implement connection setup
- Add retry logic
- Test SDK initialization

#### Step 4.2: Basic Prompt Testing
- Create simple prompt builder
- Test SDK communication
- Implement response parsing
- Verify API integration

### Iteration 5: Prompt Engineering

#### Step 5.1: Orchestrator Prompt
- Create OrchestratorPrompt class
- Implement prompt template
- Add dynamic sections
- Test prompt generation

#### Step 5.2: Sub-Agent Prompts
- Create prompt templates for each agent
- Implement prompt composition
- Add context injection
- Test individual prompts

#### Step 5.3: Result Extraction
- Create ResultExtractor class
- Implement parsing logic
- Add validation
- Test extraction accuracy

### Iteration 6: Core Customization Engine

#### Step 6.1: Resume Analyzer
- Create ResumeAnalyzer class
- Implement section detection
- Add skill extraction
- Test analysis accuracy

#### Step 6.2: Job Matcher
- Create JobMatcher class
- Implement requirement matching
- Add gap analysis
- Test matching logic

#### Step 6.3: Content Optimizer
- Create ContentOptimizer class
- Implement rewriting logic
- Add keyword integration
- Test optimization quality

#### Step 6.4: Customizer Integration
- Create ResumeCustomizer class
- Wire together components
- Implement orchestration
- Test full customization flow

### Iteration 7: CLI Interface

#### Step 7.1: Click Application
- Create main CLI entry point
- Add command structure
- Implement option parsing
- Test command execution

#### Step 7.2: Input Validation
- Add file existence checks
- Implement format validation
- Create error messages
- Test validation logic

#### Step 7.3: Progress Display
- Add progress indicators
- Implement status messages
- Create verbose mode
- Test user feedback

#### Step 7.4: Output Handling
- Implement result display
- Add file writing
- Create success messages
- Test output generation

### Iteration 8: Error Handling & Resilience

#### Step 8.1: API Error Handling
- Add retry mechanisms
- Implement backoff strategies
- Create fallback behavior
- Test error scenarios

#### Step 8.2: File Error Handling
- Add file permission checks
- Implement encoding fallbacks
- Create helpful error messages
- Test edge cases

#### Step 8.3: Validation & Warnings
- Add comprehensive validation
- Implement warning system
- Create user guidance
- Test validation flows

### Iteration 9: Integration & Polish

#### Step 9.1: End-to-End Testing
- Create integration tests
- Test full workflows
- Add performance tests
- Verify quality metrics

#### Step 9.2: Documentation
- Add inline documentation
- Create user guide
- Write API documentation
- Test documentation accuracy

#### Step 9.3: Performance Optimization
- Profile application
- Optimize slow paths
- Add caching where needed
- Test performance improvements

## Code Generation Prompts

### Prompt 1: Project Setup

```text
Create a new Python project for a resume customizer application using uv. Set up the project structure with the following:

1. Initialize a new uv project called "resume-customizer"
2. Add these dependencies: click, pydantic, pydantic-settings, claude-code-sdk, pytest, pytest-asyncio, pytest-cov
3. Create this directory structure:
   - src/resume_customizer/ (main package)
   - src/resume_customizer/models/ (domain models)
   - src/resume_customizer/io/ (file I/O)
   - src/resume_customizer/core/ (business logic)
   - src/resume_customizer/cli/ (CLI interface)
   - tests/ (test files)
   - tests/unit/
   - tests/integration/
   - examples/ (example files)

4. Create a basic __init__.py in each package
5. Set up pytest configuration in pyproject.toml
6. Create a .env.example file with RESUME_CLAUDE_API_KEY placeholder

Write tests first to verify the project structure is correct, then implement the setup.
```

### Prompt 2: Settings Configuration

```text
Implement a settings module using Pydantic for configuration management. Follow TDD:

1. First, write tests for a Settings class that should:
   - Load RESUME_CLAUDE_API_KEY from environment
   - Set default max_iterations to 3
   - Set default output_format to "markdown"
   - Set default preserve_formatting to True
   - Support loading from .env file
   - Validate that claude_api_key is not empty

2. Create the Settings class in src/resume_customizer/config.py
3. Use Pydantic BaseSettings with proper validation
4. Implement environment variable prefix "RESUME_"
5. Add a get_settings() function with functools.lru_cache

Ensure all tests pass before moving on.
```

### Prompt 3: Logging Setup

```text
Add structured logging to the application using Python's logging module. Follow TDD:

1. Write tests for a logging configuration that:
   - Creates a logger named "resume_customizer"
   - Supports DEBUG, INFO, WARNING, ERROR levels
   - Formats logs with timestamp, level, and message
   - Can be configured via RESUME_LOG_LEVEL env var
   - Defaults to INFO level

2. Create logging configuration in src/resume_customizer/utils/logging.py
3. Implement get_logger() function
4. Add JSON formatting option for production
5. Include context data support (job_id, resume_name)

Test different log levels and ensure proper formatting.
```

### Prompt 4: Resume Model

```text
Create a Resume domain model with comprehensive parsing capabilities. Follow TDD:

1. Write tests for a Resume dataclass that:
   - Parses markdown content into sections
   - Identifies common sections (Summary, Experience, Skills, Education)
   - Preserves original formatting
   - Extracts key information (years of experience, skills list)
   - Handles various section naming conventions
   - Validates required sections exist

2. Implement Resume model in src/resume_customizer/models/resume.py
3. Use dataclasses with proper type hints
4. Add section detection logic
5. Implement content preservation
6. Create from_markdown() class method

Test with various resume formats and edge cases.
```

### Prompt 5: Job Description Model

```text
Create a JobDescription model for parsing job postings. Follow TDD:

1. Write tests for a JobDescription dataclass that:
   - Extracts job title and company
   - Identifies required skills
   - Finds years of experience requirements
   - Extracts key responsibilities
   - Identifies nice-to-have skills
   - Parses both structured and unstructured text

2. Implement in src/resume_customizer/models/job_description.py
3. Add keyword extraction logic
4. Implement requirement categorization
5. Create from_text() class method
6. Add ATS keyword detection

Test with real job descriptions in various formats.
```

### Prompt 6: Customization Result Model

```text
Create a CustomizationResult model to track changes. Follow TDD:

1. Write tests for a CustomizationResult dataclass that:
   - Stores original and customized resume content
   - Tracks specific changes made
   - Calculates match score
   - Lists integrated keywords
   - Identifies reordered sections
   - Provides change summary

2. Implement in src/resume_customizer/models/result.py
3. Add change tracking logic
4. Implement diff generation
5. Create formatting for CLI output
6. Add export methods

Test change tracking and summary generation.
```

### Prompt 7: Markdown Reader

```text
Implement a MarkdownReader for parsing resume files. Follow TDD:

1. Write tests for a MarkdownReader class that:
   - Reads markdown files with proper encoding
   - Handles file not found gracefully
   - Detects file encoding automatically
   - Validates markdown structure
   - Preserves formatting and whitespace
   - Extracts metadata if present

2. Create in src/resume_customizer/io/readers.py
3. Implement read() method
4. Add encoding detection
5. Create validation logic
6. Handle various markdown flavors

Test with different file encodings and markdown styles.
```

### Prompt 8: Output Writer

```text
Create an OutputWriter for saving customized resumes. Follow TDD:

1. Write tests for an OutputWriter class that:
   - Writes markdown with preserved formatting
   - Creates backup of original if exists
   - Handles write permissions properly
   - Adds metadata comments
   - Supports different output paths
   - Validates output before writing

2. Implement in src/resume_customizer/io/writers.py
3. Add write() method with safety checks
4. Implement backup functionality
5. Create formatting preservation
6. Add success confirmation

Test file writing with various scenarios and permissions.
```

### Prompt 9: Claude Client Wrapper

```text
Create a wrapper around Claude Code SDK for easier testing. Follow TDD:

1. Write tests for a ClaudeClient class that:
   - Initializes with API key from settings
   - Sends prompts and receives responses
   - Handles API errors gracefully
   - Implements retry logic
   - Tracks token usage
   - Supports timeout configuration

2. Implement in src/resume_customizer/core/claude_client.py
3. Create async query method
4. Add retry decorator
5. Implement error handling
6. Add response parsing

Mock the SDK for testing and verify error handling.
```

### Prompt 10: Orchestrator Prompt Builder

```text
Build the orchestrator prompt generator. Follow TDD:

1. Write tests for an OrchestratorPromptBuilder that:
   - Creates structured prompts for Claude
   - Includes resume and job description
   - Defines sub-agent roles
   - Sets truthfulness constraints
   - Specifies output format
   - Adds evaluation criteria

2. Implement in src/resume_customizer/core/prompts.py
3. Create build_prompt() method
4. Add template management
5. Implement variable substitution
6. Create prompt validation

Test prompt generation with various inputs.
```

### Prompt 11: Result Extractor

```text
Create a ResultExtractor to parse Claude's responses. Follow TDD:

1. Write tests for a ResultExtractor class that:
   - Extracts customized resume from response
   - Parses change summary
   - Identifies keywords added
   - Extracts match score
   - Handles malformed responses
   - Validates extracted content

2. Implement in src/resume_customizer/core/extractors.py
3. Add extract_result() method
4. Create parsing strategies
5. Implement validation logic
6. Add fallback handling

Test with various response formats and edge cases.
```

### Prompt 12: Resume Customizer Core

```text
Implement the main ResumeCustomizer class. Follow TDD:

1. Write tests for ResumeCustomizer that:
   - Orchestrates the full customization flow
   - Loads resume and job description
   - Builds and sends prompts
   - Extracts and validates results
   - Handles errors gracefully
   - Supports iteration configuration

2. Implement in src/resume_customizer/core/customizer.py
3. Create customize() method
4. Wire together all components
5. Add progress callbacks
6. Implement error recovery

Test the complete customization flow end-to-end.
```

### Prompt 13: CLI Implementation

```text
Create the Click CLI application. Follow TDD:

1. Write tests for CLI commands that:
   - Parse command-line arguments
   - Validate input files exist
   - Handle missing arguments
   - Support verbose mode
   - Display progress
   - Show results clearly

2. Implement in src/resume_customizer/cli/app.py
3. Create main command group
4. Add customize command
5. Implement option parsing
6. Add output formatting

Test CLI with various argument combinations.
```

### Prompt 14: Progress Display

```text
Add progress indicators to the CLI. Follow TDD:

1. Write tests for a ProgressDisplay class that:
   - Shows step-by-step progress
   - Updates in real-time
   - Supports verbose mode details
   - Handles long-running operations
   - Shows time estimates
   - Cleans up on completion

2. Implement in src/resume_customizer/cli/progress.py
3. Create progress bar integration
4. Add status messages
5. Implement time tracking
6. Create spinner for indeterminate tasks

Test progress display with various scenarios.
```

### Prompt 15: Error Handling Enhancement

```text
Enhance error handling throughout the application. Follow TDD:

1. Write tests for comprehensive error handling:
   - API rate limits
   - Network timeouts
   - Invalid file formats
   - Malformed responses
   - Missing dependencies
   - Configuration errors

2. Create custom exceptions in src/resume_customizer/exceptions.py
3. Add error recovery strategies
4. Implement user-friendly messages
5. Create error logging
6. Add troubleshooting hints

Test all error scenarios with helpful outputs.
```

### Prompt 16: Integration Testing

```text
Create comprehensive integration tests. Follow TDD:

1. Write integration tests that:
   - Test full CLI workflow
   - Verify file I/O operations
   - Check Claude API integration
   - Validate customization quality
   - Test error scenarios
   - Measure performance

2. Create in tests/integration/
3. Add fixture management
4. Implement test data
5. Create quality assertions
6. Add performance benchmarks

Ensure all components work together correctly.
```

### Prompt 17: Final Polish and Documentation

```text
Add final polish and documentation:

1. Write tests for:
   - CLI help text completeness
   - Example file validity
   - Documentation accuracy
   - Version information
   - License compliance

2. Create comprehensive documentation:
   - README with quick start
   - CLI usage examples
   - API documentation
   - Contributing guidelines
   - Example resumes and job descriptions

3. Add final improvements:
   - Performance profiling
   - Memory optimization
   - Code cleanup
   - Type hint completion

Ensure the application is production-ready.
```

## Implementation Order Summary

1. **Foundation** (Steps 1-3): Project setup, configuration, logging
2. **Models** (Steps 4-6): Domain models for data representation
3. **I/O** (Steps 7-8): File reading and writing
4. **Claude Integration** (Steps 9-11): SDK wrapper and prompt handling
5. **Core Logic** (Step 12): Main customization engine
6. **CLI** (Steps 13-14): Command-line interface
7. **Polish** (Steps 15-17): Error handling, testing, documentation

Each step builds on previous ones, ensuring no orphaned code and continuous integration of components.