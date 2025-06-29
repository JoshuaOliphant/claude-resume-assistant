# ABOUTME: Test fixtures and data for integration tests
# ABOUTME: Provides reusable test data, sample files, and fixture management

"""Test fixtures for integration tests."""

import os
import tempfile
from pathlib import Path
from typing import Dict, Tuple, Any
import pytest
from datetime import datetime


class TestDataFixtures:
    """Provides test data for integration tests."""
    
    @staticmethod
    def get_sample_resume(experience_level: str = "mid") -> str:
        """Get a sample resume based on experience level."""
        resumes = {
            "entry": """# Alex Johnson

## Contact Information
- Email: alex.johnson@email.com
- Phone: (555) 987-6543
- Location: Austin, TX
- GitHub: github.com/alexjohnson

## Summary
Recent computer science graduate passionate about software development and eager to contribute to innovative projects.

## Education
**BS Computer Science** - University of Texas at Austin (2023)
- GPA: 3.7/4.0
- Relevant Coursework: Data Structures, Algorithms, Web Development, Database Systems

## Projects

### Personal Portfolio Website (2023)
- Built responsive website using HTML, CSS, and JavaScript
- Implemented contact form with Node.js backend
- Deployed on Heroku with CI/CD pipeline

### Task Management App (2023)
- Developed full-stack application using React and Express
- Implemented user authentication and data persistence
- Used MongoDB for data storage

## Skills
- Languages: Python, JavaScript, Java, SQL
- Web: HTML, CSS, React, Node.js
- Tools: Git, VS Code, Linux
- Other: Agile methodologies, Problem solving""",

            "mid": """# Sarah Chen

## Contact Information
- Email: sarah.chen@techmail.com
- Phone: (555) 234-5678
- Location: Seattle, WA
- LinkedIn: linkedin.com/in/sarachen
- GitHub: github.com/sarahchen

## Professional Summary
Experienced full-stack developer with 5 years of experience building scalable web applications. Strong expertise in Python backend development and modern JavaScript frameworks. Proven track record of delivering high-quality software solutions and leading technical initiatives.

## Professional Experience

### Senior Software Engineer - TechCorp Solutions (2021-Present)
- Lead development of microservices architecture serving 1M+ daily active users
- Implemented RESTful APIs using Python, FastAPI, and PostgreSQL
- Reduced API response time by 40% through query optimization and caching strategies
- Mentored team of 3 junior developers and conducted code reviews
- Introduced automated testing practices, increasing code coverage from 45% to 85%

### Software Engineer - Digital Innovations Inc (2019-2021)
- Developed customer-facing web applications using React and TypeScript
- Built real-time data processing pipeline using Apache Kafka and Python
- Collaborated with product team to define technical requirements
- Implemented CI/CD pipelines using Jenkins and Docker
- Participated in on-call rotation and resolved production incidents

### Junior Developer - StartupXYZ (2018-2019)
- Created responsive UI components using React and Material-UI
- Assisted in database design and optimization
- Fixed bugs and implemented feature enhancements
- Participated in daily standups and sprint planning

## Technical Skills
- **Languages**: Python, JavaScript, TypeScript, SQL, Java
- **Backend**: Django, FastAPI, Flask, Node.js, Express
- **Frontend**: React, Redux, Vue.js, HTML5, CSS3, Sass
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Cloud & DevOps**: AWS (EC2, S3, RDS), Docker, Kubernetes, CI/CD
- **Tools**: Git, JIRA, Confluence, VS Code, PyCharm

## Education
**BS Computer Science** - University of Washington (2018)
- Graduated Magna Cum Laude
- Dean's List: 4 semesters

## Certifications
- AWS Certified Developer - Associate (2022)
- Python Institute PCEP Certification (2020)""",

            "senior": """# Michael Rodriguez

## Contact Information
- Email: michael.rodriguez@techleader.com
- Phone: (555) 345-6789
- Location: San Francisco, CA
- LinkedIn: linkedin.com/in/mrodriguez
- GitHub: github.com/mrodriguez
- Portfolio: mrodriguez.dev

## Executive Summary
Accomplished Principal Software Engineer with 12+ years of experience architecting and delivering enterprise-scale software solutions. Expert in distributed systems, cloud architecture, and technical leadership. Proven ability to drive innovation, mentor engineering teams, and align technology initiatives with business objectives.

## Professional Experience

### Principal Software Engineer - MegaTech Corporation (2020-Present)
- Architect and tech lead for company's core platform serving 50M+ users globally
- Designed distributed system handling 100K requests/second with 99.99% uptime
- Led migration from monolithic architecture to microservices, reducing deployment time by 75%
- Established engineering best practices and coding standards across 5 teams
- Drove adoption of event-driven architecture using Kafka and event sourcing
- Mentored 15+ engineers and conducted technical interviews
- Reduced infrastructure costs by $2M annually through optimization initiatives

### Staff Software Engineer - Innovation Labs Inc (2017-2020)
- Technical lead for real-time analytics platform processing 1TB+ data daily
- Implemented machine learning pipeline for predictive analytics using Python and TensorFlow
- Designed multi-region disaster recovery strategy with RPO < 1 minute
- Built custom Kubernetes operators for automated scaling and deployment
- Introduced chaos engineering practices to improve system reliability
- Published 3 technical blog posts and presented at 2 conferences

### Senior Software Engineer - CloudScale Systems (2014-2017)
- Developed high-throughput data processing system using Apache Spark
- Implemented authentication and authorization service handling 10M+ users
- Optimized database queries resulting in 60% performance improvement
- Led technical design reviews and architectural decision records
- Mentored junior and mid-level engineers

### Software Engineer - TechStartup Co (2011-2014)
- Full-stack development using Python/Django and Angular
- Implemented payment processing system integrating with Stripe
- Developed automated testing framework reducing QA time by 50%
- Participated in 24/7 on-call rotation

## Technical Expertise
- **Languages**: Python, Go, Java, JavaScript, TypeScript, Rust, C++
- **Frameworks**: Django, FastAPI, Spring Boot, React, Node.js
- **Databases**: PostgreSQL, Cassandra, MongoDB, Redis, Elasticsearch
- **Cloud Platforms**: AWS (Expert), GCP, Azure
- **Infrastructure**: Kubernetes, Docker, Terraform, Ansible, Helm
- **Data Processing**: Apache Spark, Kafka, Airflow, Flink
- **Monitoring**: Prometheus, Grafana, ELK Stack, Datadog
- **Architecture**: Microservices, Event-Driven, CQRS, Domain-Driven Design

## Leadership & Achievements
- Technical reviewer for O'Reilly Media (3 books)
- Open source contributor: 500+ GitHub stars on distributed caching library
- Speaker at PyCon 2022: "Scaling Python Services to Billions of Requests"
- Led company-wide Python 2 to 3 migration affecting 200+ services
- Established mentorship program that onboarded 30+ engineers

## Education
**MS Computer Science** - Stanford University (2011)
- Specialization: Distributed Systems
- Thesis: "Optimizing Consensus Algorithms for Geo-Distributed Systems"

**BS Computer Science** - UC Berkeley (2009)
- Graduated Summa Cum Laude
- ACM Programming Competition Winner (2008)

## Certifications & Training
- AWS Certified Solutions Architect - Professional (2021)
- Google Cloud Professional Cloud Architect (2020)
- Kubernetes Certified Administrator (CKA) (2019)
- Machine Learning Specialization - Coursera (2018)

## Publications & Patents
- "Efficient State Management in Distributed Systems" - IEEE Conference (2021)
- Patent: "Method for Dynamic Resource Allocation in Cloud Environments" (2020)
- "Building Resilient Microservices" - Tech Blog Series (2019)"""
        }
        
        return resumes.get(experience_level, resumes["mid"])
    
    @staticmethod
    def get_sample_job_description(job_type: str = "standard") -> str:
        """Get a sample job description."""
        job_descriptions = {
            "standard": """# Software Engineer - Cloud Platform Team

## About the Company
TechInnovate is a leading cloud infrastructure company providing cutting-edge solutions to Fortune 500 companies. We're building the next generation of cloud platforms that power critical business applications worldwide.

## Position Overview
We're seeking a talented Software Engineer to join our Cloud Platform team. You'll work on distributed systems that handle millions of requests per day, collaborating with a team of passionate engineers to solve complex technical challenges.

## Key Responsibilities
- Design and implement scalable backend services using Python and Go
- Build and maintain RESTful APIs and microservices
- Optimize database queries and improve system performance
- Participate in code reviews and technical design discussions
- Collaborate with cross-functional teams to deliver features
- Monitor and troubleshoot production systems
- Contribute to technical documentation and best practices

## Required Qualifications
- 3-5 years of software development experience
- Strong proficiency in Python and at least one other language (Go, Java, or Node.js)
- Experience with relational databases (PostgreSQL, MySQL)
- Solid understanding of data structures and algorithms
- Experience with version control systems (Git)
- Excellent problem-solving and communication skills
- Bachelor's degree in Computer Science or related field

## Preferred Qualifications
- Experience with cloud platforms (AWS, GCP, or Azure)
- Knowledge of containerization (Docker, Kubernetes)
- Familiarity with message queuing systems (Kafka, RabbitMQ)
- Experience with NoSQL databases (MongoDB, Redis)
- Understanding of CI/CD pipelines and DevOps practices
- Contributions to open-source projects

## What We Offer
- Competitive salary and equity packages
- Comprehensive health, dental, and vision insurance
- Flexible work arrangements and unlimited PTO
- Professional development budget
- State-of-the-art equipment and tools
- Collaborative and inclusive work environment""",

            "senior": """# Senior/Staff Software Engineer - Platform Architecture

## About Us
GlobalTech Systems is transforming how enterprises manage their digital infrastructure. Our platform processes billions of transactions daily and serves customers in over 100 countries. We're looking for exceptional engineers to help us scale to the next level.

## The Role
As a Senior/Staff Software Engineer on our Platform Architecture team, you'll be responsible for designing and implementing core infrastructure that powers our entire product suite. This is a high-impact role where you'll shape the technical direction of our platform.

## What You'll Do
- Architect distributed systems handling extreme scale (100K+ RPS)
- Lead technical initiatives spanning multiple engineering teams
- Design APIs and data models for platform services
- Implement high-performance services in Python, Go, or Java
- Establish engineering best practices and coding standards
- Mentor engineers and promote technical excellence
- Collaborate with product management on technical strategy
- Drive adoption of new technologies and methodologies
- Participate in incident response and on-call rotation

## What We're Looking For

### Must-Have Qualifications
- 7+ years of backend software development experience
- Expert-level proficiency in at least two of: Python, Go, Java, or C++
- Deep experience with distributed systems and microservices
- Strong knowledge of database systems (SQL and NoSQL)
- Experience with cloud platforms (AWS preferred)
- Track record of designing scalable, reliable systems
- Excellent communication and leadership skills
- BS/MS in Computer Science or equivalent experience

### Nice-to-Have Qualifications
- Experience with Kubernetes and container orchestration
- Knowledge of streaming systems (Kafka, Kinesis)
- Familiarity with observability tools (Prometheus, Grafana, ELK)
- Experience with Infrastructure as Code (Terraform, CloudFormation)
- Background in security best practices
- Open source contributions or technical publications
- Experience in high-growth startup environments

## Technical Environment
- Languages: Python, Go, Java, TypeScript
- Infrastructure: AWS, Kubernetes, Docker, Terraform
- Databases: PostgreSQL, DynamoDB, Redis, Elasticsearch
- Data Pipeline: Kafka, Spark, Airflow
- Monitoring: Datadog, PagerDuty, Sentry
- CI/CD: GitHub Actions, ArgoCD

## Why Join Us
- Work on challenging problems at massive scale
- Competitive compensation: $180K-$280K + equity
- Comprehensive benefits and wellness programs
- Annual learning budget and conference attendance
- Flexible remote work options
- Opportunity to mentor and grow with the team
- Direct impact on product used by millions""",

            "ai_ml": """# Machine Learning Engineer - AI Products Team

## Company Overview
AI Innovations Corp is at the forefront of artificial intelligence, developing cutting-edge solutions that transform how businesses operate. Our AI-powered products serve millions of users across healthcare, finance, and e-commerce sectors.

## Position Summary
We're looking for a talented Machine Learning Engineer to join our AI Products team. You'll work on state-of-the-art ML systems, from research to production deployment, solving real-world problems with advanced AI techniques.

## Responsibilities
- Design and implement machine learning models for production systems
- Build end-to-end ML pipelines from data ingestion to model serving
- Optimize model performance and reduce inference latency
- Collaborate with data scientists on model development
- Implement A/B testing frameworks for model evaluation
- Deploy models using MLOps best practices
- Monitor model performance and implement retraining pipelines
- Research and apply latest ML techniques to product features

## Required Qualifications
- 3+ years of experience in machine learning engineering
- Strong programming skills in Python and ML frameworks (TensorFlow, PyTorch, scikit-learn)
- Experience deploying ML models to production
- Solid understanding of ML algorithms and statistical concepts
- Experience with data processing tools (Pandas, NumPy, Spark)
- Familiarity with cloud platforms and containerization
- Strong software engineering practices (testing, version control, CI/CD)
- BS/MS in Computer Science, Machine Learning, or related field

## Preferred Qualifications
- Experience with deep learning and neural networks
- Knowledge of MLOps tools (MLflow, Kubeflow, SageMaker)
- Experience with real-time model serving (TensorFlow Serving, TorchServe)
- Background in specific domains (NLP, Computer Vision, RecSys)
- Experience with distributed training frameworks
- Publications or contributions to ML research
- Experience with edge deployment and model optimization

## Tech Stack
- ML Frameworks: TensorFlow, PyTorch, JAX
- Languages: Python, C++, Go
- Data Tools: Spark, Airflow, Kafka
- MLOps: MLflow, Weights & Biases, DVC
- Cloud: AWS SageMaker, GCP Vertex AI
- Infrastructure: Kubernetes, Docker, CUDA

## What We Offer
- Work on cutting-edge AI projects
- Access to GPU clusters and latest hardware
- Collaboration with top ML researchers
- Competitive salary and equity
- Conference attendance and paper publication support
- Flexible work arrangements""",

            "minimal": """# Python Developer Needed

We need a Python developer with 3+ years of experience.

Key requirements:
- Strong Python skills
- API development experience
- Database knowledge
- Team player

Send your resume to: hiring@company.com"""
        }
        
        return job_descriptions.get(job_type, job_descriptions["standard"])
    
    @staticmethod
    def get_edge_case_resume(case_type: str) -> str:
        """Get edge case resumes for testing."""
        edge_cases = {
            "minimal": "# Jane Doe\nSoftware Developer",
            
            "no_experience": """# Recent Graduate

## Education
BS Computer Science - State University (2024)

## Skills
Python, Java, JavaScript""",
            
            "career_change": """# Pat Smith

## Summary
Former teacher transitioning to software development after completing bootcamp.

## Experience
### High School Math Teacher (2015-2023)
- Taught algebra and calculus
- Developed curriculum

## Education
### Software Development Bootcamp (2023)
- Full-stack web development
- Built 5 projects

### BA Mathematics (2015)

## Skills
- JavaScript, React, Node.js
- Problem solving
- Communication""",
            
            "overqualified": """# Dr. Expert McExpert, PhD

## Summary
30 years of experience. Published 50 papers. Founded 3 companies. Know 20 programming languages.

## Experience
[Lists 15 different senior positions]

## Education
- PhD Computer Science - MIT
- MS Computer Science - Stanford  
- BS Computer Science - Harvard

## Skills
[Lists every technology ever invented]"""
        }
        
        return edge_cases.get(case_type, edge_cases["minimal"])


@pytest.fixture
def test_data_manager():
    """Provides test data manager instance."""
    return TestDataFixtures()


@pytest.fixture
def temp_test_environment():
    """Creates a complete test environment with multiple files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        
        # Create directory structure
        (base_path / "resumes").mkdir()
        (base_path / "jobs").mkdir()
        (base_path / "output").mkdir()
        
        # Create test files
        files = {
            "resumes": {
                "mid_level.md": TestDataFixtures.get_sample_resume("mid"),
                "entry_level.md": TestDataFixtures.get_sample_resume("entry"),
                "senior_level.md": TestDataFixtures.get_sample_resume("senior"),
                "minimal.md": TestDataFixtures.get_edge_case_resume("minimal"),
                "career_change.md": TestDataFixtures.get_edge_case_resume("career_change")
            },
            "jobs": {
                "standard_swe.md": TestDataFixtures.get_sample_job_description("standard"),
                "senior_role.md": TestDataFixtures.get_sample_job_description("senior"),
                "ai_ml_role.md": TestDataFixtures.get_sample_job_description("ai_ml"),
                "minimal_posting.md": TestDataFixtures.get_sample_job_description("minimal")
            }
        }
        
        # Write all files
        created_files = {}
        for category, file_dict in files.items():
            created_files[category] = {}
            for filename, content in file_dict.items():
                file_path = base_path / category / filename
                file_path.write_text(content, encoding='utf-8')
                created_files[category][filename] = str(file_path)
        
        # Add paths to output
        created_files["output_dir"] = str(base_path / "output")
        created_files["base_path"] = str(base_path)
        
        yield created_files


@pytest.fixture
def performance_tracker():
    """Tracks performance metrics during tests."""
    class PerformanceTracker:
        def __init__(self):
            self.metrics = {
                "start_time": None,
                "end_time": None,
                "api_calls": 0,
                "total_tokens": 0,
                "file_operations": {
                    "reads": 0,
                    "writes": 0
                },
                "memory_usage": []
            }
        
        def start(self):
            self.metrics["start_time"] = datetime.now()
        
        def stop(self):
            self.metrics["end_time"] = datetime.now()
        
        def add_api_call(self, tokens: int = 0):
            self.metrics["api_calls"] += 1
            self.metrics["total_tokens"] += tokens
        
        def add_file_operation(self, operation: str):
            if operation in self.metrics["file_operations"]:
                self.metrics["file_operations"][operation] += 1
        
        def get_duration(self) -> float:
            if self.metrics["start_time"] and self.metrics["end_time"]:
                delta = self.metrics["end_time"] - self.metrics["start_time"]
                return delta.total_seconds()
            return 0.0
        
        def get_summary(self) -> Dict[str, Any]:
            return {
                "duration_seconds": self.get_duration(),
                "api_calls": self.metrics["api_calls"],
                "total_tokens": self.metrics["total_tokens"],
                "file_reads": self.metrics["file_operations"]["reads"],
                "file_writes": self.metrics["file_operations"]["writes"]
            }
    
    return PerformanceTracker()


@pytest.fixture
def quality_validator():
    """Provides methods to validate resume quality."""
    class QualityValidator:
        @staticmethod
        def check_ats_compliance(content: str) -> Dict[str, bool]:
            """Check if resume is ATS-compliant."""
            checks = {
                "has_contact_section": any(
                    section in content.lower() 
                    for section in ["contact", "email", "phone"]
                ),
                "has_experience_section": any(
                    section in content.lower() 
                    for section in ["experience", "work history", "employment"]
                ),
                "has_skills_section": "skills" in content.lower(),
                "has_education_section": "education" in content.lower(),
                "no_tables": "<table" not in content.lower(),
                "no_images": not any(
                    img in content.lower() 
                    for img in ["<img", "![", ".png", ".jpg", ".jpeg"]
                ),
                "proper_headings": content.count("#") >= 3
            }
            return checks
        
        @staticmethod
        def check_keyword_integration(
            original: str, 
            customized: str, 
            job_keywords: list
        ) -> Dict[str, Any]:
            """Check how well keywords are integrated."""
            original_lower = original.lower()
            customized_lower = customized.lower()
            
            results = {
                "keywords_found": [],
                "keywords_added": [],
                "integration_score": 0.0
            }
            
            for keyword in job_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in customized_lower:
                    results["keywords_found"].append(keyword)
                    if keyword_lower not in original_lower:
                        results["keywords_added"].append(keyword)
            
            if job_keywords:
                results["integration_score"] = len(results["keywords_found"]) / len(job_keywords)
            
            return results
        
        @staticmethod
        def check_content_preservation(original: str, customized: str) -> Dict[str, bool]:
            """Ensure important content is preserved."""
            # Extract key information from original
            checks = {}
            
            # Check name preservation (assumes first # heading is name)
            import re
            name_match = re.search(r'^#\s+(.+)$', original, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                checks["name_preserved"] = name in customized
            
            # Check contact info preservation
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', original)
            if email_match:
                email = email_match.group(0)
                checks["email_preserved"] = email in customized
            
            # Check if major sections are preserved
            for section in ["experience", "education", "skills"]:
                if section in original.lower():
                    checks[f"{section}_section_preserved"] = section in customized.lower()
            
            return checks
        
        @staticmethod
        def calculate_quality_score(
            ats_checks: Dict[str, bool],
            keyword_results: Dict[str, Any],
            preservation_checks: Dict[str, bool]
        ) -> float:
            """Calculate overall quality score (0-100)."""
            # ATS compliance (40% weight)
            ats_score = sum(ats_checks.values()) / len(ats_checks) * 40
            
            # Keyword integration (40% weight)
            keyword_score = keyword_results.get("integration_score", 0) * 40
            
            # Content preservation (20% weight)
            if preservation_checks:
                preservation_score = sum(preservation_checks.values()) / len(preservation_checks) * 20
            else:
                preservation_score = 20
            
            return ats_score + keyword_score + preservation_score
    
    return QualityValidator()