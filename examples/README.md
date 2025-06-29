# Example Files

This directory contains sample resumes and job descriptions to help you get started with the Resume Customizer.

## Available Examples

### Resumes

1. **resume.txt** - Mid-level full-stack software engineer with 6 years of experience
   - Good for: General software engineering roles
   - Industries: Tech, SaaS, Startups

2. **entry_level_resume.txt** - Recent computer science graduate
   - Good for: Entry-level positions, internships
   - Industries: Any tech company hiring new grads

3. **data_scientist_resume.txt** - Senior data scientist with PhD and 8 years experience
   - Good for: Data science, ML research roles
   - Industries: Tech, Healthcare, Finance

### Job Descriptions

1. **job_description.txt** - Senior Backend Engineer at a FinTech company
   - Focus: Payment processing, security, scalability
   - Required: Python, PostgreSQL, financial systems

2. **frontend_job.txt** - Senior Frontend Engineer at a SaaS company
   - Focus: React, TypeScript, performance optimization
   - Required: Modern JavaScript, accessibility, testing

3. **ml_engineer_job.txt** - Machine Learning Engineer at a healthcare AI company
   - Focus: Production ML, healthcare applications
   - Required: Python, ML frameworks, cloud deployment

## Usage Examples

### Basic Customization

Customize the mid-level resume for the FinTech backend role:
```bash
uv run python resume_customizer.py -r examples/resume.txt -j examples/job_description.txt
```

### Entry-Level to Frontend Role

Customize entry-level resume for frontend position:
```bash
uv run python resume_customizer.py \
    -r examples/entry_level_resume.txt \
    -j examples/frontend_job.txt \
    -o entry_level_frontend.md
```

### Data Scientist to ML Engineer

Transform data scientist resume for ML engineering role:
```bash
uv run python resume_customizer.py \
    -r examples/data_scientist_resume.txt \
    -j examples/ml_engineer_job.txt \
    --iterations 5 \
    --verbose
```

## Tips for Best Results

1. **Match Seniority Levels**: The tool works best when the resume and job are at similar experience levels

2. **Industry Alignment**: While the tool can adapt resumes across industries, better results come from related fields

3. **Use More Iterations**: For significant transitions (e.g., data scientist to ML engineer), use more iterations:
   ```bash
   --iterations 5
   ```

4. **Review and Refine**: The output is a great starting point, but always review and make final adjustments

## Creating Your Own Examples

When preparing your resume for customization:

1. **Use Clear Sections**: Include standard sections like:
   - Contact Information
   - Professional Summary
   - Work Experience
   - Education
   - Technical Skills
   - Projects (if applicable)

2. **Be Specific**: Include:
   - Quantifiable achievements
   - Specific technologies used
   - Clear job titles and companies
   - Dates for all positions

3. **Format Consistently**: Use consistent formatting for:
   - Bullet points
   - Date formats
   - Section headers

## Example Output

When you run the customizer, you'll see the resume transformed to:
- Emphasize relevant experience
- Include important keywords from the job description
- Reframe accomplishments to match the role
- Maintain truthfulness while optimizing presentation

## Need Help?

- Check the main [README](../README.md) for detailed usage instructions
- See [CONTRIBUTING](../CONTRIBUTING.md) if you'd like to add more examples
- Open an issue if you encounter any problems