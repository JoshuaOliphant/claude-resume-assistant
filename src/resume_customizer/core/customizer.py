# ABOUTME: Simplified ResumeCustomizer that orchestrates the customization process
# ABOUTME: Validates inputs and delegates to ClaudeClient for actual customization

"""Simplified resume customizer that leverages Claude Code SDK."""

from pathlib import Path
from typing import Optional, Callable

from resume_customizer.config import Settings
from resume_customizer.core.claude_client import ClaudeClient
from resume_customizer.utils.logging import get_logger


logger = get_logger(__name__)


class ResumeCustomizer:
    """Simplified customizer that validates inputs and calls Claude Code SDK."""
    
    def __init__(self, settings: Settings):
        """
        Initialize the resume customizer.
        
        Args:
            settings: Application settings with configuration
        """
        self.settings = settings
        self.claude_client = ClaudeClient(settings)
        logger.info("ResumeCustomizer initialized")
    
    async def customize(
        self,
        resume_path: str,
        job_description_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Customize a resume for a specific job application.
        
        This method validates inputs and delegates to ClaudeClient which uses
        Claude Code SDK to read files, analyze content, and write the customized resume.
        
        Args:
            resume_path: Path to the input resume file
            job_description_path: Path to the job description file
            output_path: Path where customized resume will be written
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to the generated output file
            
        Raises:
            FileNotFoundError: If input files don't exist
            Exception: For other errors during customization
        """
        logger.info("Starting resume customization")
        
        # Report progress
        if progress_callback:
            progress_callback("Validating input files...")
        
        # Convert to absolute paths
        resume_path = str(Path(resume_path).resolve())
        job_description_path = str(Path(job_description_path).resolve())
        output_path = str(Path(output_path).resolve())
        
        logger.debug(f"Resume path: {resume_path}")
        logger.debug(f"Job description path: {job_description_path}")
        logger.debug(f"Output path: {output_path}")
        
        # Validate input files exist
        logger.info("Validating input files")
        
        if not Path(resume_path).exists():
            error_msg = f"Resume file not found: {resume_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if not Path(job_description_path).exists():
            error_msg = f"Job description file not found: {job_description_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ensured: {output_dir}")
        
        # Report progress
        if progress_callback:
            progress_callback("Starting customization with Claude...")
        
        try:
            # Delegate to ClaudeClient
            logger.info("Delegating to ClaudeClient for customization")
            await self.claude_client.customize_resume(
                resume_path=resume_path,
                job_description_path=job_description_path,
                output_path=output_path,
                progress_callback=progress_callback
            )
            
            # Verify output was created
            if Path(output_path).exists():
                success_msg = f"Resume customization completed successfully! Output saved to: {output_path}"
                logger.info(success_msg)
                if progress_callback:
                    progress_callback(success_msg)
            else:
                warning_msg = f"Warning: Output file was not created at {output_path}"
                logger.warning(warning_msg)
                if progress_callback:
                    progress_callback(warning_msg)
            
            return output_path
            
        except Exception as e:
            error_msg = f"Error during customization: {str(e)}"
            logger.error(error_msg)
            raise