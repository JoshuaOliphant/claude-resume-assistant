# ABOUTME: Main package for the resume customizer application
# ABOUTME: Provides AI-powered resume customization using Claude Code SDK

"""
Resume Customizer - AI-powered resume customization tool.

This package provides functionality to customize resumes for specific job applications
using Claude AI, with built-in cost tracking and budget management.
"""

from .cost_tracker import CostTracker, APICall

__version__ = "0.1.0"
__all__ = ["CostTracker", "APICall"]