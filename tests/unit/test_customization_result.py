# ABOUTME: Test suite for the CustomizationResult model
# ABOUTME: Verifies change tracking, scoring, and summary generation

import pytest
from datetime import datetime
from dataclasses import asdict

from resume_customizer.models.result import (
    CustomizationResult,
    ChangeType,
    Change,
    SectionChange,
    KeywordIntegration,
    DiffLine,
    DiffType
)


class TestCustomizationResult:
    """Test suite for CustomizationResult model."""
    
    @pytest.fixture
    def sample_result(self):
        """Create a sample customization result for testing."""
        return CustomizationResult(
            original_content="Original resume content",
            customized_content="Customized resume content",
            match_score=85.5,
            changes=[
                Change(
                    type=ChangeType.CONTENT_REWRITE,
                    section="Experience",
                    description="Reworded job descriptions to emphasize leadership"
                ),
                Change(
                    type=ChangeType.KEYWORD_ADDITION,
                    section="Skills",
                    description="Added 'Python' and 'AWS' keywords"
                )
            ],
            integrated_keywords=["Python", "AWS", "Leadership", "Agile"],
            reordered_sections=[
                SectionChange(
                    original_position=2,
                    new_position=1,
                    section_name="Skills"
                )
            ],
            timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )
    
    def test_dataclass_creation(self):
        """Test that CustomizationResult can be created with required fields."""
        result = CustomizationResult(
            original_content="Original",
            customized_content="Customized",
            match_score=75.0,
            changes=[],
            integrated_keywords=[],
            reordered_sections=[]
        )
        
        assert result.original_content == "Original"
        assert result.customized_content == "Customized"
        assert result.match_score == 75.0
        assert result.changes == []
        assert result.integrated_keywords == []
        assert result.reordered_sections == []
        assert isinstance(result.timestamp, datetime)
    
    def test_change_types(self):
        """Test that all change types are properly defined."""
        assert ChangeType.CONTENT_REWRITE == "content_rewrite"
        assert ChangeType.KEYWORD_ADDITION == "keyword_addition"
        assert ChangeType.SECTION_REORDER == "section_reorder"
        assert ChangeType.FORMAT_UPDATE == "format_update"
        assert ChangeType.SECTION_EMPHASIS == "section_emphasis"
    
    def test_change_summary_generation(self, sample_result):
        """Test that change summary is generated correctly."""
        summary = sample_result.get_change_summary()
        
        assert "Match Score: 85.5%" in summary
        assert "Total Changes: 2" in summary
        assert "Keywords Added: 4" in summary
        assert "Sections Reordered: 1" in summary
        assert "Experience: Reworded job descriptions to emphasize leadership" in summary
        assert "Skills: Added 'Python' and 'AWS' keywords" in summary
    
    def test_detailed_summary(self, sample_result):
        """Test detailed summary generation."""
        summary = sample_result.get_detailed_summary()
        
        assert "RESUME CUSTOMIZATION SUMMARY" in summary
        assert "Generated at:" in summary
        assert "Match Score: 85.5%" in summary
        assert "Integrated Keywords:" in summary
        assert "- Python" in summary
        assert "- AWS" in summary
        assert "Section Order Changes:" in summary
        assert "Skills moved from position 2 to position 1" in summary
    
    def test_keyword_frequency_analysis(self):
        """Test keyword frequency analysis in the customized content."""
        result = CustomizationResult(
            original_content="Software Engineer with Java experience",
            customized_content="Python Software Engineer with Python and AWS experience. Python expert.",
            match_score=90.0,
            changes=[],
            integrated_keywords=["Python", "AWS"],
            reordered_sections=[]
        )
        
        freq = result.get_keyword_frequency()
        assert freq["Python"] == 3
        assert freq["AWS"] == 1
    
    def test_diff_generation(self):
        """Test diff generation between original and customized content."""
        result = CustomizationResult(
            original_content="Line 1\nLine 2\nLine 3",
            customized_content="Line 1\nModified Line 2\nLine 3\nLine 4",
            match_score=80.0,
            changes=[],
            integrated_keywords=[],
            reordered_sections=[]
        )
        
        diff = result.generate_diff()
        
        assert len(diff) == 5
        assert diff[0] == DiffLine(type=DiffType.UNCHANGED, content="Line 1", line_num=1)
        assert diff[1] == DiffLine(type=DiffType.REMOVED, content="Line 2", line_num=2)
        assert diff[2] == DiffLine(type=DiffType.ADDED, content="Modified Line 2", line_num=2)
        assert diff[3] == DiffLine(type=DiffType.UNCHANGED, content="Line 3", line_num=3)
        assert diff[4] == DiffLine(type=DiffType.ADDED, content="Line 4", line_num=4)
    
    def test_cli_format_output(self, sample_result):
        """Test CLI-friendly formatted output."""
        output = sample_result.format_for_cli()
        
        # Should have color codes for terminal
        assert "\033[" in output  # ANSI color code
        assert "✓" in output or "✔" in output  # Success checkmark
        assert "85.5%" in output
        assert "Changes Applied" in output
    
    def test_export_to_dict(self, sample_result):
        """Test exporting result to dictionary."""
        data = sample_result.to_dict()
        
        assert data["original_content"] == "Original resume content"
        assert data["customized_content"] == "Customized resume content"
        assert data["match_score"] == 85.5
        assert len(data["changes"]) == 2
        assert len(data["integrated_keywords"]) == 4
        assert data["timestamp"] == "2024-01-01T12:00:00"
    
    def test_export_to_json(self, sample_result):
        """Test exporting result to JSON string."""
        json_str = sample_result.to_json()
        
        import json
        data = json.loads(json_str)
        
        assert data["match_score"] == 85.5
        assert "changes" in data
        assert "integrated_keywords" in data
    
    def test_save_to_file(self, tmp_path, sample_result):
        """Test saving result to file."""
        output_file = tmp_path / "result.json"
        
        sample_result.save_to_file(str(output_file))
        
        assert output_file.exists()
        
        import json
        with open(output_file) as f:
            data = json.load(f)
        
        assert data["match_score"] == 85.5
    
    def test_match_score_validation(self):
        """Test that match score is validated to be between 0 and 100."""
        with pytest.raises(ValueError, match="Match score must be between 0 and 100"):
            CustomizationResult(
                original_content="",
                customized_content="",
                match_score=150.0,
                changes=[],
                integrated_keywords=[],
                reordered_sections=[]
            )
        
        with pytest.raises(ValueError, match="Match score must be between 0 and 100"):
            CustomizationResult(
                original_content="",
                customized_content="",
                match_score=-10.0,
                changes=[],
                integrated_keywords=[],
                reordered_sections=[]
            )
    
    def test_improvement_percentage(self):
        """Test calculation of improvement percentage."""
        # Assuming original had 2 keywords and customized has 6
        result = CustomizationResult(
            original_content="Engineer with Java skills",
            customized_content="Python Engineer with Python, AWS, Docker, Kubernetes skills",
            match_score=90.0,
            changes=[],
            integrated_keywords=["Python", "AWS", "Docker", "Kubernetes"],
            reordered_sections=[]
        )
        
        improvement = result.calculate_improvement_percentage(original_keywords=2)
        assert improvement == 100.0  # 100% improvement (2 to 4 keywords)
    
    def test_get_statistics(self, sample_result):
        """Test statistics generation."""
        stats = sample_result.get_statistics()
        
        assert stats["total_changes"] == 2
        assert stats["keywords_added"] == 4
        assert stats["sections_reordered"] == 1
        assert stats["content_rewrite_count"] == 1
        assert stats["keyword_addition_count"] == 1
        assert stats["match_score"] == 85.5
    
    def test_empty_result(self):
        """Test handling of empty customization result."""
        result = CustomizationResult(
            original_content="",
            customized_content="",
            match_score=0.0,
            changes=[],
            integrated_keywords=[],
            reordered_sections=[]
        )
        
        summary = result.get_change_summary()
        assert "No changes made" in summary
        
        stats = result.get_statistics()
        assert stats["total_changes"] == 0
    
    def test_markdown_export(self, sample_result):
        """Test exporting result summary as markdown."""
        markdown = sample_result.export_as_markdown()
        
        assert "# Resume Customization Report" in markdown
        assert "## Match Score: 85.5%" in markdown
        assert "### Changes Applied" in markdown
        assert "- **Experience**: Reworded job descriptions" in markdown
        assert "### Integrated Keywords" in markdown
        assert "- Python" in markdown
        
    def test_comparison_metrics(self):
        """Test generation of before/after comparison metrics."""
        result = CustomizationResult(
            original_content="Short resume content here",
            customized_content="Much longer and more detailed resume content here with keywords",
            match_score=92.0,
            changes=[],
            integrated_keywords=["resume", "content", "keywords"],
            reordered_sections=[]
        )
        
        metrics = result.get_comparison_metrics()
        
        assert metrics["original_length"] == 25
        assert metrics["customized_length"] == 63
        assert metrics["length_increase_percent"] > 100
        assert metrics["keyword_density_change"] > 0