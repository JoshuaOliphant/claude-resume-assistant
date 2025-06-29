# Resume Customizer TDD Implementation Plan

## Overview

This plan breaks down the Resume Customizer application into small, testable chunks that build incrementally. Each step follows TDD principles: write failing tests first, implement minimal code to pass, then refactor.

**ARCHITECTURAL UPDATE**: We're using Claude Code SDK with file system tools, which dramatically simplifies the implementation. Claude will handle file I/O, sub-agent orchestration, and content analysis directly.

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

3. **File I/O Layer** (SIMPLIFIED - Claude handles this)
   - ~~Resume file reader~~ Claude reads files
   - ~~Job description reader~~ Claude reads files
   - ~~Output writer~~ Claude writes files

4. **Claude Code SDK Integration**
   - SDK setup and configuration
   - Basic prompt construction
   - Response handling

5. **Customization Engine** (SIMPLIFIED)
   - Orchestrator prompt builder (includes sub-agents)
   - ~~Sub-agent prompts~~ Handled in orchestrator prompt
   - ~~Result extraction~~ Claude writes directly

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

**NOTE: With Claude Code SDK, these steps are no longer needed as Claude handles file I/O directly**

#### Step 3.1: Markdown Reader (NOT NEEDED)
- ~~Create MarkdownReader class~~ Claude reads files
- ~~Implement file parsing~~ Claude handles this
- ~~Add error handling~~ Claude handles this
- ~~Test various markdown formats~~ Claude handles this

#### Step 3.2: Text File Reader (NOT APPLICABLE)
- Not needed for markdown-only CLI tool

#### Step 3.3: Output Writer (NOT NEEDED)
- ~~Create OutputWriter class~~ Claude writes files
- ~~Implement markdown generation~~ Claude handles this
- ~~Add formatting preservation~~ Claude handles this
- ~~Test output generation~~ Claude handles this

### Iteration 4: Claude Code SDK Setup

#### Step 4.1: SDK Configuration (NEEDS REDO)
- Create ClaudeClient wrapper using claude-code-sdk
- Implement file system tools configuration
- Configure ClaudeCodeOptions
- Test SDK initialization with file operations

#### Step 4.2: Basic Prompt Testing
- Test file reading capabilities
- Test file writing capabilities
- Verify tool usage tracking
- Test error scenarios

### Iteration 5: Prompt Engineering

#### Step 5.1: Orchestrator Prompt (SIMPLIFIED)
- Create comprehensive prompt with sub-agent instructions
- Include file paths for input/output
- Define iterative refinement process
- Test prompt effectiveness

#### Step 5.2: Sub-Agent Prompts (NOT NEEDED)
- ~~Create prompt templates~~ Handled in orchestrator
- ~~Implement prompt composition~~ Claude creates internally
- ~~Add context injection~~ Claude handles this
- ~~Test individual prompts~~ Not applicable

#### Step 5.3: Result Extraction (NOT NEEDED)
- ~~Create ResultExtractor class~~ Claude writes directly
- ~~Implement parsing logic~~ Not needed
- ~~Add validation~~ Claude validates output
- ~~Test extraction accuracy~~ Test file output instead

### Iteration 6: Core Customization Engine

#### Step 6.1: Resume Analyzer (NOT NEEDED)
- ~~Create ResumeAnalyzer class~~ Claude analyzes
- ~~Implement section detection~~ Claude handles this
- ~~Add skill extraction~~ Claude handles this
- ~~Test analysis accuracy~~ Test via output quality

#### Step 6.2: Job Matcher (NOT NEEDED)
- ~~Create JobMatcher class~~ Claude matches
- ~~Implement requirement matching~~ Claude handles this
- ~~Add gap analysis~~ Claude handles this
- ~~Test matching logic~~ Test via output quality

#### Step 6.3: Content Optimizer (NOT NEEDED)
- ~~Create ContentOptimizer class~~ Claude optimizes
- ~~Implement rewriting logic~~ Claude handles this
- ~~Add keyword integration~~ Claude handles this
- ~~Test optimization quality~~ Test via output quality

#### Step 6.4: Customizer Integration (SIMPLIFIED)
- Create simple ResumeCustomizer class
- Call Claude Code SDK with orchestrator prompt
- Monitor progress via message stream
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

### Prompt 1: Project Setup (Step 1.1)

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

### Prompt 2: Settings Configuration (Step 1.2)

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

### Prompt 3: Logging Setup (Step 1.3)

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

### Prompt 4: Resume Model (Step 2.1)

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

### Prompt 5: Job Description Model (Step 2.2)

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

### Prompt 6: Customization Result Model (Step 2.3)

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

### Prompt 7: Markdown Reader (Step 3.1)

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

### Prompt 8: Output Writer (Step 3.3)

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

### Prompt 9: Claude Client Wrapper (Step 4.1) (UPDATED FOR CLAUDE CODE SDK)

```text
Create a wrapper around Claude Code SDK with file system tools. Follow TDD:

1. Write tests for a ClaudeClient class that:
   - Uses claude-code-sdk's query() function
   - Configures file system tools (Read, Write)
   - Sends orchestrator prompt with file paths
   - Monitors progress through message stream
   - Handles SDK-specific errors
   - Tracks tool usage

2. Implement in src/resume_customizer/core/claude_client.py
3. Create async customize_resume() method
4. Configure ClaudeCodeOptions with tools
5. Process message stream
6. Log tool usage for visibility

Note: Claude Code SDK handles retries internally. Token tracking not available.
Mock the query() function for testing.
```

### Prompt 10: Basic Prompt Testing (Step 4.2)

```text
Test the Claude Code SDK integration with file operations. Follow TDD:

1. Write integration tests that verify:
   - Claude can read files through the Read tool
   - Claude can write files through the Write tool
   - Tool usage is properly tracked and reported
   - Error scenarios are handled correctly
   - File paths are validated before sending to Claude

2. Create test scenarios in tests/integration/test_claude_integration.py:
   - Test reading a simple markdown file
   - Test writing output to a new file
   - Test handling non-existent files
   - Test keyword integration from job description
   - Test progress tracking throughout the process

3. Use test fixtures with real sample files
4. Make actual API calls to understand Claude's behavior
5. Verify the orchestrator prompt produces expected results
6. Test progress callback functionality

Note: These are integration tests that require ANTHROPIC_API_KEY to be set.
They will make real API calls and help us understand how Claude actually
behaves with file operations, rather than how we think it should behave.
```

### Prompt 11: Orchestrator Prompt Builder (Step 5.1) (UPDATED)

```text
Build the orchestrator prompt that includes sub-agent instructions. Follow TDD:

1. Write tests for a build_orchestrator_prompt() function that:
   - Creates comprehensive prompt for Claude Code
   - Includes file paths for resume and job description
   - Embeds sub-agent roles within the prompt
   - Sets truthfulness constraints
   - Defines iterative refinement process
   - Specifies output file path

2. Implement in src/resume_customizer/core/prompts.py
3. Include orchestrator-workers pattern in prompt
4. Add instructions for multiple iterations
5. Specify evaluation criteria
6. Include ATS optimization guidelines

Test that prompt contains all necessary instructions.
```

### Prompt 12: Result Extractor (Step 5.3) (NO LONGER NEEDED)

```text
NO LONGER NEEDED - Claude Code SDK writes output directly to files.

Previously this would extract results from API responses, but with Claude Code SDK:
- Claude writes the customized resume directly to the output file
- No parsing or extraction needed
- Success is determined by file existence and validity
- Progress is monitored through tool usage messages

Skip this step entirely.
```

### Prompt 13: Resume Customizer Core (Step 6.4) (SIMPLIFIED)

```text
Implement the simplified ResumeCustomizer class. Follow TDD:

1. Write tests for ResumeCustomizer that:
   - Validates input file paths exist
   - Calls ClaudeClient with file paths
   - Verifies output file creation
   - Handles errors gracefully

2. Implement in src/resume_customizer/core/customizer.py
3. Create customize() method that:
   - Validates inputs
   - Builds orchestrator prompt
   - Calls Claude Code SDK
   - Reports progress
4. Add success verification

Test the complete flow with mocked Claude responses.
```

### Prompt 14: CLI Implementation (Step 7.1)

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

### Prompt 15: Progress Display (Step 7.3)

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

### Prompt 16: Error Handling Enhancement (Step 8.1)

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

### Prompt 17: Integration Testing (Step 9.1)

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

### Prompt 17: Final Polish and Documentation (Step 9.2-9.3)

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
3. **I/O** (Steps 7-8): ~~File reading and writing~~ NOT NEEDED - Claude handles
4. **Claude Integration** (Steps 9-11): SDK wrapper and prompt handling
5. **Core Logic** (Step 12): Main customization engine - SIMPLIFIED
6. **CLI** (Steps 13-14): Command-line interface
7. **Polish** (Steps 15-17): Error handling, testing, documentation

Each step builds on previous ones, ensuring no orphaned code and continuous integration of components.

## Architectural Changes Summary

By using Claude Code SDK with file system tools:

1. **Eliminated Components**:
   - File readers (Claude reads files)
   - File writers (Claude writes files)
   - Result extractors (Claude writes directly)
   - Sub-agent implementations (handled in prompt)
   - Resume analyzer, job matcher, content optimizer (Claude does this)

2. **Simplified Components**:
   - ClaudeClient: Just configures SDK and monitors progress
   - Orchestrator prompt: Includes all sub-agent instructions
   - ResumeCustomizer: Validates inputs and calls Claude

3. **Benefits**:
   - ~60% less code to write and maintain
   - More capable (future URL fetching, MCP servers)
   - Better results (Claude has full file context)
   - Simpler testing (fewer components)