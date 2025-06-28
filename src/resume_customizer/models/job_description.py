# ABOUTME: Domain model for job description representation and parsing
# ABOUTME: Handles text parsing, requirement extraction, and keyword detection

"""Job description domain model for parsing and analyzing job postings."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from resume_customizer.utils.logging import get_logger

logger = get_logger("models.job_description")


@dataclass
class JobDescription:
    """Domain model representing a parsed job description."""
    title: str
    company: str
    raw_content: str = ""
    required_skills: List[str] = field(default_factory=list)
    nice_to_have_skills: List[str] = field(default_factory=list)
    years_of_experience: int = 0
    responsibilities: List[str] = field(default_factory=list)
    qualifications: List[str] = field(default_factory=list)
    keywords: Set[str] = field(default_factory=set)
    
    # Common skill normalizations
    SKILL_NORMALIZATIONS = {
        "js": "JavaScript",
        "ts": "TypeScript", 
        "py": "Python",
        "node": "Node.js",
        "react.js": "React",
        "vue.js": "Vue",
        "postgres": "PostgreSQL",
        "mongo": "MongoDB",
        "k8s": "Kubernetes",
        "ml": "ML",
        "ai": "Artificial Intelligence",
        "ci/cd": "CI/CD",
        "tdd": "Test-Driven Development",
    }
    
    @classmethod
    def from_text(cls, text: str) -> "JobDescription":
        """
        Parse a job description from text content.
        
        Args:
            text: The raw job description text
            
        Returns:
            JobDescription instance with parsed data
            
        Raises:
            ValueError: If text is empty or invalid
        """
        if not text or not text.strip():
            raise ValueError("Empty or invalid job description")
        
        logger.debug("Parsing job description from text")
        
        # Extract basic info
        title = cls._extract_title(text)
        company = cls._extract_company(text)
        years_exp = cls._extract_years_of_experience(text)
        
        # Extract skills
        required_skills = cls._extract_required_skills(text)
        nice_to_have_skills = cls._extract_nice_to_have_skills(text)
        
        # Extract other information
        responsibilities = cls._extract_responsibilities(text)
        qualifications = cls._extract_qualifications(text)
        
        # Create job description instance
        job = cls(
            title=title,
            company=company,
            raw_content=text,
            required_skills=required_skills,
            nice_to_have_skills=nice_to_have_skills,
            years_of_experience=years_exp,
            responsibilities=responsibilities,
            qualifications=qualifications
        )
        
        # Extract keywords for ATS
        job.keywords = job._extract_keywords()
        
        return job
    
    @staticmethod
    def _extract_title(text: str) -> str:
        """Extract job title from text."""
        lines = text.strip().split('\n')
        
        # Common patterns for job title
        title_patterns = [
            r'^Job Title:\s*(.+)$',
            r'^Position:\s*(.+)$',
            r'^Role:\s*(.+)$',
            r'^Title:\s*(.+)$',
        ]
        
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            # Check explicit patterns
            for pattern in title_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            
            # Check for "at/for Company" pattern
            if ' at ' in line or ' for ' in line:
                title = re.split(r'\s+(?:at|for)\s+', line)[0].strip()
                if title and not any(char.isdigit() for char in title):
                    return title
            
            # Special case for "We're hiring [title]" pattern
            hiring_match = re.search(r"(?:We're|We are)\s+(?:hiring|looking for|seeking)\s+(?:a|an)?\s*([^!.]+?)(?:\s+to\s+|\s+at\s+|!|\.|$)", line, re.IGNORECASE)
            if hiring_match:
                title = hiring_match.group(1).strip()
                # Clean up the title - remove trailing phrases
                title = re.sub(r'\s+to\s+join.*$', '', title, flags=re.IGNORECASE)
                if title:
                    return title
            
            # First non-empty line that looks like a title
            if (line and len(line) < 100 and 
                not any(word in line.lower() for word in ['about', 'location', 'description']) and
                not ':' in line):
                # If it contains "we're hiring" etc, it's handled above
                if any(phrase in line.lower() for phrase in ["we're hiring", "we are hiring", "looking for", "seeking"]):
                    continue
                # Extract just the title part if it says "position available" etc
                position_match = re.search(r'^(.+?)\s+(?:position|role|opportunity)\s*(?:available|open)?', line, re.IGNORECASE)
                if position_match:
                    return position_match.group(1).strip()
                # Likely a title if it's short and doesn't contain pronouns/common words
                if not line.endswith('.') and not line.endswith('!'):
                    return line.split('\n')[0].strip()
        
        return "Unknown"
    
    @staticmethod
    def _extract_company(text: str) -> str:
        """Extract company name from text."""
        lines = text.strip().split('\n')
        
        # Patterns for company extraction
        patterns = [
            r'^Company:\s*(.+?)$',
            r'^Employer:\s*(.+?)$',
            r'^Organization:\s*(.+?)$',
            r'\bat\s+([A-Z][A-Za-z0-9\s&.-]+?)(?:\s*[!,.]|\s*$)',
            r'\bfor\s+([A-Z][A-Za-z0-9\s&.-]+?)(?:\s*[!,.]|\s*$)',
            r'(?:join|joining)\s+(?:our\s+)?(?:team\s+at\s+)?([A-Z][A-Za-z0-9\s&.-]+?)(?:[!,.]|$)',
        ]
        
        # First check if company is on second or third line (common pattern)
        for i in range(1, min(4, len(lines))):
            line = lines[i].strip()
            if line and len(line) < 50 and not any(word in line.lower() for word in ['about', 'location', 'we', 'our']):
                # Could be company name if it's short and doesn't have common words
                if not line.endswith('.') and ':' not in line and not ',' in line:
                    return line
        
        # Then check patterns
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                company = match.group(1).strip()
                # Clean up company name
                company = re.sub(r'\s*[-–]\s*$', '', company)
                company = company.strip('.,;!')
                # Remove trailing "to join" type phrases
                company = re.sub(r'\s+(?:to|who|that)\s+.*$', '', company)
                return company
        
        return "Unknown"
    
    @staticmethod
    def _extract_years_of_experience(text: str) -> int:
        """Extract required years of experience."""
        # Patterns for years of experience (order matters!)
        patterns = [
            # Range patterns first (more specific)
            r'(\d+)\s*(?:-|to)\s*\d+\s*years?\s*.*?(?:experience|expertise)',
            # Standard patterns
            r'(\d+)\+?\s*(?:to\s*\d+\s*)?years?\s*(?:of\s*)?(?:experience|expertise)',
            r'(?:minimum|at\s*least|requires?)\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*(?:minimum|required)',
            r'(\d+)\+?\s*years?\s+(?:of\s+)?[\w\s]+\s+experience',  # "5 years Python experience"
        ]
        
        all_years = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Extract years from matches
                for match in matches:
                    if isinstance(match, str):
                        all_years.append(int(match))
                    elif isinstance(match, tuple):
                        # For range patterns like "3-5 years", take the first (minimum) value
                        all_years.append(int(match[0]))
        
        # Return the minimum years found (most lenient requirement)
        return min(all_years) if all_years else 0
    
    @classmethod
    def _extract_required_skills(cls, text: str) -> List[str]:
        """Extract required skills from job description."""
        skills = []
        
        # Define section headers for required skills
        required_headers = [
            r'Required\s*(?:Skills?|Qualifications?)?:?',
            r'Requirements?:?',
            r'Must\s*(?:Have|Haves?)?:?',
            r'Essential\s*(?:Skills?|Qualifications?)?:?',
            r'Mandatory\s*(?:Skills?|Requirements?)?:?',
            r'Should\s*have:?',  # Sometimes "should have" is also required
        ]
        
        # Find required skills sections
        for header_pattern in required_headers:
            pattern = rf'{header_pattern}\s*\n((?:[-•*]\s*[^\n]+\n?)+)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                skills.extend(cls._parse_skill_list(match))
        
        # Also look for inline requirements
        inline_patterns = [
            r'(?:strong|solid|extensive|expert)\s+(?:knowledge|experience|proficiency)\s+(?:in|with|of)\s+([A-Za-z0-9\s,/.-]+)',
            r'(?:experience|proficiency|expertise)\s+(?:with|in)\s+([A-Za-z0-9\s,/.-]+)\s+(?:required|is\s+required)',
        ]
        
        for pattern in inline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                skills.extend(cls._parse_skill_list(match))
        
        # Normalize and deduplicate
        normalized_skills = []
        seen = set()
        for skill in skills:
            normalized = cls._normalize_skill(skill)
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                normalized_skills.append(normalized)
        
        return normalized_skills
    
    @classmethod
    def _extract_nice_to_have_skills(cls, text: str) -> List[str]:
        """Extract nice-to-have skills from job description."""
        skills = []
        
        # Define section headers for nice-to-have skills
        nice_headers = [
            r'Nice\s*to\s*(?:Have|Haves?)?:?',
            r'Preferred\s*(?:Skills?|Qualifications?)?:?',
            r'Bonus\s*(?:Skills?|Points?)?:?',
            r'(?:Would\s*be\s*)?(?:a\s*)?Plus:?',
            r'Desirable\s*(?:Skills?)?:?',
            r'(?:Good|Great)\s*to\s*Have:?',
            r'Good\s*to\s*have:?',  # Handle case variations
        ]
        
        # Find nice-to-have sections
        for header_pattern in nice_headers:
            pattern = rf'{header_pattern}\s*\n((?:[-•*]\s*[^\n]+\n?)+)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                skills.extend(cls._parse_skill_list(match))
        
        # Look for inline nice-to-have mentions
        inline_patterns = [
            r'([A-Za-z0-9\s,/.-]+?)\s+(?:would\s+be|is)\s+(?:a\s+)?(?:plus|bonus|advantage)',
            r'(?:experience\s+with|knowledge\s+of)\s+([A-Za-z0-9\s,/.-]+?)\s+(?:is\s+)?(?:preferred|desired)',
        ]
        
        for pattern in inline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                skills.extend(cls._parse_skill_list(match))
        
        # Normalize and deduplicate
        normalized_skills = []
        seen = set()
        for skill in skills:
            normalized = cls._normalize_skill(skill)
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                normalized_skills.append(normalized)
        
        return normalized_skills
    
    @classmethod
    def _extract_responsibilities(cls, text: str) -> List[str]:
        """Extract job responsibilities."""
        responsibilities = []
        
        # Section headers for responsibilities
        headers = [
            r'Responsibilities?:?',
            r'(?:Key\s+)?Duties:?',
            r'What\s+you[\'\']?ll\s+do:?',
            r'You\s+will:?',
            r'Role\s+(?:Responsibilities?|Overview):?',
        ]
        
        # Find responsibility sections
        for header_pattern in headers:
            pattern = rf'{header_pattern}\s*\n((?:[-•*]\s*[^\n]+\n?)+)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                lines = match.strip().split('\n')
                for line in lines:
                    cleaned = re.sub(r'^[-•*]\s*', '', line).strip()
                    if cleaned and len(cleaned) > 10:
                        responsibilities.append(cleaned)
        
        # Look for action verbs that indicate responsibilities
        action_patterns = [
            r'(?:will\s+)?(?:be\s+)?(?:responsible\s+for|expected\s+to)\s+([^.]+)',
            r'(?:Day\s+to\s+day|Daily),?\s*(?:you[\'\']?ll\s+)?(.+?)(?:\.|$)',
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                cleaned = match.strip()
                if cleaned and len(cleaned) > 10:
                    responsibilities.append(cleaned)
        
        return responsibilities
    
    @classmethod
    def _extract_qualifications(cls, text: str) -> List[str]:
        """Extract qualifications and education requirements."""
        qualifications = []
        
        # Section headers
        headers = [
            r'Qualifications?:?',
            r'Education\s*(?:Requirements?)?:?',
            r'(?:Minimum\s+)?Requirements?:?',
            r'Required\s+Education:?',
        ]
        
        # Find qualification sections
        for header_pattern in headers:
            pattern = rf'{header_pattern}\s*\n((?:[-•*]\s*[^\n]+\n?)+)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                lines = match.strip().split('\n')
                for line in lines:
                    cleaned = re.sub(r'^[-•*]\s*', '', line).strip()
                    if cleaned:
                        # Check if it's actually a qualification
                        if any(word in cleaned.lower() for word in 
                              ['degree', 'bachelor', 'master', 'phd', 'education', 
                               'certification', 'diploma', 'years']):
                            qualifications.append(cleaned)
                        # Note: We don't add non-qualification items to responsibilities here
        
        # Look for degree mentions inline
        degree_patterns = [
            r'((?:Bachelor|Master|PhD|Doctoral)[\'\']?s?\s+(?:degree|Degree)\s+[^.]+)',
            r'((?:BS|BA|MS|MA|MBA|PhD)\s+in\s+[^.]+)',
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match not in qualifications:
                    qualifications.append(match.strip())
        
        return qualifications
    
    @staticmethod
    def _parse_skill_list(text: str) -> List[str]:
        """Parse skills from bullet points or comma-separated lists."""
        skills = []
        
        # Remove bullet points
        text = re.sub(r'^[-•*]\s*', '', text, flags=re.MULTILINE)
        
        # Split by common delimiters
        if ',' in text:
            # Comma-separated
            parts = text.split(',')
        elif '\n' in text:
            # Line-separated
            parts = text.split('\n')
        else:
            parts = [text]
        
        for part in parts:
            # Clean up
            skill = part.strip()
            skill = re.sub(r'\s+', ' ', skill)  # Normalize whitespace
            
            # Handle "X or Y" patterns
            if ' or ' in skill.lower():
                sub_skills = skill.split(' or ')
                skills.extend([s.strip() for s in sub_skills if s.strip()])
            elif ' and ' in skill.lower() and len(skill) < 50:
                # Short "X and Y" might be separate skills
                sub_skills = skill.split(' and ')
                skills.extend([s.strip() for s in sub_skills if s.strip()])
            elif skill:
                skills.append(skill)
        
        return skills
    
    @classmethod
    def _normalize_skill(cls, skill: str) -> str:
        """Normalize skill name for consistency."""
        # Remove extra whitespace and punctuation
        skill = skill.strip().strip('.,;:')
        skill = re.sub(r'\s+', ' ', skill)
        
        # Remove common suffixes
        skill = re.sub(r'\s*(?:experience|knowledge|skills?|expertise|proficiency)$', '', skill, flags=re.IGNORECASE)
        
        # Apply known normalizations
        lower_skill = skill.lower()
        for variant, normalized in cls.SKILL_NORMALIZATIONS.items():
            if lower_skill == variant:
                return normalized
        
        # Handle variations like "Python programming" -> "Python"
        programming_langs = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust']
        for lang in programming_langs:
            if lower_skill.startswith(lang + ' '):
                # Extract just the language name
                skill = lang
                lower_skill = lang
        
        # Capitalize appropriately
        # Known all-caps terms
        all_caps = {'sql', 'html', 'css', 'xml', 'json', 'api', 'rest', 'aws', 'gcp', 'ci/cd', 'tdd', 'bdd'}
        if lower_skill in all_caps:
            return skill.upper()
        
        # Known mixed-case terms
        mixed_case = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript', 
            'python': 'Python',
            'java': 'Java',
            'c#': 'C#',
            'c++': 'C++',
            'node.js': 'Node.js',
            'vue.js': 'Vue.js',
            'angular.js': 'Angular.js',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'graphql': 'GraphQL',
            'django': 'Django',
            'flask': 'Flask',
            'react': 'React',
            'react.js': 'React',
            'kubernetes': 'Kubernetes',
            'docker': 'Docker',
            'git': 'Git',
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'linux': 'Linux',
            'macos': 'macOS',
            'redis': 'Redis',
            'elasticsearch': 'Elasticsearch',
            'machine learning': 'Machine Learning',
            'aws certification': 'AWS',
            'graphql knowledge': 'GraphQL',
            'docker containerization': 'Docker',
            'rest api development': 'REST API',
            'linux/unix proficiency': 'Linux/Unix',
            'ml background': 'ML',
            'mobile development': 'Mobile Development',
        }
        
        # First check exact match
        if lower_skill in mixed_case:
            return mixed_case[lower_skill]
        
        # Then check if skill contains known terms
        for key, value in mixed_case.items():
            if key in lower_skill:
                # Replace the known term with its normalized version
                return value
        
        # Default: capitalize first letter of each word
        return ' '.join(word.capitalize() for word in skill.split())
    
    def _extract_keywords(self) -> Set[str]:
        """Extract ATS keywords from the job description."""
        keywords = set()
        
        # Extract from all text content
        text = self.raw_content.lower()
        
        # Technical terms and skills
        technical_patterns = [
            r'\b(?:python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|php|swift|kotlin)\b',
            r'\b(?:react|angular|vue|django|flask|spring|rails|express|fastapi)\b',
            r'\b(?:sql|nosql|postgresql|mysql|mongodb|redis|elasticsearch)\b',
            r'\b(?:aws|azure|gcp|cloud|serverless|lambda|kubernetes|docker)\b',
            r'\b(?:api|rest|restful|graphql|grpc|websocket|microservices)\b',
            r'\b(?:git|github|gitlab|bitbucket|ci/cd|jenkins|travis|circle)\b',
            r'\b(?:agile|scrum|kanban|waterfall|lean|devops)\b',
            r'\b(?:tdd|bdd|unit\s+test|integration\s+test|e2e|testing)\b',
            r'\b(?:machine\s+learning|ml|ai|artificial\s+intelligence|deep\s+learning|nlp)\b',
            r'\b(?:data\s+science|analytics|visualization|etl|data\s+pipeline)\b',
        ]
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update(match.lower() for match in matches)
        
        # Add skills as keywords
        for skill in self.required_skills + self.nice_to_have_skills:
            keywords.add(skill.lower())
            # Also add individual words from multi-word skills
            if len(skill.split()) > 1:
                keywords.update(word.lower() for word in skill.split() 
                              if len(word) > 2 and word.lower() not in {'and', 'the', 'for', 'with'})
        
        # Extract from responsibilities
        action_verbs = ['design', 'develop', 'implement', 'build', 'create', 'optimize', 
                       'lead', 'manage', 'architect', 'deploy', 'maintain', 'analyze']
        for resp in self.responsibilities:
            resp_lower = resp.lower()
            for verb in action_verbs:
                if verb in resp_lower:
                    keywords.add(verb)
        
        # Clean up keywords
        cleaned_keywords = set()
        for keyword in keywords:
            keyword = keyword.strip().lower()
            # Remove very short or very long keywords
            if 2 < len(keyword) < 30:
                cleaned_keywords.add(keyword)
        
        return cleaned_keywords
    
    def validate(self) -> List[str]:
        """
        Validate the job description has sufficient information.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check title
        if not self.title or self.title == "Unknown":
            errors.append("Missing or unclear job title")
        
        # Check company
        if not self.company or self.company == "Unknown":
            errors.append("Missing company name")
        
        # Check skills
        if not self.required_skills:
            errors.append("No required skills identified")
        
        # Check if we have enough information
        if not self.responsibilities and not self.qualifications:
            errors.append("No responsibilities or qualifications found")
        
        # Check for years of experience (optional, many jobs don't specify)
        # Only add this as a warning if other key info is missing
        if self.years_of_experience == 0 and len(errors) > 2:
            errors.append("Years of experience not specified")
        
        return errors