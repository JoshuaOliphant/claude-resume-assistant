# ABOUTME: Prompt building functions for Claude Code SDK orchestration
# ABOUTME: Creates comprehensive prompts with embedded sub-agent instructions

"""Prompt building utilities for resume customization."""

from typing import Optional

from resume_customizer.config import Settings
from resume_customizer.utils.logging import get_logger


logger = get_logger(__name__)


def build_orchestrator_prompt(
    resume_path: str,
    job_description_path: str,
    output_path: str,
    settings: Settings
) -> str:
    """
    Build a comprehensive orchestrator prompt for Claude Code SDK.
    
    This prompt includes:
    - File paths for input/output
    - Sub-agent role definitions
    - Iterative refinement process
    - Truthfulness constraints
    - ATS optimization guidelines
    - Evaluation criteria
    
    Args:
        resume_path: Path to the input resume file
        job_description_path: Path to the job description file  
        output_path: Path where customized resume will be written
        settings: Application settings with configuration
        
    Returns:
        Complete orchestrator prompt for Claude
    """
    logger.info("Building orchestrator prompt")
    logger.debug(f"Resume: {resume_path}")
    logger.debug(f"Job Description: {job_description_path}")
    logger.debug(f"Output: {output_path}")
    logger.debug(f"Max iterations: {settings.max_iterations}")
    
    prompt = f"""You are an expert resume customization orchestrator. Your task is to customize a resume for a specific job application using an orchestrator-workers pattern with multiple iterations for refinement.

## Input Files
- Resume: {resume_path}
- Job Description: {job_description_path}

## Output File
- Customized Resume: {output_path}

## Process Overview
You will act as an orchestrator coordinating multiple specialized sub-agents to analyze, match, and optimize the resume. Each sub-agent has specific expertise, and you'll coordinate their work through multiple iterations to produce the best possible result.

## Sub-Agent Roles

### 1. Resume Analyzer Agent
Responsibilities:
- Extract and understand all sections of the resume
- Identify key skills, experiences, and achievements
- Note the current structure and formatting
- Catalog quantifiable results and specific technologies
- Understand the candidate's career progression
- Identify transferable skills that may not be obvious

### 2. Job Requirements Analyzer Agent
Responsibilities:
- Parse the job description thoroughly
- Extract required skills, qualifications, and keywords
- Identify nice-to-have skills and preferred qualifications
- Understand the company culture and values from the posting
- Note any specific ATS keywords that must be included
- Identify the level of experience required
- Understand the role's main responsibilities and priorities

### 3. Gap Analysis Agent
Responsibilities:
- Compare resume content with job requirements
- Identify missing keywords and skills
- Find relevant experiences that aren't properly highlighted
- Determine which accomplishments best match the role
- Identify transferable skills that could fill gaps
- Suggest reframing of experiences to better match requirements
- Prioritize which gaps are most critical to address

### 4. ATS Optimization Agent
Responsibilities:
- Ensure all critical keywords from job description are naturally integrated
- Optimize section headings for ATS parsing
- Verify standard section names (Experience, Education, Skills, etc.)
- Check for ATS-friendly formatting (no tables, graphics, or special characters)
- Ensure consistent date formatting
- Verify contact information is properly formatted
- Check that skills section includes both spelled-out and abbreviated terms

### 5. Content Enhancement Agent
Responsibilities:
- Rewrite bullet points to emphasize relevant experience
- Quantify achievements where possible (percentages, dollars, time saved)
- Tailor the professional summary to the specific role
- Ensure action verbs align with the job level and industry
- Highlight leadership and collaboration experiences appropriately
- Emphasize results and impact over just responsibilities
- Ensure consistent voice and tense throughout

### 6. Quality Assurance Agent
Responsibilities:
- Verify all information remains truthful and accurate
- Check for consistency in formatting, style, and voice
- Ensure the resume tells a coherent career story
- Validate that all job requirements are addressed
- Check for grammar, spelling, and punctuation errors
- Verify the resume length is appropriate (1-2 pages typically)
- Ensure contact information is complete and professional

## Iterative Refinement Process

You will perform at least {settings.max_iterations} iterations to refine the resume:

### Iteration 1: Initial Analysis and Customization
1. Read both input files thoroughly
2. Deploy Resume Analyzer Agent to understand the candidate's background
3. Deploy Job Requirements Analyzer Agent to extract all requirements
4. Deploy Gap Analysis Agent to identify matches and gaps
5. Create first version of customized resume focusing on:
   - Incorporating critical keywords naturally
   - Reordering experiences to highlight most relevant ones
   - Adjusting the professional summary for the role

### Iteration 2: Enhancement and Optimization
1. Review the first version critically
2. Deploy Content Enhancement Agent to:
   - Strengthen bullet points with quantifiable achievements
   - Improve action verbs and language
   - Ensure every point demonstrates value
3. Deploy ATS Optimization Agent to:
   - Verify all keywords are present
   - Ensure formatting is ATS-compatible
   - Check section headings and structure
4. Make refinements based on agent feedback

### Iteration 3: Polish and Final Review
1. Deploy Quality Assurance Agent for comprehensive review
2. Fine-tune language for maximum impact
3. Verify truthfulness constraint is maintained
4. Ensure professional tone throughout
5. Make final adjustments for clarity and coherence
6. Confirm all job requirements are addressed

## Critical Constraints

1. **Truthfulness**: You must NEVER add false information. Only reorganize, reframe, and emphasize existing experiences. Every claim must be based on information in the original resume.

2. **ATS Compatibility**: Maintain standard section headings and clean formatting. Avoid tables, graphics, or special formatting that could confuse ATS systems.

3. **Relevance**: Every modification should make the resume more relevant to the specific job. Remove or de-emphasize experiences that don't support the application.

4. **Professional Tone**: Maintain a professional, confident tone throughout. Avoid overly casual language or excessive self-promotion.

## Handling Edge Cases

### Minimal Resumes
If the input resume is extremely minimal (e.g., just a name and title):
- Focus on creating a proper structure with standard sections
- Use any available information to create section headings
- Add placeholder text that clearly indicates where the candidate should add their information
- Include comments or notes about what information is needed
- Still create the output file with a properly formatted template

### Career Change Resumes
For candidates changing careers:
- Focus heavily on transferable skills
- Reframe experiences to highlight relevant aspects
- Emphasize soft skills that apply across industries
- De-emphasize industry-specific jargon from previous career

## Evaluation Criteria

After each iteration, evaluate the resume against these criteria:
- Keyword match percentage with job description
- Clarity and impact of bullet points
- Coherence of career narrative
- ATS compatibility score
- Overall relevance to the target role
- Professional presentation and formatting

## Output Requirements

Write the final customized resume to the specified output file. The resume should:
- Include all relevant keywords from the job description naturally integrated
- Emphasize experiences and achievements that match job requirements
- Maintain clean, ATS-friendly formatting with standard sections
- Tell a compelling career story aligned with the target role
- Be truthful while presenting the candidate in the best possible light
- Be the appropriate length (typically 1-2 pages)

## Execution Instructions

1. Begin by reading both input files to understand the full context
2. Work through each iteration systematically, using the sub-agents as described
3. After each iteration, assess progress against the evaluation criteria
4. Make refinements based on the assessment
5. Continue iterating until you've completed at least {settings.max_iterations} iterations
6. Write the final, polished resume to the output file using the Write tool
7. IMPORTANT: Always create an output file, even for minimal resumes. If the input is too minimal, create a template with guidance.
8. Ensure the output file is created successfully before completing

Start by reading the input files and begin the customization process. Remember to ALWAYS write an output file."""
    
    logger.info("Orchestrator prompt built successfully")
    return prompt