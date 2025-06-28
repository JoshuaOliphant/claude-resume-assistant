# ABOUTME: Unit tests for the JobDescription domain model
# ABOUTME: Tests parsing job postings and extracting key information

import pytest
from typing import List, Set


class TestJobDescriptionModel:
    """Test suite for JobDescription domain model."""
    
    def test_job_description_dataclass_creation(self):
        """Test that JobDescription dataclass can be created with required fields."""
        from resume_customizer.models.job_description import JobDescription
        
        job = JobDescription(
            title="Senior Software Engineer",
            company="Tech Corp",
            raw_content="Full job description text",
            required_skills=["Python", "Django"],
            nice_to_have_skills=["React", "Docker"],
            years_of_experience=5,
            responsibilities=["Build scalable systems", "Lead team"],
            qualifications=["BS in Computer Science"],
            keywords={"python", "django", "api", "microservices"}
        )
        
        assert job.title == "Senior Software Engineer"
        assert job.company == "Tech Corp"
        assert "Python" in job.required_skills
        assert "React" in job.nice_to_have_skills
        assert job.years_of_experience == 5
        assert len(job.responsibilities) == 2
        assert "python" in job.keywords
    
    def test_from_text_basic_parsing(self):
        """Test parsing a basic job description."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
Senior Software Engineer
Tech Corp

About the Role:
We are looking for a Senior Software Engineer with 5+ years of experience.

Requirements:
- 5+ years of experience in software development
- Strong proficiency in Python and Django
- Experience with REST APIs
- Knowledge of SQL databases

Nice to Have:
- Experience with React
- Docker and Kubernetes knowledge
- AWS experience

Responsibilities:
- Design and build scalable web applications
- Lead technical projects
- Mentor junior developers
"""
        
        job = JobDescription.from_text(job_text)
        
        assert job.title == "Senior Software Engineer"
        assert job.company == "Tech Corp"
        assert job.years_of_experience == 5
        assert "Python" in job.required_skills
        assert "Django" in job.required_skills
        assert "React" in job.nice_to_have_skills
        assert "Docker" in job.nice_to_have_skills
        assert any("scalable" in r for r in job.responsibilities)
    
    def test_extract_job_title_variations(self):
        """Test extracting job title from various formats."""
        from resume_customizer.models.job_description import JobDescription
        
        test_cases = [
            # Format 1: Title at top
            ("Software Engineer - Backend\nCompany: Google", "Software Engineer - Backend"),
            # Format 2: With job prefix
            ("Job Title: Senior Developer\nLocation: Seattle", "Senior Developer"),
            # Format 3: Position label
            ("Position: Full Stack Engineer\nDepartment: Engineering", "Full Stack Engineer"),
            # Format 4: Role label  
            ("Role: DevOps Engineer\nTeam: Infrastructure", "DevOps Engineer"),
        ]
        
        for job_text, expected_title in test_cases:
            job = JobDescription.from_text(job_text)
            assert job.title == expected_title
    
    def test_extract_company_name(self):
        """Test extracting company name from various formats."""
        from resume_customizer.models.job_description import JobDescription
        
        test_cases = [
            # Format 1: Company label
            ("Software Engineer\nCompany: Microsoft\nLocation: Redmond", "Microsoft"),
            # Format 2: At/for pattern
            ("Senior Developer at Amazon\nSeattle, WA", "Amazon"),
            # Format 3: Organization label
            ("Data Scientist\nOrganization: Meta\nTeam: AI Research", "Meta"),
            # Format 4: Employer label
            ("DevOps Engineer\nEmployer: Netflix", "Netflix"),
        ]
        
        for job_text, expected_company in test_cases:
            job = JobDescription.from_text(job_text)
            assert job.company == expected_company
    
    def test_extract_years_of_experience(self):
        """Test extracting years of experience requirement."""
        from resume_customizer.models.job_description import JobDescription
        
        test_cases = [
            # Basic patterns
            ("Requires 3+ years of experience", 3),
            ("5-7 years of experience required", 5),
            ("Minimum 10 years experience", 10),
            ("At least 2 years of professional experience", 2),
            # With qualifiers
            ("8+ years of software development experience", 8),
            ("3-5 years Python experience required", 3),
            # Edge cases
            ("1+ year of experience", 1),
            ("15+ years of leadership experience", 15),
        ]
        
        for job_text, expected_years in test_cases:
            job = JobDescription.from_text(job_text)
            assert job.years_of_experience == expected_years
    
    def test_extract_required_skills(self):
        """Test extracting required skills from various sections."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
Software Engineer

Required Skills:
- Python
- Django or Flask
- PostgreSQL
- REST API development

Requirements:
• Experience with JavaScript frameworks (React preferred)
• Strong knowledge of Git
• Linux/Unix proficiency

Must have:
- Docker containerization
- CI/CD pipelines
"""
        
        job = JobDescription.from_text(job_text)
        
        required = job.required_skills
        assert "Python" in required
        assert "Django" in required or "Flask" in required
        assert "PostgreSQL" in required
        assert "Git" in required
        assert "Docker" in required
    
    def test_extract_nice_to_have_skills(self):
        """Test extracting nice-to-have skills."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
Backend Developer

Required:
- Python
- SQL

Nice to have:
- Kubernetes experience
- AWS certification
- GraphQL knowledge

Preferred:
• Redis
• Elasticsearch

Bonus:
- Machine learning experience
- Open source contributions
"""
        
        job = JobDescription.from_text(job_text)
        
        nice_to_have = job.nice_to_have_skills
        assert "Kubernetes" in nice_to_have
        assert "AWS" in nice_to_have
        assert "GraphQL" in nice_to_have
        assert "Redis" in nice_to_have
        assert "Machine Learning" in nice_to_have or "ML" in nice_to_have
    
    def test_extract_responsibilities(self):
        """Test extracting job responsibilities."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
Senior Engineer

Responsibilities:
- Design and implement scalable microservices
- Lead code reviews and maintain code quality
- Collaborate with product managers on requirements
- Mentor junior developers

What you'll do:
• Build RESTful APIs
• Optimize database performance
• Participate in on-call rotation
"""
        
        job = JobDescription.from_text(job_text)
        
        responsibilities = job.responsibilities
        assert len(responsibilities) >= 7
        assert any("microservices" in r for r in responsibilities)
        assert any("code reviews" in r for r in responsibilities)
        assert any("mentor" in r.lower() for r in responsibilities)
        assert any("APIs" in r for r in responsibilities)
    
    def test_extract_qualifications(self):
        """Test extracting qualifications and education requirements."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
Data Scientist

Qualifications:
- Bachelor's degree in Computer Science, Mathematics, or related field
- Master's degree preferred
- 3+ years of experience in data science
- Strong statistical knowledge

Education:
• BS/MS in Computer Science or equivalent
• PhD is a plus
"""
        
        job = JobDescription.from_text(job_text)
        
        qualifications = job.qualifications
        assert any("Bachelor" in q for q in qualifications)
        assert any("Master" in q for q in qualifications)
        assert any("Computer Science" in q for q in qualifications)
    
    def test_keyword_extraction(self):
        """Test extraction of ATS keywords."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
Full Stack Developer

We're looking for a Full Stack Developer with expertise in Python, JavaScript, 
and React. You'll work with Django REST framework, PostgreSQL, and Redis.

Requirements:
- Python programming
- JavaScript ES6+  
- React.js and Redux
- RESTful API design
- Agile methodology
- Test-driven development (TDD)
- Continuous Integration/Continuous Deployment (CI/CD)
"""
        
        job = JobDescription.from_text(job_text)
        
        keywords = job.keywords
        # Should extract technical terms
        assert "python" in keywords
        assert "javascript" in keywords
        assert "react" in keywords or "react.js" in keywords
        assert "django" in keywords
        assert "postgresql" in keywords
        assert "redis" in keywords
        assert "api" in keywords or "restful" in keywords
        assert "agile" in keywords
        assert "tdd" in keywords or "test-driven" in keywords
        assert "ci/cd" in keywords or "continuous integration" in keywords
    
    def test_handles_unstructured_text(self):
        """Test parsing completely unstructured job description."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
We're hiring a Senior Backend Engineer to join our growing team at StartupXYZ!

You'll be working on our core platform using Python and Django. We need someone 
with at least 5 years of experience building scalable web applications. 

You should be comfortable with PostgreSQL, Redis, and have experience with 
microservices architecture. Knowledge of Docker and Kubernetes would be great 
but not required.

Day to day, you'll be designing APIs, improving system performance, and 
collaborating with our frontend team. We'd love someone who can also help 
mentor our junior developers.

If you have a CS degree and experience with AWS, that's even better!
"""
        
        job = JobDescription.from_text(job_text)
        
        assert job.title == "Senior Backend Engineer"
        assert job.company == "StartupXYZ"
        assert job.years_of_experience == 5
        assert "Python" in job.required_skills
        assert "Django" in job.required_skills
        assert "Docker" in job.nice_to_have_skills
        assert any("APIs" in r for r in job.responsibilities)
    
    def test_categorize_requirements(self):
        """Test categorization of requirements by importance."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
Software Engineer

Must have:
- Python expertise
- SQL proficiency

Should have:
- Cloud experience
- DevOps knowledge

Good to have:
- ML background
- Mobile development
"""
        
        job = JobDescription.from_text(job_text)
        
        # Check that skills are properly categorized
        assert "Python" in job.required_skills
        assert "SQL" in job.required_skills
        assert "Cloud" in job.nice_to_have_skills or "Cloud" in job.required_skills
        assert "ML" in job.nice_to_have_skills or "Mobile" in job.nice_to_have_skills
    
    def test_skill_normalization(self):
        """Test that skills are normalized for consistency."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = """
Developer Position

Required:
- PYTHON programming
- javascript/typescript
- React.JS
- node.js
- postgresQL
"""
        
        job = JobDescription.from_text(job_text)
        
        # Skills should be normalized
        assert "Python" in job.required_skills  # Capitalized
        assert "JavaScript" in job.required_skills or "TypeScript" in job.required_skills
        assert "React" in job.required_skills or "React.js" in job.required_skills
        assert "Node.js" in job.required_skills
        assert "PostgreSQL" in job.required_skills
    
    def test_empty_text_handling(self):
        """Test handling of empty or invalid text."""
        from resume_customizer.models.job_description import JobDescription
        
        with pytest.raises(ValueError, match="Empty or invalid job description"):
            JobDescription.from_text("")
        
        with pytest.raises(ValueError, match="Empty or invalid job description"):
            JobDescription.from_text("   \n\n   ")
    
    def test_missing_information_defaults(self):
        """Test that missing information has sensible defaults."""
        from resume_customizer.models.job_description import JobDescription
        
        job_text = "Software Developer position available."
        
        job = JobDescription.from_text(job_text)
        
        assert job.title == "Software Developer"  # Extracted from text
        assert job.company == "Unknown"  # Default when not found
        assert job.years_of_experience == 0  # Default when not specified
        assert job.required_skills == []  # Empty when none found
        assert job.nice_to_have_skills == []
        assert job.responsibilities == []
    
    def test_validate_method(self):
        """Test validation of job description completeness."""
        from resume_customizer.models.job_description import JobDescription
        
        # Complete job description
        complete_job = JobDescription(
            title="Software Engineer",
            company="Tech Corp",
            raw_content="Full description",
            required_skills=["Python", "SQL"],
            years_of_experience=3
        )
        
        errors = complete_job.validate()
        assert len(errors) == 0
        
        # Incomplete job description
        incomplete_job = JobDescription(
            title="Unknown",
            company="Unknown",
            raw_content="Brief text",
            required_skills=[]
        )
        
        errors = incomplete_job.validate()
        assert len(errors) > 0
        assert any("title" in e for e in errors)
        assert any("skills" in e for e in errors)