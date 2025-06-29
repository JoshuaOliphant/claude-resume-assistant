# ABOUTME: Progress display functionality for CLI with spinners and progress bars
# ABOUTME: Provides real-time progress updates with time tracking and verbose mode

"""Progress display utilities for the CLI."""

import time
import threading
from enum import Enum, auto
from typing import Optional, List, Tuple, Dict, Callable
from datetime import datetime

import click


class ProgressStep(Enum):
    """Enumeration of progress steps."""
    INITIALIZING = auto()
    VALIDATING = auto()
    READING_FILES = auto()
    ANALYZING = auto()
    CUSTOMIZING = auto()
    WRITING_OUTPUT = auto()
    COMPLETED = auto()


class ProgressDisplay:
    """Manages progress display for the CLI with spinners and progress tracking."""
    
    # Default step messages
    DEFAULT_STEPS = [
        (ProgressStep.INITIALIZING, "Initializing"),
        (ProgressStep.VALIDATING, "Validating input files"),
        (ProgressStep.READING_FILES, "Reading files"),
        (ProgressStep.ANALYZING, "Analyzing content"),
        (ProgressStep.CUSTOMIZING, "Customizing resume"),
        (ProgressStep.WRITING_OUTPUT, "Writing output"),
        (ProgressStep.COMPLETED, "Completed")
    ]
    
    # Spinner frames
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(
        self,
        verbose: bool = False,
        indeterminate: bool = False,
        steps: Optional[List[Tuple[ProgressStep, str]]] = None
    ):
        """
        Initialize progress display.
        
        Args:
            verbose: Show detailed progress information
            indeterminate: Show only spinner without percentage
            steps: Custom step definitions
        """
        self.verbose = verbose
        self.indeterminate = indeterminate
        self.steps = steps or self.DEFAULT_STEPS
        self.current_step: Optional[ProgressStep] = None
        self.start_time = time.time()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._details: List[str] = []
        self._error = False
        self._error_message = ""
        self._step_times: Dict[ProgressStep, float] = {}
        self._step_start_time: Optional[float] = None
        self._spinner_index = 0
        
        # Create step message mapping
        self._step_messages = {step: msg for step, msg in self.steps}
    
    def start(self) -> None:
        """Start the progress display."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._thread = threading.Thread(target=self._display_loop, daemon=True)
            self._thread.start()
    
    def stop(self) -> None:
        """Stop the progress display."""
        with self._lock:
            self._running = False
        
        if self._thread:
            self._thread.join(timeout=1)
            
        # Clear the line one final time
        self.clear_line()
        
        # Show final status
        if self._error:
            click.echo(click.style(f"✗ Error: {self._error_message}", fg='red'))
        elif self.current_step == ProgressStep.COMPLETED:
            elapsed = self.get_elapsed_time()
            click.echo(click.style(
                f"✓ Completed in {self.format_time(elapsed)}", 
                fg='green'
            ))
    
    def update(self, step: ProgressStep) -> None:
        """Update the current progress step."""
        with self._lock:
            # Track step duration
            if self.current_step and self._step_start_time:
                self._step_times[self.current_step] = time.time() - self._step_start_time
            
            self.current_step = step
            self._step_start_time = time.time()
            
            # Show verbose update
            if self.verbose:
                message = self.get_step_message(step)
                click.echo(click.style(f"→ {message}", fg='blue'))
    
    def add_detail(self, detail: str) -> None:
        """Add a detail message (shown in verbose mode)."""
        with self._lock:
            self._details.append(detail)
            
        if self.verbose:
            click.echo(f"  {detail}")
    
    def error(self, message: str) -> None:
        """Mark an error occurred."""
        with self._lock:
            self._error = True
            self._error_message = message
    
    def get_step_message(self, step: ProgressStep) -> str:
        """Get the message for a step."""
        return self._step_messages.get(step, step.name.replace('_', ' ').title())
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    def format_time(self, seconds: float) -> str:
        """Format time in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)}s"
        else:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
    
    def get_spinner_frames(self) -> List[str]:
        """Get spinner animation frames."""
        return self.SPINNER_FRAMES
    
    def get_progress_percentage(self) -> int:
        """Calculate progress percentage based on current step."""
        if not self.current_step:
            return 0
        
        # Find step index
        step_indices = {step: i for i, (step, _) in enumerate(self.steps)}
        current_index = step_indices.get(self.current_step, 0)
        total_steps = len(self.steps)
        
        # Calculate percentage
        if total_steps <= 1:
            return 100 if self.current_step == ProgressStep.COMPLETED else 0
        
        percentage = int((current_index / (total_steps - 1)) * 100)
        return min(percentage, 100)
    
    def get_step_duration(self, step: ProgressStep) -> float:
        """Get duration of a specific step."""
        return self._step_times.get(step, 0.0)
    
    def clear_line(self) -> None:
        """Clear the current line."""
        click.echo('\r\033[K', nl=False)
    
    def _display_loop(self):
        """Main display loop running in separate thread."""
        while self._running:
            with self._lock:
                if self._error:
                    break
                
                # Get current state
                current_step = self.current_step
                spinner_frame = self.SPINNER_FRAMES[self._spinner_index]
                self._spinner_index = (self._spinner_index + 1) % len(self.SPINNER_FRAMES)
            
            # Build display string
            if current_step:
                message = self.get_step_message(current_step)
                elapsed = self.format_time(self.get_elapsed_time())
                
                if self.indeterminate:
                    # Just spinner and message
                    display = f"{spinner_frame} {message} ({elapsed})"
                else:
                    # Spinner, message, and percentage
                    percentage = self.get_progress_percentage()
                    display = f"{spinner_frame} {message} {percentage}% ({elapsed})"
                
                # Clear line and show update
                self.clear_line()
                click.echo(display, nl=False)
            
            # Sleep briefly
            time.sleep(0.1)
        
        # Clear spinner when done
        self.clear_line()
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type:
            self.error(str(exc_val))
        self.stop()
        return False


def create_progress_callback(progress_display: ProgressDisplay) -> Callable[[str], None]:
    """
    Create a progress callback function for use with ResumeCustomizer.
    
    Args:
        progress_display: The ProgressDisplay instance to update
        
    Returns:
        Callback function that updates progress based on messages
    """
    def callback(message: str) -> None:
        """Progress callback that interprets messages and updates display."""
        message_lower = message.lower()
        
        # Map messages to progress steps
        if "validating" in message_lower:
            progress_display.update(ProgressStep.VALIDATING)
        elif "reading" in message_lower or "read" in message_lower:
            progress_display.update(ProgressStep.READING_FILES)
        elif "analyzing" in message_lower or "analysis" in message_lower:
            progress_display.update(ProgressStep.ANALYZING)
        elif "customizing" in message_lower or "writing" in message_lower or "write" in message_lower:
            if "tool: write" in message_lower:
                progress_display.update(ProgressStep.WRITING_OUTPUT)
            else:
                progress_display.update(ProgressStep.CUSTOMIZING)
        elif "completed" in message_lower or "success" in message_lower:
            progress_display.update(ProgressStep.COMPLETED)
        elif "error" in message_lower:
            # Extract error message
            progress_display.error(message)
        
        # Always add as detail in verbose mode
        progress_display.add_detail(message)
    
    return callback