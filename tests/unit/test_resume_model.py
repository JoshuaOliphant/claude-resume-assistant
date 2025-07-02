# ABOUTME: Unit tests for the Resume domain model
# ABOUTME: Tests parsing, section detection, and information extraction

import pytest
from datetime import datetime
from typing import List, Dict

from resume_customizer.models.resume import Resume, Section


class TestResumeModel:
    """Test suite for Resume domain model."""
    
    def test_resume_dataclass_creation(self):
        """Test that Resume dataclass can be created with required fields."""
        
        sections = [
            Section(name="Summary", content="Experienced developer"),
            Section(name="Experience", content="Software Engineer at Tech Corp")
        ]
        
        resume = Resume(
            full_name="John Doe",
            email="john@example.com",
            phone="555-1234",
            sections=sections,
            raw_content="# John Doe\n\n## Summary\nExperienced developer"
        )
        
        assert resume.full_name == "John Doe"
        assert resume.email == "john@example.com"
        assert resume.phone == "555-1234"
        assert len(resume.sections) == 2
        assert resume.raw_content.startswith("# John Doe")
    
    def test_section_dataclass(self):
        """Test Section dataclass."""
        
        section = Section(
            name="Experience",
            content="5 years as Software Engineer",
            original_name="PROFESSIONAL EXPERIENCE"
        )
        
        assert section.name == "Experience"
        assert section.content == "5 years as Software Engineer"
        assert section.original_name == "PROFESSIONAL EXPERIENCE"
    
    def test_from_markdown_basic_parsing(self):
        """Test parsing basic markdown resume."""
        
        markdown = """# John Doe
Software Engineer
john.doe@email.com | 555-123-4567

## Summary
Experienced software engineer with 5 years in web development.

## Experience
**Senior Software Engineer** - Tech Corp (2020-Present)
- Led team of 4 engineers
- Developed microservices

## Skills
- Python, JavaScript, React
- Docker, Kubernetes

## Education
BS Computer Science - State University (2018)
"""
        
        resume = Resume.from_markdown(markdown)
        
        assert resume.full_name == "John Doe"
        assert resume.email == "john.doe@email.com"
        assert resume.phone == "555-123-4567"
        assert resume.raw_content == markdown
        
        # Check sections
        section_names = [s.name for s in resume.sections]
        assert "Summary" in section_names
        assert "Experience" in section_names
        assert "Skills" in section_names
        assert "Education" in section_names
    
    def test_section_content_preservation(self):
        """Test that section content preserves formatting."""
        
        markdown = """# Jane Smith

## Experience
**Software Engineer** | *TechCorp* | 2020-2023
- Developed REST APIs using Python and Django
- Implemented CI/CD pipelines
  - Reduced deployment time by 50%
  - Automated testing processes

**Junior Developer** | StartupXYZ | 2018-2020
"""
        
        resume = Resume.from_markdown(markdown)
        experience_section = next(s for s in resume.sections if s.name == "Experience")
        
        # Check that formatting is preserved
        assert "**Software Engineer**" in experience_section.content
        assert "  - Reduced deployment time" in experience_section.content
        assert experience_section.content.strip().endswith("2018-2020")
    
    def test_handles_various_section_names(self):
        """Test that parser handles various section naming conventions."""
        
        markdown = """# John Doe

## PROFESSIONAL SUMMARY
Senior developer with extensive experience.

## Work History
Worked at various companies.

## Technical Skills
Python, Java, C++

## EDUCATION & TRAINING
MS Computer Science
"""
        
        resume = Resume.from_markdown(markdown)
        section_names = [s.name for s in resume.sections]
        
        # Should normalize to standard names
        assert "Summary" in section_names
        assert "Experience" in section_names
        assert "Skills" in section_names
        assert "Education" in section_names
        
        # Should preserve original names
        summary_section = next(s for s in resume.sections if s.name == "Summary")
        assert summary_section.original_name == "PROFESSIONAL SUMMARY"
    
    def test_extract_contact_info(self):
        """Test extraction of contact information."""
        
        # Test various contact formats
        test_cases = [
            # Format 1: Pipe separated
            """# John Doe
john@email.com | (555) 123-4567 | LinkedIn: /in/johndoe
""",
            # Format 2: Line breaks
            """# John Doe
Email: john@email.com
Phone: 555.123.4567
""",
            # Format 2: Mixed format
            """# John Doe
Contact: john@email.com • 555-123-4567
"""
        ]
        
        for markdown in test_cases:
            resume = Resume.from_markdown(markdown)
            assert resume.email == "john@email.com"
            assert resume.phone in ["555-123-4567", "(555) 123-4567", "555.123.4567"]
    
    def test_extract_years_of_experience(self):
        """Test extraction of years of experience."""
        
        markdown = """# John Doe

## Summary
Software engineer with 8 years of experience in full-stack development.

## Experience
**Senior Engineer** - Company A (2020-2024)
4 years leading technical projects.

**Software Engineer** - Company B (2018-2020)
2 years developing web applications.

**Junior Developer** - Company C (2016-2018)
2 years learning and growing.
"""
        
        resume = Resume.from_markdown(markdown)
        
        assert resume.years_of_experience == 8
        assert resume.experience_calculation_method == "from_summary"
    
    def test_calculate_experience_from_dates(self):
        """Test calculating experience from work history dates."""
        
        markdown = """# John Doe

## Experience
**Senior Engineer** - Company A (2020-Present)
**Software Engineer** - Company B (2018-2020)
**Junior Developer** - Company C (2016-2018)
"""
        
        resume = Resume.from_markdown(markdown)
        
        # Should calculate from 2016 to present
        current_year = datetime.now().year
        expected_years = current_year - 2016
        assert resume.years_of_experience == expected_years
        assert resume.experience_calculation_method == "from_dates"
    
    def test_extract_skills_list(self):
        """Test extraction of skills from various formats."""
        
        markdown = """# John Doe

## Skills
**Programming Languages:** Python, JavaScript, TypeScript, Java
**Frameworks:** Django, React, Node.js, Spring Boot
**Databases:** PostgreSQL, MongoDB, Redis
**Tools:** Docker, Kubernetes, Jenkins, Git
"""
        
        resume = Resume.from_markdown(markdown)
        
        assert "Python" in resume.skills
        assert "JavaScript" in resume.skills
        assert "Django" in resume.skills
        assert "Docker" in resume.skills
        assert len(resume.skills) >= 12
    
    def test_skills_extraction_bullet_format(self):
        """Test skills extraction from bullet point format."""
        
        markdown = """# John Doe

## Technical Skills
- Python, Django, Flask
- JavaScript, React, Vue.js
- PostgreSQL, MySQL
- AWS, Docker, Kubernetes
"""
        
        resume = Resume.from_markdown(markdown)
        
        assert "Python" in resume.skills
        assert "React" in resume.skills
        assert "AWS" in resume.skills
    
    def test_validates_required_sections(self):
        """Test validation of required sections."""
        
        # Missing experience section
        markdown = """# John Doe

## Summary
Software engineer.

## Skills
Python, JavaScript
"""
        
        resume = Resume.from_markdown(markdown)
        validation_errors = resume.validate()
        
        assert len(validation_errors) > 0
        assert any("Experience" in error for error in validation_errors)
    
    def test_minimal_required_sections(self):
        """Test that resume with minimal required sections validates."""
        
        markdown = """# John Doe
john@email.com

## Summary
Experienced developer.

## Experience
Software Engineer at Tech Corp.

## Skills
Python, JavaScript
"""
        
        resume = Resume.from_markdown(markdown)
        validation_errors = resume.validate()
        
        assert len(validation_errors) == 0
    
    def test_empty_markdown_handling(self):
        """Test handling of empty or invalid markdown."""
        
        with pytest.raises(ValueError, match="Empty or invalid markdown"):
            Resume.from_markdown("")
        
        with pytest.raises(ValueError, match="Empty or invalid markdown"):
            Resume.from_markdown("   \n\n   ")
    
    def test_no_name_extraction(self):
        """Test handling when name cannot be extracted."""
        
        markdown = """## Summary
Software engineer.

## Experience
Worked at companies.
"""
        
        resume = Resume.from_markdown(markdown)
        assert resume.full_name == "Unknown"
    
    def test_get_section_by_name(self):
        """Test getting section by name."""
        
        markdown = """# John Doe

## Summary
Experienced developer.

## Experience
Software Engineer.
"""
        
        resume = Resume.from_markdown(markdown)
        
        summary = resume.get_section("Summary")
        assert summary is not None
        assert summary.content == "Experienced developer."
        
        # Test case insensitive
        experience = resume.get_section("experience")
        assert experience is not None
        
        # Test non-existent section
        education = resume.get_section("Education")
        assert education is None
    
    def test_section_ordering_preserved(self):
        """Test that section order is preserved from original."""
        
        markdown = """# John Doe

## Skills
Python, Java

## Summary
Developer

## Experience
Engineer

## Education
BS CS
"""
        
        resume = Resume.from_markdown(markdown)
        section_names = [s.name for s in resume.sections]
        
        # Order should be: Skills, Summary, Experience, Education
        assert section_names.index("Skills") < section_names.index("Summary")
        assert section_names.index("Summary") < section_names.index("Experience")
        assert section_names.index("Experience") < section_names.index("Education")