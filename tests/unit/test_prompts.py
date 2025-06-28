# ABOUTME: Test suite for orchestrator prompt building functionality
# ABOUTME: Verifies prompt contains all necessary components for resume customization

import pytest
from pathlib import Path

from resume_customizer.core.prompts import build_orchestrator_prompt
from resume_customizer.config import Settings


class TestBuildOrchestratorPrompt:
    """Test suite for the orchestrator prompt builder."""
    
    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings(
            claude_api_key="test-key",
            max_iterations=3
        )
    
    @pytest.fixture
    def file_paths(self):
        """Create test file paths."""
        return {
            "resume_path": "/path/to/resume.md",
            "job_description_path": "/path/to/job_description.md",
            "output_path": "/path/to/output/customized_resume.md"
        }
    
    def test_function_exists(self):
        """Test that build_orchestrator_prompt function exists."""
        assert callable(build_orchestrator_prompt)
    
    def test_includes_file_paths(self, settings, file_paths):
        """Test that prompt includes all file paths."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        assert file_paths["resume_path"] in prompt
        assert file_paths["job_description_path"] in prompt
        assert file_paths["output_path"] in prompt
    
    def test_includes_orchestrator_pattern(self, settings, file_paths):
        """Test that prompt includes orchestrator-workers pattern."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        assert "orchestrator" in prompt.lower()
        assert "sub-agent" in prompt.lower() or "sub agent" in prompt.lower()
        assert "coordinator" in prompt.lower() or "coordinate" in prompt.lower()
    
    def test_includes_sub_agent_roles(self, settings, file_paths):
        """Test that prompt defines all sub-agent roles."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        # Check for key sub-agent roles
        expected_agents = [
            "resume analyzer",
            "job requirements analyzer",
            "gap analysis",
            "ats optimization",
            "content enhancement",
            "quality assurance"
        ]
        
        prompt_lower = prompt.lower()
        for agent in expected_agents:
            assert agent in prompt_lower, f"Missing sub-agent role: {agent}"
    
    def test_includes_truthfulness_constraint(self, settings, file_paths):
        """Test that prompt includes truthfulness constraints."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        prompt_lower = prompt.lower()
        assert "truthful" in prompt_lower or "truth" in prompt_lower
        assert "never add false" in prompt_lower or "no false information" in prompt_lower
        assert "existing" in prompt_lower or "actual" in prompt_lower
    
    def test_includes_iterative_process(self, settings, file_paths):
        """Test that prompt defines iterative refinement process."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        prompt_lower = prompt.lower()
        assert "iteration" in prompt_lower
        assert str(settings.max_iterations) in prompt
        
        # Check for multiple iteration descriptions
        assert "iteration 1:" in prompt_lower
        assert "iteration 2:" in prompt_lower
        assert "iteration 3:" in prompt_lower
    
    def test_includes_ats_optimization(self, settings, file_paths):
        """Test that prompt includes ATS optimization guidelines."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        prompt_lower = prompt.lower()
        assert "ats" in prompt_lower
        assert "keyword" in prompt_lower
        assert "applicant tracking" in prompt_lower or "ats-friendly" in prompt_lower
    
    def test_includes_evaluation_criteria(self, settings, file_paths):
        """Test that prompt specifies evaluation criteria."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        prompt_lower = prompt.lower()
        # Check for evaluation-related terms
        assert any(term in prompt_lower for term in ["evaluat", "assess", "verify", "quality"])
        assert any(term in prompt_lower for term in ["criteria", "requirement", "standard"])
    
    def test_includes_output_instructions(self, settings, file_paths):
        """Test that prompt includes clear output instructions."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        prompt_lower = prompt.lower()
        assert "write" in prompt_lower
        assert "output" in prompt_lower
        assert "final" in prompt_lower
        assert "customized resume" in prompt_lower
    
    def test_includes_file_operations(self, settings, file_paths):
        """Test that prompt mentions file operations."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        prompt_lower = prompt.lower()
        assert "read" in prompt_lower
        assert "write" in prompt_lower
        assert "file" in prompt_lower
    
    def test_handles_different_settings(self, file_paths):
        """Test that prompt adapts to different settings."""
        # Test with different iteration counts
        settings1 = Settings(claude_api_key="test-key", max_iterations=2)
        prompt1 = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings1
        )
        assert "2" in prompt1
        
        settings5 = Settings(claude_api_key="test-key", max_iterations=5)
        prompt5 = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings5
        )
        assert "5" in prompt5
    
    def test_structured_format(self, settings, file_paths):
        """Test that prompt has clear structure with sections."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        # Check for section markers
        assert "##" in prompt  # Markdown headers
        assert "\n\n" in prompt  # Paragraph breaks
        
        # Check for organized sections
        prompt_lower = prompt.lower()
        assert "input" in prompt_lower
        assert "output" in prompt_lower
        assert "process" in prompt_lower or "overview" in prompt_lower
    
    def test_comprehensive_agent_descriptions(self, settings, file_paths):
        """Test that each sub-agent has detailed responsibilities."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        # Each agent should have multiple responsibilities listed
        assert prompt.count("-") >= 20  # Bullet points for responsibilities
        assert prompt.count("Agent") >= 6  # At least 6 sub-agents
    
    def test_includes_critical_constraints(self, settings, file_paths):
        """Test that prompt includes all critical constraints."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        prompt_lower = prompt.lower()
        # Check for key constraints
        assert "constraint" in prompt_lower or "critical" in prompt_lower
        assert "compatibility" in prompt_lower
        assert "relevance" in prompt_lower
        assert "professional" in prompt_lower
    
    def test_actionable_instructions(self, settings, file_paths):
        """Test that prompt provides clear, actionable instructions."""
        prompt = build_orchestrator_prompt(
            resume_path=file_paths["resume_path"],
            job_description_path=file_paths["job_description_path"],
            output_path=file_paths["output_path"],
            settings=settings
        )
        
        # Check for action words
        action_words = ["read", "analyze", "extract", "identify", "create", 
                       "write", "ensure", "verify", "optimize", "enhance"]
        prompt_lower = prompt.lower()
        
        found_actions = sum(1 for word in action_words if word in prompt_lower)
        assert found_actions >= 8, "Prompt should contain multiple action words"