# ABOUTME: Integration tests for measuring API costs of resume customization
# ABOUTME: Tracks token usage and calculates costs for different resume sizes

"""Integration tests for cost measurement and tracking."""

import pytest
import os
import asyncio
import json
import statistics
from pathlib import Path
from datetime import datetime

from resume_customizer.core.customizer import ResumeCustomizer
from resume_customizer.config import Settings
from tests.integration.fixtures import test_data_manager, temp_test_environment


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping integration tests"
)
class TestCostMeasurement:
    """Test cost tracking and measurement for resume customization."""
    
    @pytest.fixture
    def cost_results_dir(self):
        """Create directory for cost measurement results."""
        results_dir = Path("cost_analysis")
        results_dir.mkdir(exist_ok=True)
        return results_dir
    
    def save_cost_results(self, results: dict, test_name: str, results_dir: Path):
        """Save cost measurement results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"cost_{test_name}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nCost results saved to: {filename}")
    
    @pytest.mark.asyncio
    async def test_cost_by_resume_size(self, test_data_manager, cost_results_dir):
        """Measure costs for different resume sizes."""
        settings = Settings(max_iterations=2)
        customizer = ResumeCustomizer(settings)
        
        # Reset usage stats at the beginning
        customizer.claude_client.reset_usage_stats()
        
        # Test different resume sizes
        sizes = [
            ("small", 200),   # ~200 words
            ("medium", 500),  # ~500 words
            ("large", 1000),  # ~1000 words
        ]
        
        results = {
            "model": "claude-sonnet-4-0",
            "iterations": settings.max_iterations,
            "sizes": {}
        }
        
        with test_data_manager.create_temp_directory() as tmpdir:
            # Create a standard job description
            job_content = """
# Senior Software Engineer

We are looking for an experienced software engineer to join our team.

## Requirements:
- 5+ years of Python experience
- Experience with cloud platforms (AWS, GCP, Azure)
- Strong understanding of software architecture
- Experience with microservices and APIs
- Excellent communication skills

## Responsibilities:
- Design and implement scalable solutions
- Mentor junior developers
- Collaborate with cross-functional teams
- Drive technical decisions
"""
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text(job_content)
            
            for label, word_count in sizes:
                print(f"\nTesting {label} resume ({word_count} words)...")
                
                # Generate resume of specific size
                resume_content = f"# {label.title()} Resume\n\n"
                resume_content += "## Contact\nJohn Doe | john@example.com | 555-0123\n\n"
                resume_content += "## Summary\nExperienced software engineer with expertise in:\n"
                
                # Add skills to reach word count
                skills = ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", 
                         "Kubernetes", "PostgreSQL", "MongoDB", "Redis", "GraphQL", 
                         "REST APIs", "Microservices", "CI/CD", "Agile", "Scrum"]
                
                resume_content += "## Experience\n"
                words_per_job = 50
                num_jobs = max(1, (word_count - 50) // words_per_job)
                
                for i in range(num_jobs):
                    resume_content += f"\n### Software Engineer at Company{i+1}\n"
                    resume_content += f"- Developed scalable applications using {skills[i % len(skills)]}\n"
                    resume_content += f"- Collaborated with team of {5 + i} engineers\n"
                    resume_content += f"- Improved performance by {20 + i*5}% through optimization\n"
                    resume_content += f"- Mentored {2 + i} junior developers\n"
                
                resume_path = Path(tmpdir) / f"resume_{label}.md"
                resume_path.write_text(resume_content)
                
                output_path = Path(tmpdir) / f"output_{label}.md"
                
                # Clear per-request stats
                initial_stats = customizer.claude_client.get_usage_stats()
                
                # Customize resume
                await customizer.customize(
                    resume_path=str(resume_path),
                    job_description_path=str(job_path),
                    output_path=str(output_path)
                )
                
                # Get updated stats
                final_stats = customizer.claude_client.get_usage_stats()
                
                # Calculate this request's metrics
                request_data = final_stats["requests"][-1]
                
                results["sizes"][label] = {
                    "word_count": word_count,
                    "input_size": len(resume_content),
                    "output_size": len(output_path.read_text()) if output_path.exists() else 0,
                    "input_tokens": request_data["input_tokens"],
                    "output_tokens": request_data["output_tokens"],
                    "total_tokens": request_data["input_tokens"] + request_data["output_tokens"],
                    "cost": request_data["cost"],
                    "cost_per_word": request_data["cost"] / word_count,
                    "tokens_per_word": (request_data["input_tokens"] + request_data["output_tokens"]) / word_count
                }
                
                print(f"  Input tokens: {request_data['input_tokens']:,}")
                print(f"  Output tokens: {request_data['output_tokens']:,}")
                print(f"  Cost: ${request_data['cost']:.4f}")
                print(f"  Cost per word: ${request_data['cost']/word_count:.6f}")
        
        # Calculate averages and summary
        all_costs = [size_data["cost"] for size_data in results["sizes"].values()]
        all_tokens = [size_data["total_tokens"] for size_data in results["sizes"].values()]
        
        results["summary"] = {
            "total_requests": len(results["sizes"]),
            "total_cost": sum(all_costs),
            "average_cost": statistics.mean(all_costs),
            "min_cost": min(all_costs),
            "max_cost": max(all_costs),
            "average_tokens": statistics.mean(all_tokens),
            "total_tokens": sum(all_tokens)
        }
        
        # Save results
        self.save_cost_results(results, "by_resume_size", cost_results_dir)
        
        # Print summary
        print("\n=== Cost Summary by Resume Size ===")
        print(f"Average cost per resume: ${results['summary']['average_cost']:.4f}")
        print(f"Total cost for {len(sizes)} resumes: ${results['summary']['total_cost']:.4f}")
        print(f"Cost range: ${results['summary']['min_cost']:.4f} - ${results['summary']['max_cost']:.4f}")
        
        # Assert costs are reasonable (configurable thresholds)
        max_avg_cost = float(os.getenv('MAX_AVERAGE_COST', '0.50'))
        max_single_cost = float(os.getenv('MAX_SINGLE_COST', '1.00'))
        
        assert results['summary']['average_cost'] < max_avg_cost, \
            f"Average cost ${results['summary']['average_cost']:.4f} should be under ${max_avg_cost}"
        assert results['summary']['max_cost'] < max_single_cost, \
            f"Max cost ${results['summary']['max_cost']:.4f} should be under ${max_single_cost}"
    
    @pytest.mark.asyncio
    async def test_cost_by_iterations(self, temp_test_environment, cost_results_dir):
        """Measure how cost scales with iteration count."""
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        
        results = {
            "model": "claude-sonnet-4-0",
            "iterations": {}
        }
        
        for iterations in [1, 2, 3]:
            print(f"\nTesting with {iterations} iterations...")
            
            settings = Settings(max_iterations=iterations)
            customizer = ResumeCustomizer(settings)
            customizer.claude_client.reset_usage_stats()
            
            output_path = Path(temp_test_environment["output_dir"]) / f"cost_iter_{iterations}.md"
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            stats = customizer.claude_client.get_usage_stats()
            
            results["iterations"][iterations] = {
                "input_tokens": stats["total_input_tokens"],
                "output_tokens": stats["total_output_tokens"],
                "total_tokens": stats["total_input_tokens"] + stats["total_output_tokens"],
                "cost": stats["total_cost"],
                "cost_per_iteration": stats["total_cost"] / iterations
            }
            
            print(f"  Total tokens: {stats['total_input_tokens'] + stats['total_output_tokens']:,}")
            print(f"  Cost: ${stats['total_cost']:.4f}")
            print(f"  Cost per iteration: ${stats['total_cost']/iterations:.4f}")
        
        # Calculate scaling factor
        cost_1_iter = results["iterations"][1]["cost"]
        cost_2_iter = results["iterations"][2]["cost"]
        cost_3_iter = results["iterations"][3]["cost"]
        
        results["scaling"] = {
            "2_vs_1_ratio": cost_2_iter / cost_1_iter,
            "3_vs_1_ratio": cost_3_iter / cost_1_iter,
            "marginal_cost_iter_2": cost_2_iter - cost_1_iter,
            "marginal_cost_iter_3": cost_3_iter - cost_2_iter
        }
        
        # Save results
        self.save_cost_results(results, "by_iterations", cost_results_dir)
        
        # Print summary
        print("\n=== Cost Scaling by Iterations ===")
        print(f"1 iteration: ${cost_1_iter:.4f}")
        print(f"2 iterations: ${cost_2_iter:.4f} ({results['scaling']['2_vs_1_ratio']:.2f}x)")
        print(f"3 iterations: ${cost_3_iter:.4f} ({results['scaling']['3_vs_1_ratio']:.2f}x)")
        print(f"Marginal cost of 2nd iteration: ${results['scaling']['marginal_cost_iter_2']:.4f}")
        print(f"Marginal cost of 3rd iteration: ${results['scaling']['marginal_cost_iter_3']:.4f}")
        
        # Assert reasonable scaling
        assert results["scaling"]["2_vs_1_ratio"] < 2.5, "2 iterations should cost less than 2.5x of 1 iteration"
        assert results["scaling"]["3_vs_1_ratio"] < 3.5, "3 iterations should cost less than 3.5x of 1 iteration"
    
    @pytest.mark.asyncio
    async def test_cost_by_complexity(self, temp_test_environment, cost_results_dir):
        """Measure costs for different job complexity levels."""
        settings = Settings(max_iterations=2)
        customizer = ResumeCustomizer(settings)
        customizer.claude_client.reset_usage_stats()
        
        test_cases = [
            ("simple", "minimal.md", "minimal_posting.md"),
            ("standard", "mid_level.md", "standard_swe.md"),
            ("complex", "senior_level.md", "ai_ml_role.md")
        ]
        
        results = {
            "model": "claude-sonnet-4-0",
            "iterations": settings.max_iterations,
            "complexity_levels": {}
        }
        
        for label, resume_file, job_file in test_cases:
            print(f"\nTesting {label} complexity...")
            
            resume_path = temp_test_environment["resumes"][resume_file]
            job_path = temp_test_environment["jobs"][job_file]
            output_path = Path(temp_test_environment["output_dir"]) / f"cost_{label}.md"
            
            initial_cost = customizer.claude_client.get_usage_stats()["total_cost"]
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            final_stats = customizer.claude_client.get_usage_stats()
            request_cost = final_stats["total_cost"] - initial_cost
            request_data = final_stats["requests"][-1]
            
            results["complexity_levels"][label] = {
                "resume_file": resume_file,
                "job_file": job_file,
                "input_size": len(Path(resume_path).read_text()) + len(Path(job_path).read_text()),
                "output_size": len(output_path.read_text()) if output_path.exists() else 0,
                "input_tokens": request_data["input_tokens"],
                "output_tokens": request_data["output_tokens"],
                "total_tokens": request_data["input_tokens"] + request_data["output_tokens"],
                "cost": request_data["cost"]
            }
            
            print(f"  Input size: {results['complexity_levels'][label]['input_size']} chars")
            print(f"  Total tokens: {request_data['input_tokens'] + request_data['output_tokens']:,}")
            print(f"  Cost: ${request_data['cost']:.4f}")
        
        # Save results
        self.save_cost_results(results, "by_complexity", cost_results_dir)
        
        # Print comparison
        print("\n=== Cost by Complexity ===")
        simple_cost = results["complexity_levels"]["simple"]["cost"]
        standard_cost = results["complexity_levels"]["standard"]["cost"]
        complex_cost = results["complexity_levels"]["complex"]["cost"]
        
        print(f"Simple: ${simple_cost:.4f}")
        print(f"Standard: ${standard_cost:.4f} ({standard_cost/simple_cost:.2f}x of simple)")
        print(f"Complex: ${complex_cost:.4f} ({complex_cost/simple_cost:.2f}x of simple)")
        
        # Assert reasonable cost progression
        assert standard_cost > simple_cost, "Standard should cost more than simple"
        assert complex_cost > standard_cost, "Complex should cost more than standard"
        assert complex_cost < simple_cost * 5, "Complex shouldn't cost more than 5x simple"
    
    @pytest.mark.asyncio
    async def test_cost_summary_report(self, cost_results_dir):
        """Generate a comprehensive cost summary report."""
        # Find all cost analysis files
        cost_files = list(cost_results_dir.glob("cost_*.json"))
        
        if not cost_files:
            pytest.skip("No cost analysis files found")
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "model": "claude-sonnet-4-0",
            "pricing": {
                "input_per_million": 3.00,
                "output_per_million": 15.00
            },
            "analyses": {}
        }
        
        total_costs = []
        total_tokens = []
        
        for file in cost_files:
            with open(file) as f:
                data = json.load(f)
            
            analysis_name = file.stem.replace("cost_", "").split('_20')[0]
            summary["analyses"][analysis_name] = data
            
            # Extract costs and tokens
            if "summary" in data:
                total_costs.append(data["summary"]["total_cost"])
                total_tokens.append(data["summary"]["total_tokens"])
            elif "sizes" in data:
                costs = [size["cost"] for size in data["sizes"].values()]
                tokens = [size["total_tokens"] for size in data["sizes"].values()]
                total_costs.extend(costs)
                total_tokens.extend(tokens)
        
        # Calculate overall statistics
        if total_costs:
            summary["overall"] = {
                "total_analyses": len(cost_files),
                "total_requests": len(total_costs),
                "total_cost": sum(total_costs),
                "average_cost_per_request": statistics.mean(total_costs),
                "median_cost_per_request": statistics.median(total_costs),
                "min_cost": min(total_costs),
                "max_cost": max(total_costs),
                "total_tokens": sum(total_tokens),
                "average_tokens_per_request": statistics.mean(total_tokens) if total_tokens else 0
            }
        
        # Save summary
        summary_file = cost_results_dir / "cost_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n=== Overall Cost Summary ===")
        print(f"Summary saved to: {summary_file}")
        if "overall" in summary:
            print(f"Total requests analyzed: {summary['overall']['total_requests']}")
            print(f"Average cost per resume: ${summary['overall']['average_cost_per_request']:.4f}")
            print(f"Median cost per resume: ${summary['overall']['median_cost_per_request']:.4f}")
            print(f"Cost range: ${summary['overall']['min_cost']:.4f} - ${summary['overall']['max_cost']:.4f}")
            print(f"Total cost of all tests: ${summary['overall']['total_cost']:.4f}")
            print(f"Average tokens per request: {summary['overall']['average_tokens_per_request']:,.0f}")