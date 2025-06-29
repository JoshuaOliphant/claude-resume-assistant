# ABOUTME: Test suite for the ProgressDisplay class and progress indicators
# ABOUTME: Verifies step tracking, time estimation, and display formatting

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import threading

from resume_customizer.cli.progress import ProgressDisplay, ProgressStep


class TestProgressDisplay:
    """Test suite for the ProgressDisplay class."""
    
    def test_progress_step_enum(self):
        """Test that ProgressStep enum has all required steps."""
        assert hasattr(ProgressStep, 'INITIALIZING')
        assert hasattr(ProgressStep, 'VALIDATING')
        assert hasattr(ProgressStep, 'READING_FILES')
        assert hasattr(ProgressStep, 'ANALYZING')
        assert hasattr(ProgressStep, 'CUSTOMIZING')
        assert hasattr(ProgressStep, 'WRITING_OUTPUT')
        assert hasattr(ProgressStep, 'COMPLETED')
    
    def test_initialization(self):
        """Test ProgressDisplay initialization."""
        display = ProgressDisplay(verbose=False)
        
        assert display.verbose is False
        assert display.current_step is None
        assert display.start_time is not None
        assert len(display.steps) > 0
        assert not display._running
    
    def test_initialization_verbose(self):
        """Test ProgressDisplay initialization in verbose mode."""
        display = ProgressDisplay(verbose=True)
        
        assert display.verbose is True
    
    @patch('click.echo')
    def test_start_display(self, mock_echo):
        """Test starting the progress display."""
        display = ProgressDisplay()
        display.start()
        
        assert display._running is True
        assert display._thread is not None
        assert display._thread.is_alive()
        
        # Stop for cleanup
        display.stop()
    
    @patch('click.echo')
    def test_update_step(self, mock_echo):
        """Test updating progress steps."""
        display = ProgressDisplay()
        display.start()
        
        # Update to first step
        display.update(ProgressStep.VALIDATING)
        assert display.current_step == ProgressStep.VALIDATING
        
        # Update to next step
        display.update(ProgressStep.READING_FILES)
        assert display.current_step == ProgressStep.READING_FILES
        
        display.stop()
    
    @patch('click.echo')
    def test_step_messages(self, mock_echo):
        """Test that each step has a descriptive message."""
        display = ProgressDisplay()
        
        for step in ProgressStep:
            message = display.get_step_message(step)
            assert isinstance(message, str)
            assert len(message) > 0
    
    @patch('click.echo')
    def test_verbose_mode_details(self, mock_echo):
        """Test verbose mode shows detailed information."""
        display = ProgressDisplay(verbose=True)
        display.start()
        
        # Add detail message
        display.add_detail("Reading resume file...")
        
        # Should include detail in verbose mode
        display.update(ProgressStep.READING_FILES)
        
        # Check that detail was displayed
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Reading resume file" in call for call in calls)
        
        display.stop()
    
    @patch('click.echo')
    def test_time_estimation(self, mock_echo):
        """Test time estimation display."""
        display = ProgressDisplay()
        display.start()
        
        # Simulate some progress
        display.update(ProgressStep.VALIDATING)
        time.sleep(0.1)
        display.update(ProgressStep.ANALYZING)
        
        # Get elapsed time
        elapsed = display.get_elapsed_time()
        assert elapsed > 0
        
        # Format time
        time_str = display.format_time(elapsed)
        assert isinstance(time_str, str)
        assert len(time_str) > 0
        
        display.stop()
    
    def test_format_time_seconds(self):
        """Test time formatting for seconds."""
        display = ProgressDisplay()
        
        assert display.format_time(5) == "5s"
        assert display.format_time(59) == "59s"
    
    def test_format_time_minutes(self):
        """Test time formatting for minutes."""
        display = ProgressDisplay()
        
        assert display.format_time(60) == "1m 0s"
        assert display.format_time(125) == "2m 5s"
        assert display.format_time(3661) == "61m 1s"
    
    @patch('click.echo')
    def test_spinner_animation(self, mock_echo):
        """Test spinner animation frames."""
        display = ProgressDisplay()
        
        # Check spinner frames
        frames = display.get_spinner_frames()
        assert len(frames) > 0
        assert all(isinstance(frame, str) for frame in frames)
    
    @patch('click.echo')
    def test_progress_percentage(self, mock_echo):
        """Test progress percentage calculation."""
        display = ProgressDisplay()
        
        # Test each step
        steps = list(ProgressStep)
        for i, step in enumerate(steps):
            display.current_step = step
            percentage = display.get_progress_percentage()
            assert 0 <= percentage <= 100
            
            # Later steps should have higher percentage
            if i > 0:
                display.current_step = steps[i-1]
                prev_percentage = display.get_progress_percentage()
                display.current_step = step
                assert percentage >= prev_percentage
    
    @patch('click.echo')
    def test_stop_display(self, mock_echo):
        """Test stopping the progress display."""
        display = ProgressDisplay()
        display.start()
        
        assert display._running is True
        
        display.stop()
        
        assert display._running is False
        # Thread should finish
        display._thread.join(timeout=1)
        assert not display._thread.is_alive()
    
    @patch('click.echo')
    def test_completion_message(self, mock_echo):
        """Test completion message display."""
        display = ProgressDisplay()
        display.start()
        
        # Update to completed
        display.update(ProgressStep.COMPLETED)
        display.stop()
        
        # Should show completion message
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("complete" in call.lower() or "✓" in call for call in calls)
    
    @patch('click.echo')
    def test_error_handling(self, mock_echo):
        """Test error handling during display."""
        display = ProgressDisplay()
        display.start()
        
        # Mark as error
        display.error("Something went wrong")
        
        assert display._error is True
        assert display._error_message == "Something went wrong"
        
        display.stop()
        
        # Should show error message
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("error" in call.lower() or "✗" in call for call in calls)
    
    @patch('click.echo')
    def test_context_manager(self, mock_echo):
        """Test using ProgressDisplay as context manager."""
        with ProgressDisplay() as display:
            assert display._running is True
            display.update(ProgressStep.ANALYZING)
        
        # Should be stopped after context
        assert display._running is False
    
    @patch('click.echo')
    def test_thread_safety(self, mock_echo):
        """Test thread-safe operations."""
        display = ProgressDisplay()
        display.start()
        
        # Update from multiple threads
        def update_progress():
            for step in [ProgressStep.VALIDATING, ProgressStep.ANALYZING]:
                display.update(step)
                time.sleep(0.01)
        
        threads = [threading.Thread(target=update_progress) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        display.stop()
        
        # Should not crash and should have a valid state
        assert display.current_step is not None
    
    def test_step_duration_tracking(self):
        """Test tracking duration of each step."""
        display = ProgressDisplay()
        display.start()
        
        # Track step durations
        display.update(ProgressStep.VALIDATING)
        time.sleep(0.1)
        display.update(ProgressStep.ANALYZING)
        
        # Get step duration
        duration = display.get_step_duration(ProgressStep.VALIDATING)
        assert duration >= 0.1
        
        display.stop()
    
    @patch('click.echo')
    def test_clear_line(self, mock_echo):
        """Test line clearing functionality."""
        display = ProgressDisplay()
        display.clear_line()
        
        # Should output carriage return and clear codes
        mock_echo.assert_called_once_with('\r\033[K', nl=False)
    
    @patch('click.echo')
    def test_indeterminate_progress(self, mock_echo):
        """Test indeterminate progress (spinner only)."""
        display = ProgressDisplay(indeterminate=True)
        display.start()
        
        # Update to trigger display
        display.update(ProgressStep.CUSTOMIZING)
        
        # Should show spinner without percentage
        time.sleep(0.3)
        
        display.stop()
        
        # Check that echo was called multiple times
        assert mock_echo.call_count > 0
        
        # Check that no percentage was shown in any call
        calls = [str(call) for call in mock_echo.call_args_list]
        # In indeterminate mode, we shouldn't see percentage
        percentage_calls = [call for call in calls if "%" in call and "nl=False" in call]
        assert len(percentage_calls) == 0
    
    def test_custom_steps(self):
        """Test using custom step definitions."""
        custom_steps = [
            (ProgressStep.INITIALIZING, "Setting up"),
            (ProgressStep.CUSTOMIZING, "Processing"),
            (ProgressStep.COMPLETED, "Done")
        ]
        
        display = ProgressDisplay(steps=custom_steps)
        
        assert len(display.steps) == 3
        assert display.get_step_message(ProgressStep.CUSTOMIZING) == "Processing"