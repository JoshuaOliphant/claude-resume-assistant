# ABOUTME: ClaudeClient wrapper for the Claude Code SDK with file system tools
# ABOUTME: Handles resume customization using Claude's file operations capabilities

"""Claude Code SDK wrapper for resume customization."""

from pathlib import Path
from typing import Optional, Callable

from claude_code_sdk import query, ClaudeCodeOptions
from resume_customizer.config import Settings
from resume_customizer.utils.logging import get_logger


logger = get_logger(__name__)


class ClaudeClient:
    """Wrapper around Claude Code SDK for resume customization with file tools."""
    
    def __init__(self, settings: Settings):
        """
        Initialize Claude client with settings.
        
        Args:
            settings: Application settings with API key and configuration
            
        Raises:
            ValueError: If API key is missing
        """
        if not settings.claude_api_key:
            raise ValueError("Claude API key is required")
        
        self.settings = settings
        logger.info("ClaudeClient initialized with Claude Code SDK")
    
    async def customize_resume(
        self,
        resume_path: str,
        job_description_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Customize a resume for a specific job using Claude Code SDK.
        
        Claude will read the input files, analyze them, and write the customized
        resume directly to the output file.
        
        Args:
            resume_path: Path to the input resume file
            job_description_path: Path to the job description file
            output_path: Path where customized resume will be written
            progress_callback: Optional callback for progress updates
            
        Raises:
            FileNotFoundError: If input files don't exist
            Exception: For other errors during customization
        """
        # Validate input files exist
        if not Path(resume_path).exists():
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        
        if not Path(job_description_path).exists():
            raise FileNotFoundError(f"Job description file not found: {job_description_path}")
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build the orchestrator prompt
        prompt = self._build_orchestrator_prompt(
            resume_path=resume_path,
            job_description_path=job_description_path,
            output_path=output_path
        )
        
        # Configure Claude Code options
        options = ClaudeCodeOptions(
            max_turns=10,  # Allow multiple turns for Claude to complete the task
            allowed_tools=["Read", "Write", "Edit", "TodoWrite", "TodoRead"],  # Include all tools Claude might use
            system_prompt=self.settings.system_prompt if hasattr(self.settings, 'system_prompt') else None,
            cwd=Path.cwd()  # Set working directory
        )
        
        logger.info(f"Starting resume customization with Claude Code SDK")
        logger.debug(f"Resume: {resume_path}")
        logger.debug(f"Job Description: {job_description_path}")
        logger.debug(f"Output: {output_path}")
        
        # Track tool usage
        tool_usage = {"Read": 0, "Write": 0}
        
        try:
            # Process messages from Claude
            async for message in query(prompt=prompt, options=options):
                # Log progress
                if hasattr(message, 'content') and message.content:
                    for content_block in message.content:
                        # Handle text messages
                        if hasattr(content_block, 'text') and content_block.text:
                            text = content_block.text
                            logger.info(f"Claude: {text[:100]}...")
                            if progress_callback:
                                progress_callback(text)
                        
                        # Handle tool usage
                        elif hasattr(content_block, 'name') and content_block.name:
                            tool_name = content_block.name
                            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
                            
                            logger.info(f"Claude using tool: {tool_name}")
                            
                            if hasattr(content_block, 'input'):
                                tool_input = content_block.input
                                
                                # Extract file path from different tool input formats
                                file_path = None
                                if isinstance(tool_input, dict):
                                    file_path = tool_input.get('path') or tool_input.get('file_path')
                                
                                if tool_name == "Read":
                                    logger.info(f"Claude reading file: {file_path or 'unknown'}")
                                    if progress_callback:
                                        progress_callback(f"Tool: Read - {file_path or 'unknown'}")
                                elif tool_name == "Write":
                                    logger.info(f"Claude writing file: {file_path or 'unknown'}")
                                    if progress_callback:
                                        progress_callback(f"Tool: Write - {file_path or 'unknown'}")
                                elif tool_name == "Edit":
                                    logger.info(f"Claude editing file: {file_path or 'unknown'}")
                                    if progress_callback:
                                        progress_callback(f"Tool: Edit - {file_path or 'unknown'}")
                                else:
                                    # Log other tools being used
                                    logger.debug(f"Claude using {tool_name} with input: {tool_input}")
                                    if progress_callback:
                                        progress_callback(f"Tool: {tool_name}")
            
            # Log tool usage summary
            logger.info(f"Tool usage summary: {tool_usage}")
            
            # Verify output file was created
            if not Path(output_path).exists():
                warning_msg = f"Warning: Output file was not created at {output_path}"
                logger.warning(warning_msg)
                if progress_callback:
                    progress_callback(warning_msg)
            else:
                success_msg = f"Resume customization completed successfully! Output: {output_path}"
                logger.info(success_msg)
                if progress_callback:
                    progress_callback(success_msg)
                    
        except Exception as e:
            logger.error(f"Error during resume customization: {str(e)}")
            raise
    
    def _build_orchestrator_prompt(
        self,
        resume_path: str,
        job_description_path: str,
        output_path: str
    ) -> str:
        """
        Build the orchestrator prompt that includes sub-agent instructions.
        
        Args:
            resume_path: Path to the input resume file
            job_description_path: Path to the job description file
            output_path: Path where customized resume will be written
            
        Returns:
            The complete orchestrator prompt
        """
        prompt = f"""You are an expert resume customization orchestrator. Your task is to customize a resume for a specific job application using an orchestrator-workers pattern with multiple iterations for refinement.

## Input Files
- Resume: {resume_path}
- Job Description: {job_description_path}

## Output File
- Customized Resume: {output_path}

## Process Overview
You will act as an orchestrator managing multiple specialized sub-agents to analyze, match, and optimize the resume. Each sub-agent has specific expertise, and you'll coordinate their work through multiple iterations.

## Sub-Agent Roles

### 1. Resume Analyzer Agent
- Extract and understand all sections of the resume
- Identify key skills, experiences, and achievements
- Note the current structure and formatting
- Catalog quantifiable results and specific technologies

### 2. Job Requirements Analyzer Agent
- Parse the job description thoroughly
- Extract required skills, qualifications, and keywords
- Identify nice-to-have skills
- Understand the company culture and values from the posting
- Note any specific ATS keywords that must be included

### 3. Gap Analysis Agent
- Compare resume content with job requirements
- Identify missing keywords and skills
- Find relevant experiences that aren't highlighted
- Determine which accomplishments best match the role

### 4. ATS Optimization Agent
- Ensure all critical keywords from job description are naturally integrated
- Optimize section headings for ATS parsing
- Verify standard section names (Experience, Education, Skills)
- Check for ATS-friendly formatting

### 5. Content Enhancement Agent
- Rewrite bullet points to emphasize relevant experience
- Quantify achievements where possible
- Tailor the professional summary to the specific role
- Ensure action verbs align with the job level

### 6. Quality Assurance Agent
- Verify all information remains truthful
- Check for consistency in formatting and style
- Ensure the resume tells a coherent career story
- Validate that all job requirements are addressed

## Iteration Process

Perform at least {self.settings.max_iterations} iterations:

### Iteration 1: Initial Analysis and Customization
1. Read both input files
2. Perform initial analysis with all agents
3. Create first version of customized resume
4. Focus on incorporating all critical keywords

### Iteration 2: Enhancement and Optimization
1. Review the first version
2. Enhance bullet points for stronger impact
3. Optimize for ATS scanning
4. Ensure all requirements are addressed

### Iteration 3: Polish and Refinement
1. Final review for quality and coherence
2. Fine-tune language for maximum impact
3. Verify truthfulness constraint
4. Make final adjustments

## Critical Constraints

1. **Truthfulness**: You must NEVER add false information. Only reorganize, reframe, and emphasize existing experiences.
2. **ATS Compatibility**: Maintain standard section headings and clean formatting.
3. **Relevance**: Every modification should make the resume more relevant to the specific job.
4. **Professional Tone**: Maintain a professional, confident tone throughout.

## Output Requirements

Write the final customized resume to the specified output file. The resume should:
- Include all relevant keywords from the job description
- Emphasize experiences that match job requirements
- Maintain clean, ATS-friendly formatting
- Tell a compelling career story aligned with the target role

Begin by reading both input files, then proceed with the iterative customization process."""

        return prompt