# ABOUTME: ClaudeClient wrapper for the Claude Code SDK with file system tools
# ABOUTME: Handles resume customization using Claude's file operations capabilities

"""Claude Code SDK wrapper for resume customization."""

import time
from pathlib import Path
from typing import Optional, Callable, Dict, Any

from claude_code_sdk import query, ClaudeCodeOptions
from resume_customizer.config import Settings
from resume_customizer.utils.logging import get_logger
from resume_customizer.core.prompts import build_orchestrator_prompt


logger = get_logger(__name__)

# Pricing information for Claude models (per 1M tokens)
CLAUDE_PRICING = {
    "claude-sonnet-4-0": {
        "input": 3.00,   # $3.00 per 1M input tokens
        "output": 15.00  # $15.00 per 1M output tokens
    }
}


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
        self.model_name = getattr(settings, 'model_name', 'claude-sonnet-4-0')
        # Cap max_history_requests to prevent memory issues
        self.max_history_requests = min(getattr(settings, 'max_history_requests', 100), 1000)
        self.usage_stats = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "requests": []
        }
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
            cwd=Path.cwd(),  # Set working directory
            model=self.model_name  # Use configurable model
        )
        
        logger.info(f"Starting resume customization with Claude Code SDK")
        logger.debug(f"Resume: {resume_path}")
        logger.debug(f"Job Description: {job_description_path}")
        logger.debug(f"Output: {output_path}")
        
        # Track tool usage and request metrics
        tool_usage = {"Read": 0, "Write": 0}
        request_tokens = {"input": 0, "output": 0}
        request_start_time = time.time()
        final_cost_usd = None
        
        try:
            # Process messages from Claude
            async for message in query(prompt=prompt, options=options):
                # Handle ResultMessage which comes at the end
                if hasattr(message, 'total_cost_usd') and hasattr(message, 'usage'):
                    # This is the final ResultMessage with complete usage info
                    if hasattr(message, 'usage') and message.usage:
                        usage_data = message.usage
                        if isinstance(usage_data, dict):
                            # Track all token types - note that cache tokens may have different pricing
                            request_tokens["input"] = usage_data.get('input_tokens', 0) + \
                                                    usage_data.get('cache_creation_input_tokens', 0) + \
                                                    usage_data.get('cache_read_input_tokens', 0)
                            request_tokens["output"] = usage_data.get('output_tokens', 0)
                        
                    if hasattr(message, 'total_cost_usd'):
                        final_cost_usd = message.total_cost_usd
                        logger.info(f"API cost from SDK: ${final_cost_usd:.6f}")
                        logger.debug(f"Full usage data: {message.usage if hasattr(message, 'usage') else 'None'}")
                
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
            
            # Use SDK-provided cost if available, otherwise calculate
            if final_cost_usd is not None:
                total_cost = final_cost_usd
                # Calculate input/output costs based on token ratio
                if request_tokens["input"] + request_tokens["output"] > 0:
                    input_ratio = request_tokens["input"] / (request_tokens["input"] + request_tokens["output"])
                    input_cost = total_cost * input_ratio
                    output_cost = total_cost * (1 - input_ratio)
                else:
                    input_cost = 0.0
                    output_cost = 0.0
            else:
                # Fallback to manual calculation
                model_pricing = CLAUDE_PRICING.get(self.model_name, {"input": 3.0, "output": 15.0})
                input_cost = (request_tokens["input"] / 1_000_000) * model_pricing["input"]
                output_cost = (request_tokens["output"] / 1_000_000) * model_pricing["output"]
                total_cost = input_cost + output_cost
            
            # Update usage statistics
            self.usage_stats["total_input_tokens"] += request_tokens["input"]
            self.usage_stats["total_output_tokens"] += request_tokens["output"]
            self.usage_stats["total_cost"] += total_cost
            
            # Add request data with timestamp
            request_data = {
                "resume_path": resume_path,
                "job_path": job_description_path,
                "input_tokens": request_tokens["input"],
                "output_tokens": request_tokens["output"],
                "cost": total_cost,
                "timestamp": time.time()  # Add timestamp for better tracking
            }
            
            # Proactive cleanup before adding to prevent memory leak
            if len(self.usage_stats["requests"]) >= self.max_history_requests:
                # Remove oldest requests to make room
                self.usage_stats["requests"] = self.usage_stats["requests"][-(self.max_history_requests-1):]
            
            self.usage_stats["requests"].append(request_data)
            
            logger.info(f"Token usage - Input: {request_tokens['input']:,}, Output: {request_tokens['output']:,}")
            logger.info(f"Request cost: ${total_cost:.4f} (Input: ${input_cost:.4f}, Output: ${output_cost:.4f})")
            if final_cost_usd is not None:
                logger.info(f"Cost source: SDK-provided (total_cost_usd)")
            else:
                logger.info(f"Cost source: Calculated from token counts")
            
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
                    progress_callback(f"Cost: ${total_cost:.4f} ({request_tokens['input']:,} input + {request_tokens['output']:,} output tokens)")
                    
        except Exception as e:
            logger.error(f"Error during resume customization: {str(e)}")
            raise
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics.
        
        Returns:
            Dictionary containing token usage and cost information
        """
        return self.usage_stats.copy()
    
    def reset_usage_stats(self) -> None:
        """Reset usage statistics to zero."""
        self.usage_stats = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "requests": []
        }
        logger.info("Usage statistics reset")
    
    def get_average_cost_per_resume(self) -> float:
        """
        Calculate average cost per resume customization.
        
        Returns:
            Average cost in dollars
        """
        if not self.usage_stats["requests"]:
            return 0.0
        
        return self.usage_stats["total_cost"] / len(self.usage_stats["requests"])
