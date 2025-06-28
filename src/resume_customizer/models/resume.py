# ABOUTME: Domain model for resume representation and parsing
# ABOUTME: Handles markdown parsing, section detection, and information extraction

"""Resume domain model for parsing and representing resume data."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from resume_customizer.utils.logging import get_logger

logger = get_logger("models.resume")


@dataclass
class Section:
    """Represents a section in a resume."""
    name: str  # Normalized name (e.g., "Experience")
    content: str  # The content of the section
    original_name: Optional[str] = None  # Original name from markdown (e.g., "WORK HISTORY")


@dataclass
class Resume:
    """Domain model representing a parsed resume."""
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    sections: List[Section] = field(default_factory=list)
    raw_content: str = ""
    skills: List[str] = field(default_factory=list)
    years_of_experience: Optional[int] = None
    experience_calculation_method: Optional[str] = None
    
    # Section name mappings for normalization
    SECTION_MAPPINGS = {
        # Summary variations
        "summary": "Summary",
        "professional summary": "Summary",
        "profile": "Summary",
        "objective": "Summary",
        "career objective": "Summary",
        "executive summary": "Summary",
        
        # Experience variations
        "experience": "Experience",
        "work experience": "Experience",
        "professional experience": "Experience",
        "employment": "Experience",
        "work history": "Experience",
        "employment history": "Experience",
        "career history": "Experience",
        
        # Skills variations
        "skills": "Skills",
        "technical skills": "Skills",
        "core competencies": "Skills",
        "competencies": "Skills",
        "expertise": "Skills",
        "qualifications": "Skills",
        
        # Education variations
        "education": "Education",
        "education & training": "Education",
        "academic background": "Education",
        "qualifications": "Education",
        "certifications": "Education",
    }
    
    @classmethod
    def from_markdown(cls, markdown: str) -> "Resume":
        """
        Parse a resume from markdown content.
        
        Args:
            markdown: The markdown content of the resume
            
        Returns:
            Resume instance with parsed data
            
        Raises:
            ValueError: If markdown is empty or invalid
        """
        if not markdown or not markdown.strip():
            raise ValueError("Empty or invalid markdown content")
        
        logger.debug("Parsing resume from markdown")
        
        # Extract basic info
        full_name = cls._extract_name(markdown)
        email = cls._extract_email(markdown)
        phone = cls._extract_phone(markdown)
        
        # Parse sections
        sections = cls._parse_sections(markdown)
        
        # Create resume instance
        resume = cls(
            full_name=full_name,
            email=email,
            phone=phone,
            sections=sections,
            raw_content=markdown
        )
        
        # Extract additional info
        resume.skills = resume._extract_skills()
        resume.years_of_experience, resume.experience_calculation_method = resume._calculate_experience()
        
        return resume
    
    @staticmethod
    def _extract_name(markdown: str) -> str:
        """Extract name from markdown, typically from first H1."""
        h1_match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
        if h1_match:
            name = h1_match.group(1).strip()
            # Remove any trailing contact info from name line
            name = re.split(r'\s*[\|•]\s*', name)[0].strip()
            return name
        return "Unknown"
    
    @staticmethod
    def _extract_email(markdown: str) -> Optional[str]:
        """Extract email address from markdown."""
        # Look for email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, markdown)
        if email_match:
            return email_match.group(0)
        return None
    
    @staticmethod
    def _extract_phone(markdown: str) -> Optional[str]:
        """Extract phone number from markdown."""
        # Look for various phone formats
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (555) 123-4567 or 555-123-4567 or 555.123.4567
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',  # 555-123-4567
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, markdown)
            if phone_match:
                return phone_match.group(0)
        return None
    
    @classmethod
    def _parse_sections(cls, markdown: str) -> List[Section]:
        """Parse markdown into sections based on headers."""
        sections = []
        
        # Split by H2 headers (## Section Name)
        section_pattern = r'^##\s+(.+)$'
        lines = markdown.split('\n')
        
        current_section_name = None
        current_section_content = []
        current_original_name = None
        
        for line in lines:
            header_match = re.match(section_pattern, line)
            
            if header_match:
                # Save previous section if exists
                if current_section_name and current_section_content:
                    content = '\n'.join(current_section_content).strip()
                    normalized_name = cls._normalize_section_name(current_section_name)
                    sections.append(Section(
                        name=normalized_name,
                        content=content,
                        original_name=current_original_name
                    ))
                
                # Start new section
                current_original_name = header_match.group(1).strip()
                current_section_name = current_original_name
                current_section_content = []
            else:
                # Add line to current section
                if current_section_name:
                    current_section_content.append(line)
        
        # Save last section
        if current_section_name and current_section_content:
            content = '\n'.join(current_section_content).strip()
            normalized_name = cls._normalize_section_name(current_section_name)
            sections.append(Section(
                name=normalized_name,
                content=content,
                original_name=current_original_name
            ))
        
        return sections
    
    @classmethod
    def _normalize_section_name(cls, name: str) -> str:
        """Normalize section name to standard form."""
        normalized = name.lower().strip()
        return cls.SECTION_MAPPINGS.get(normalized, name)
    
    def get_section(self, name: str) -> Optional[Section]:
        """Get a section by name (case-insensitive)."""
        normalized_name = self._normalize_section_name(name)
        for section in self.sections:
            if section.name.lower() == normalized_name.lower():
                return section
        return None
    
    def _extract_skills(self) -> List[str]:
        """Extract skills from the Skills section."""
        skills = []
        skills_section = self.get_section("Skills")
        
        if not skills_section:
            return skills
        
        content = skills_section.content
        
        # Extract skills from various formats
        # Format 1: Category: skill1, skill2, skill3
        category_pattern = r'^[^:]+:\s*(.+)$'
        for line in content.split('\n'):
            match = re.match(category_pattern, line)
            if match:
                skill_list = match.group(1)
                # Remove markdown formatting like ** from skills
                skill_list = re.sub(r'\*+', '', skill_list)
                skills.extend([s.strip() for s in skill_list.split(',') if s.strip()])
            # Format 2: Bullet points with comma-separated skills
            elif line.strip().startswith('-'):
                skill_line = line.strip()[1:].strip()
                skills.extend([s.strip() for s in skill_line.split(',') if s.strip()])
            # Format 3: Just comma-separated skills
            elif ',' in line and ':' not in line:
                skills.extend([s.strip() for s in line.split(',') if s.strip()])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills
    
    def _calculate_experience(self) -> Tuple[Optional[int], Optional[str]]:
        """Calculate years of experience from resume content."""
        # Method 1: Check summary for explicit mention
        summary = self.get_section("Summary")
        if summary:
            # Look for patterns like "8 years of experience"
            years_pattern = r'(\d+)\s*(?:\+\s*)?years?\s*(?:of\s*)?(?:experience|expertise)'
            match = re.search(years_pattern, summary.content, re.IGNORECASE)
            if match:
                return int(match.group(1)), "from_summary"
        
        # Method 2: Calculate from experience dates
        experience = self.get_section("Experience")
        if experience:
            # Find all year ranges
            date_pattern = r'\b(\d{4})\s*[-–]\s*(?:(\d{4})|Present|Current)\b'
            matches = re.findall(date_pattern, experience.content, re.IGNORECASE)
            
            if matches:
                earliest_year = None
                latest_year = datetime.now().year
                
                for start_year, end_year in matches:
                    start = int(start_year)
                    if earliest_year is None or start < earliest_year:
                        earliest_year = start
                    
                    if end_year and end_year not in ['Present', 'Current']:
                        end = int(end_year)
                        if end > latest_year:
                            latest_year = end
                
                if earliest_year:
                    return latest_year - earliest_year, "from_dates"
        
        return None, None
    
    def validate(self) -> List[str]:
        """
        Validate the resume has required sections.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check for required sections
        required_sections = ["Summary", "Experience", "Skills"]
        for section_name in required_sections:
            if not self.get_section(section_name):
                errors.append(f"Missing required section: {section_name}")
        
        # Check for contact info
        if not self.email:
            errors.append("Missing email address")
        
        return errors