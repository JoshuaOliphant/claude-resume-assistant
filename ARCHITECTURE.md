# Resume Customizer Architecture & Design Decisions

## Overview

This application demonstrates how to build an effective Claude Code application using the Python SDK. It implements sophisticated agentic patterns to customize resumes for specific job applications.

## Agentic Workflow Selection

After analyzing the documentation, I chose a hybrid approach combining:

### 1. **Orchestrator-Workers Pattern** (Primary)
- **Why**: Resume customization requires analyzing multiple aspects (skills, experience, keywords) that benefit from specialized handling
- **Implementation**: The main prompt instructs Claude to act as an orchestrator that breaks down the task into specialized subtasks

### 2. **Evaluator-Optimizer Pattern** (Secondary)
- **Why**: Resume quality improves through iterative refinement
- **Implementation**: The workflow includes evaluation and optimization phases

### 3. **Prompt Chaining** (Supporting)
- **Why**: The task naturally flows through sequential phases
- **Implementation**: Analyze → Plan → Customize → Evaluate → Optimize

## Prompt Engineering Strategy

The orchestrator prompt (`_create_orchestrator_prompt`) is structured to:

### 1. Define Clear Phases
```
1. Analysis Phase - Extract requirements and analyze current resume
2. Planning Phase - Develop customization strategy  
3. Customization Phase - Execute targeted improvements
4. Evaluation Phase - Verify quality and compliance
5. Optimization Phase - Iterative refinement
```

### 2. Create Virtual Subagents
The prompt instructs Claude to create specialized workers for:
- **Requirement Extractor**: Identifies key job requirements
- **Gap Analyzer**: Finds missing skills or experiences
- **Content Optimizer**: Rewrites sections for impact
- **ATS Checker**: Ensures formatting compliance
- **Keyword Optimizer**: Natural keyword integration

### 3. Enforce Constraints
- **Truthfulness**: "Maintain 100% truthfulness"
- **ATS Compliance**: "Use standard section headings"
- **Best Practices**: Include specific formatting rules

## SDK Configuration Decisions

### ClaudeCodeOptions Settings

```python
options = ClaudeCodeOptions(
    max_turns=15,  # Sufficient for complex analysis
    system_prompt="Expert resume customization system...",
    # No tool restrictions - resume customization is read/analyze only
)
```

**Rationale**:
- **max_turns=15**: Allows for thorough analysis and multiple refinement iterations
- **system_prompt**: Reinforces the orchestrator role and truthfulness requirement
- **No allowed_tools**: This task doesn't require file operations or code execution

## Implementation Patterns

### 1. Async Message Handling
```python
async for message in query(orchestrator_prompt, options):
    self.messages.append(message)
    # Extract final result when available
```

### 2. Result Extraction
The prompt instructs Claude to prefix the final result with "FINAL_RESUME:", making extraction reliable:
```python
if 'FINAL_RESUME:' in str(message.content):
    customized_resume = str(message.content).split('FINAL_RESUME:')[1]
```

### 3. Modular Design
- `ResumeCustomizer`: Main orchestration logic
- `ResumeSummarizer`: Separate component for change analysis
- Clear separation of concerns

## Why This Approach Works

### 1. Leverages Claude's Strengths
- **Analysis**: Claude excels at understanding complex requirements
- **Pattern Matching**: Naturally identifies keyword opportunities
- **Writing**: Generates professional, contextual content
- **Iteration**: Can self-evaluate and improve

### 2. Minimizes Weaknesses
- **No Code Execution**: Pure text analysis and generation
- **No External Tools**: Self-contained workflow
- **Clear Structure**: Phases prevent meandering

### 3. Scalable Design
- Easy to add new optimization strategies
- Can handle various resume formats
- Extensible to different job types

## Alternative Approaches Considered

### 1. Simple Prompt (Rejected)
```python
"Customize this resume for this job"
```
**Why Rejected**: Too vague, inconsistent results

### 2. Pure Routing Pattern (Rejected)
Route to different handlers based on job type
**Why Rejected**: Overcomplicates for marginal benefit

### 3. External Tool Usage (Rejected)
Use file operations, web search for industry research
**Why Rejected**: Adds complexity without proportional value

## Best Practices Demonstrated

1. **Clear Phase Definition**: Each phase has specific goals
2. **Iterative Refinement**: Built-in optimization loop
3. **Constraint Enforcement**: Truthfulness and ATS compliance
4. **Result Validation**: Evaluation phase ensures quality
5. **Structured Output**: Predictable result format

## Extension Points

The architecture supports several enhancements:

1. **Industry-Specific Agents**: Add specialized prompts for different fields
2. **Multi-Format Support**: Extend to handle PDF/DOCX
3. **Skill Gap Analysis**: Detailed reporting on missing qualifications
4. **A/B Testing**: Compare different customization strategies
5. **Learning Loop**: Store successful customizations for pattern recognition

## Conclusion

This implementation demonstrates how to:
- Apply agentic patterns from Claude Code documentation
- Structure complex prompts for reliable results
- Use the SDK effectively for non-coding tasks
- Build extensible, maintainable AI applications

The orchestrator-workers pattern with evaluator-optimizer refinement provides a robust framework for complex document transformation tasks.