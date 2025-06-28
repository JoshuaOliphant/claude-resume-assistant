# ABOUTME: ClaudeClient wrapper for the Claude Code SDK with file system tools
# ABOUTME: Handles resume customization using Claude's file operations capabilities

"""Claude Code SDK wrapper for resume customization."""

from pathlib import Path
from typing import Optional, Callable

from claude_code_sdk import query, ClaudeCodeOptions
from resume_customizer.config import Settings
from resume_customizer.utils.logging import get_logger
from resume_customizer.core.prompts import build_orchestrator_prompt


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
        prompt = build_orchestrator_prompt(
            resume_path=resume_path,
            job_description_path=job_description_path,
            output_path=output_path,
            settings=self.settings
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
    
