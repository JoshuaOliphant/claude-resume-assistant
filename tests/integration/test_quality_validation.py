# ABOUTME: Integration tests for output quality validation and ATS compliance
# ABOUTME: Tests keyword integration, content preservation, and formatting standards

"""Integration tests for resume quality validation."""

import pytest
import os
from pathlib import Path
import re
from collections import Counter

from resume_customizer.core.customizer import ResumeCustomizer
from resume_customizer.config import Settings
from tests.integration.fixtures import test_data_manager, temp_test_environment, quality_validator


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping integration tests"
)
class TestQualityValidation:
    """Test quality of customized resumes."""
    
    @pytest.fixture
    def settings(self):
        """Create settings for quality tests."""
        return Settings(max_iterations=3)  # More iterations for quality
    
    @pytest.fixture
    def customizer(self, settings):
        """Create customizer instance."""
        return ResumeCustomizer(settings)
    
    @pytest.mark.asyncio
    async def test_ats_compliance(self, customizer, temp_test_environment, quality_validator):
        """Test that output resumes are ATS-compliant."""
        # Test multiple resume types
        test_cases = [
            ("mid_level.md", "standard_swe.md"),
            ("entry_level.md", "standard_swe.md"),
            ("senior_level.md", "senior_role.md")
        ]
        
        for resume_file, job_file in test_cases:
            output_path = Path(temp_test_environment["output_dir"]) / f"ats_test_{resume_file}"
            
            await customizer.customize(
                resume_path=temp_test_environment["resumes"][resume_file],
                job_description_path=temp_test_environment["jobs"][job_file],
                output_path=str(output_path)
            )
            
            # Check ATS compliance
            output_content = output_path.read_text()
            ats_checks = quality_validator.check_ats_compliance(output_content)
            
            # All checks should pass
            for check_name, passed in ats_checks.items():
                assert passed, f"ATS check failed for {check_name} in {resume_file}"
            
            print(f"\nATS Compliance for {resume_file}: {sum(ats_checks.values())}/{len(ats_checks)} checks passed")
    
    @pytest.mark.asyncio
    async def test_keyword_integration(self, customizer, temp_test_environment, quality_validator):
        """Test that job keywords are properly integrated."""
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["ai_ml_role.md"]
        output_path = Path(temp_test_environment["output_dir"]) / "keyword_test.md"
        
        # Extract key ML/AI keywords from job description
        job_content = Path(job_path).read_text()
        important_keywords = [
            "machine learning", "tensorflow", "pytorch", "neural network",
            "mlops", "model deployment", "deep learning", "ml pipeline"
        ]
        
        # Run customization
        await customizer.customize(
            resume_path=resume_path,
            job_description_path=job_path,
            output_path=str(output_path)
        )
        
        # Check keyword integration
        original_content = Path(resume_path).read_text()
        output_content = output_path.read_text()
        
        keyword_results = quality_validator.check_keyword_integration(
            original_content,
            output_content,
            important_keywords
        )
        
        # Should integrate at least 50% of keywords
        assert keyword_results["integration_score"] >= 0.5, \
            f"Low keyword integration: {keyword_results['integration_score']:.2%}"
        
        print(f"\nKeyword Integration Results:")
        print(f"  Keywords found: {len(keyword_results['keywords_found'])}/{len(important_keywords)}")
        print(f"  Keywords added: {keyword_results['keywords_added']}")
        print(f"  Integration score: {keyword_results['integration_score']:.2%}")
    
    @pytest.mark.asyncio
    async def test_content_preservation(self, customizer, temp_test_environment, quality_validator):
        """Test that important content is preserved during customization."""
        test_cases = [
            "mid_level.md",
            "senior_level.md",
            "entry_level.md"
        ]
        
        for resume_file in test_cases:
            resume_path = temp_test_environment["resumes"][resume_file]
            job_path = temp_test_environment["jobs"]["standard_swe.md"]
            output_path = Path(temp_test_environment["output_dir"]) / f"preserve_test_{resume_file}"
            
            original_content = Path(resume_path).read_text()
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            output_content = output_path.read_text()
            preservation_checks = quality_validator.check_content_preservation(
                original_content,
                output_content
            )
            
            # Critical information should be preserved
            for check_name, preserved in preservation_checks.items():
                assert preserved, f"Failed to preserve {check_name} in {resume_file}"
            
            # Additional checks
            # Verify no false information added
            if "10 years" not in original_content:
                assert "10 years" not in output_content, "Should not add false experience"
            
            # Verify education preserved
            education_match = re.search(r'## Education.*?(?=##|\Z)', original_content, re.DOTALL | re.IGNORECASE)
            if education_match:
                education_text = education_match.group(0)
                # Extract degree info
                if "BS" in education_text or "Bachelor" in education_text:
                    assert any(term in output_content for term in ["BS", "Bachelor"]), \
                        "Should preserve education credentials"
    
    @pytest.mark.asyncio
    async def test_formatting_consistency(self, customizer, temp_test_environment):
        """Test that output maintains consistent formatting."""
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        output_path = Path(temp_test_environment["output_dir"]) / "format_test.md"
        
        await customizer.customize(
            resume_path=resume_path,
            job_description_path=job_path,
            output_path=str(output_path)
        )
        
        output_content = output_path.read_text()
        
        # Check markdown formatting
        # Count heading levels
        h1_count = len(re.findall(r'^# ', output_content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', output_content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', output_content, re.MULTILINE))
        
        # Should have proper heading hierarchy
        assert h1_count >= 1, "Should have at least one H1 (name)"
        assert h2_count >= 3, "Should have multiple H2 sections"
        
        # Check bullet point consistency
        bullet_lines = re.findall(r'^[-*] ', output_content, re.MULTILINE)
        if bullet_lines:
            # Should use consistent bullet style
            bullet_chars = [line[0] for line in bullet_lines]
            most_common = Counter(bullet_chars).most_common(1)[0][0]
            consistency_ratio = bullet_chars.count(most_common) / len(bullet_chars)
            assert consistency_ratio >= 0.9, "Should use consistent bullet style"
        
        # Check line spacing
        double_newlines = output_content.count('\n\n')
        triple_newlines = output_content.count('\n\n\n')
        assert triple_newlines < 5, "Should not have excessive blank lines"
    
    @pytest.mark.asyncio
    async def test_length_appropriateness(self, customizer, temp_test_environment):
        """Test that output length is appropriate for input."""
        test_cases = [
            ("minimal.md", 0.8, 3.0),  # Can expand minimal significantly
            ("entry_level.md", 0.9, 2.0),  # Moderate expansion
            ("senior_level.md", 0.8, 1.5),  # Less expansion for already detailed
        ]
        
        for resume_file, min_ratio, max_ratio in test_cases:
            resume_path = temp_test_environment["resumes"][resume_file]
            job_path = temp_test_environment["jobs"]["standard_swe.md"]
            output_path = Path(temp_test_environment["output_dir"]) / f"length_test_{resume_file}"
            
            original_length = len(Path(resume_path).read_text())
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            output_length = len(output_path.read_text())
            expansion_ratio = output_length / original_length
            
            assert min_ratio <= expansion_ratio <= max_ratio, \
                f"Inappropriate expansion ratio {expansion_ratio:.2f} for {resume_file}"
            
            print(f"\n{resume_file} - Original: {original_length} chars, "
                  f"Output: {output_length} chars, Ratio: {expansion_ratio:.2f}x")
    
    @pytest.mark.asyncio
    async def test_job_specific_customization(self, customizer, temp_test_environment):
        """Test that same resume is customized differently for different jobs."""
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        
        # Customize for different job types
        job_types = [
            ("standard_swe.md", ["microservices", "restful", "api", "backend"]),
            ("ai_ml_role.md", ["machine learning", "tensorflow", "model", "ml"]),
            ("senior_role.md", ["architect", "leadership", "mentor", "scale"])
        ]
        
        outputs = {}
        
        for job_file, expected_terms in job_types:
            output_path = Path(temp_test_environment["output_dir"]) / f"job_specific_{job_file}"
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=temp_test_environment["jobs"][job_file],
                output_path=str(output_path)
            )
            
            content = output_path.read_text().lower()
            outputs[job_file] = content
            
            # Check job-specific terms
            term_count = sum(1 for term in expected_terms if term in content)
            assert term_count >= len(expected_terms) // 2, \
                f"Should include job-specific terms for {job_file}"
        
        # Verify outputs are different
        contents = list(outputs.values())
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                similarity = len(set(contents[i].split()) & set(contents[j].split())) / \
                           max(len(contents[i].split()), len(contents[j].split()))
                assert similarity < 0.95, "Outputs should be meaningfully different"
    
    @pytest.mark.asyncio
    async def test_iteration_improvement(self, customizer, temp_test_environment, quality_validator):
        """Test that multiple iterations improve quality."""
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["senior_role.md"]
        
        # Extract keywords from job
        job_content = Path(job_path).read_text()
        keywords = ["architect", "distributed", "scale", "leadership", "mentor", "technical strategy"]
        
        results = {}
        
        # Test with different iteration counts
        for iterations in [1, 2, 3]:
            settings = Settings(max_iterations=iterations)
            customizer = ResumeCustomizer(settings)
            
            output_path = Path(temp_test_environment["output_dir"]) / f"iteration_test_{iterations}.md"
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            # Analyze quality
            original_content = Path(resume_path).read_text()
            output_content = output_path.read_text()
            
            keyword_results = quality_validator.check_keyword_integration(
                original_content,
                output_content,
                keywords
            )
            
            ats_checks = quality_validator.check_ats_compliance(output_content)
            
            results[iterations] = {
                "keyword_score": keyword_results["integration_score"],
                "ats_score": sum(ats_checks.values()) / len(ats_checks),
                "length": len(output_content)
            }
        
        # Quality should improve with iterations
        assert results[3]["keyword_score"] >= results[1]["keyword_score"], \
            "Keyword integration should improve with iterations"
        
        print("\n=== Iteration Quality Analysis ===")
        for iterations, metrics in results.items():
            print(f"\n{iterations} iteration(s):")
            print(f"  Keyword score: {metrics['keyword_score']:.2%}")
            print(f"  ATS score: {metrics['ats_score']:.2%}")
            print(f"  Output length: {metrics['length']} chars")
    
    @pytest.mark.asyncio
    async def test_edge_case_quality(self, customizer, temp_test_environment, quality_validator):
        """Test quality for edge case resumes."""
        edge_cases = [
            "minimal.md",
            "career_change.md"
        ]
        
        for resume_file in edge_cases:
            resume_path = temp_test_environment["resumes"][resume_file]
            job_path = temp_test_environment["jobs"]["standard_swe.md"]
            output_path = Path(temp_test_environment["output_dir"]) / f"edge_case_{resume_file}"
            
            original_content = Path(resume_path).read_text()
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            output_content = output_path.read_text()
            
            # Should still produce quality output
            ats_checks = quality_validator.check_ats_compliance(output_content)
            ats_score = sum(ats_checks.values()) / len(ats_checks)
            
            assert ats_score >= 0.7, f"Edge case {resume_file} should still be ATS-compliant"
            
            # Should expand minimal content appropriately
            if len(original_content) < 200:
                assert len(output_content) > 500, "Should expand minimal resumes"
            
            print(f"\nEdge case {resume_file}: ATS score = {ats_score:.2%}, "
                  f"Expansion = {len(output_content)/len(original_content):.1f}x")