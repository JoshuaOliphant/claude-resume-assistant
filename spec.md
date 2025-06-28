# Resume Customizer Application Specification

## Executive Summary

An automated resume customization tool that uses the Claude Code SDK to tailor resumes for specific job applications, saving job seekers significant time while maintaining truthfulness and quality.

## Problem Statement

Job seekers spend excessive time customizing resumes for each application, including:
- Rewriting job descriptions to match keywords
- Reorganizing sections to highlight relevant experience
- Adjusting summaries and objectives
- Ensuring ATS compliance

Manual customization for multiple applications is tedious and time-consuming.

## Solution Overview

An AI-powered application that:
1. Accepts a resume and job description as input
2. Analyzes job requirements and resume content
3. Automatically customizes the resume while maintaining truthfulness
4. Outputs an optimized resume tailored to the specific position

## Technical Architecture

### Core Technology
- **Language**: Python
- **AI SDK**: Claude Code SDK
- **Architecture Pattern**: Orchestrator-Workers with Evaluator-Optimizer

### Development Phases

#### Phase 1: CLI Application
- Click-based command-line interface
- Core customization logic
- Markdown input/output support

#### Phase 2: Web Application
- **Backend**: FastAPI
- **Frontend**: HTMX + Tailwind CSS + Alpine.js + DaisyUI
- RESTful API design
- Real-time customization feedback

## Detailed Requirements

### Input Specifications

#### Resume Input
- **Phase 1**: Markdown files (.md)
- **Phase 2**: Microsoft Word documents (.docx)
- **Format**: Must preserve original formatting and styling
- **Structure**: Auto-detect sections (Experience, Skills, Education, etc.)

#### Job Description Input
- **Phase 1**: Plain text (copied from job postings)
- **Phase 2**: URL input with Jina API scraping
- **Phase 3**: Browserbase integration for restricted sites (e.g., LinkedIn)

### Processing Logic

#### AI Prompt Strategy
The Claude Code prompt implements an orchestrator that creates virtual sub-agents:

1. **Requirement Extractor**: Identifies key job requirements
2. **Gap Analyzer**: Finds missing skills or experiences
3. **Content Optimizer**: Rewrites sections for impact
4. **ATS Checker**: Ensures formatting compliance
5. **Keyword Optimizer**: Natural keyword integration

#### Customization Rules
- **Truthfulness**: Never fabricate information
- **Keyword Optimization**: Use synonymous terms (e.g., "managed" → "led")
- **Section Reordering**: Emphasize relevant experience
- **Content Reframing**: Highlight matching skills without adding false claims

#### Iteration Configuration
- Fixed number of refinement iterations
- Configurable via Pydantic settings
- Environment variable override support
- Embedded evaluator-optimizer pattern in prompts

### Output Specifications

#### Phase 1
- Markdown format matching input structure
- Preserved formatting and styling
- Clear indication of changes made

#### Phase 2
- PDF export capability
- Change tracking/summary
- Multiple format options

### Error Handling

1. **Parse Failures**: Graceful degradation with helpful error messages
2. **Missing Sections**: Best-effort customization with warnings
3. **API Failures**: Retry logic with exponential backoff
4. **Invalid Input**: Clear validation messages

## CLI Application Design

### Command Structure
```bash
# Basic usage
python resume_customizer.py -r resume.md -j job_description.txt

# With custom iterations
python resume_customizer.py -r resume.md -j job_description.txt --iterations 5

# With URL input (Phase 2)
python resume_customizer.py -r resume.md -j https://example.com/job-posting

# Verbose mode
python resume_customizer.py -r resume.md -j job.txt --verbose
```

### Configuration
```python
# settings.py using Pydantic
class Settings(BaseSettings):
    max_iterations: int = 3
    claude_api_key: str
    output_format: str = "markdown"
    preserve_formatting: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "RESUME_"
```

### Core Classes
```python
class ResumeCustomizer:
    """Main orchestration logic"""
    
class ResumeSummarizer:
    """Analyzes and summarizes changes"""
    
class FormatPreserver:
    """Maintains original formatting"""
    
class ATSOptimizer:
    """Ensures ATS compliance"""
```

## Web Application Design

### API Endpoints

```
POST /api/customize
  Body: {
    "resume": "markdown content or file",
    "job_description": "text or URL",
    "options": {
      "iterations": 3,
      "preserve_formatting": true
    }
  }
  Response: {
    "customized_resume": "markdown content",
    "changes_summary": "list of changes",
    "ats_score": 85
  }

GET /api/status/{job_id}
  Response: {
    "status": "processing|completed|failed",
    "progress": 75,
    "message": "Analyzing keywords..."
  }

POST /api/export/{job_id}
  Body: { "format": "pdf|docx|markdown" }
  Response: Binary file download
```

### Frontend Components

1. **Upload Section**
   - Drag-and-drop for resume files
   - Text area for job descriptions
   - URL input with validation

2. **Customization Options**
   - Iteration slider
   - ATS optimization toggle
   - Format preservation checkbox

3. **Progress Display**
   - Real-time status updates via HTMX
   - Step-by-step progress indicators
   - Animated processing feedback

4. **Results Section**
   - Side-by-side comparison
   - Highlighted changes
   - Download buttons for various formats

### UI/UX Flow
1. User uploads resume (drag-and-drop or file picker)
2. User inputs job description (paste text or enter URL)
3. Optional: Configure settings
4. Click "Customize Resume"
5. View real-time progress
6. Review customized result with changes highlighted
7. Download in preferred format

## Security Considerations

1. **Data Privacy**
   - No permanent storage of resumes
   - Session-based temporary files
   - Automatic cleanup after processing

2. **API Security**
   - Rate limiting per IP/session
   - Input validation and sanitization
   - CORS configuration for web app

3. **Authentication (Future)**
   - Optional user accounts
   - Saved resume templates
   - Customization history

## Performance Requirements

- Resume processing: < 30 seconds average
- API response time: < 200ms for status checks
- Concurrent users: Support 100+ simultaneous customizations
- File size limits: 10MB for resume uploads

## Testing Strategy

1. **Unit Tests**
   - Prompt generation logic
   - Format preservation
   - Error handling

2. **Integration Tests**
   - Claude Code SDK integration
   - File parsing and generation
   - API endpoint functionality

3. **E2E Tests**
   - Full customization workflow
   - Various resume formats
   - Error scenarios

## Deployment

### Phase 1 (CLI)
- Python package distribution
- Docker container option
- Installation via pip/uv

### Phase 2 (Web)
- Docker Compose setup
- Cloud deployment (AWS/GCP/Azure)
- CDN for static assets
- Redis for job queue management

## Future Enhancements

1. **Batch Processing**: Multiple job applications at once
2. **Resume Templates**: Industry-specific formats
3. **Skills Gap Analysis**: Detailed reports on missing qualifications
4. **A/B Testing**: Compare customization effectiveness
5. **Learning System**: Improve based on successful applications
6. **Browser Extension**: Direct integration with job sites
7. **Mobile App**: iOS/Android versions
8. **Multi-language Support**: Resumes in different languages
9. **Industry Insights**: Trending keywords and skills
10. **Interview Prep**: Generate likely interview questions

## Success Metrics

1. **Time Saved**: Average 20-30 minutes per application
2. **Customization Quality**: 90%+ user satisfaction
3. **ATS Pass Rate**: 85%+ success rate
4. **User Adoption**: 1000+ active users in 6 months
5. **Processing Speed**: < 30 seconds per resume

## Development Timeline

### Phase 1: CLI Application (2 weeks)
- Week 1: Core logic and Claude integration
- Week 2: CLI interface and testing

### Phase 2: Web Application (4 weeks)
- Week 1: FastAPI backend setup
- Week 2: Frontend development
- Week 3: Integration and testing
- Week 4: Deployment and documentation

### Phase 3: Advanced Features (Ongoing)
- URL scraping integration
- PDF/Word support
- Batch processing
- Analytics dashboard

## Conclusion

This specification outlines a comprehensive solution for automated resume customization that balances sophistication with simplicity. By starting with a CLI application and progressively adding features, we ensure a solid foundation while delivering value quickly to users.

The use of Claude Code SDK with an orchestrator-workers pattern provides the flexibility and intelligence needed for high-quality customization while maintaining the critical constraint of truthfulness. The modular architecture supports future enhancements and scaling as user needs evolve.