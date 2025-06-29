# ABOUTME: Performance benchmark tests for the resume customizer
# ABOUTME: Measures execution time, resource usage, and scalability metrics

"""Performance benchmark tests for resume customization."""

import pytest
import os
import time
import asyncio
import psutil
import statistics
import tempfile
from pathlib import Path
from datetime import datetime
import json

from resume_customizer.core.customizer import ResumeCustomizer
from resume_customizer.config import Settings
from tests.integration.fixtures import test_data_manager, temp_test_environment, performance_tracker


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping integration tests"
)
class TestPerformanceBenchmarks:
    """Benchmark performance metrics of the resume customizer."""
    
    @pytest.fixture
    def benchmark_results_dir(self):
        """Create directory for benchmark results."""
        results_dir = Path("benchmark_results")
        results_dir.mkdir(exist_ok=True)
        return results_dir
    
    def save_benchmark_results(self, results: dict, benchmark_name: str, results_dir: Path):
        """Save benchmark results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"{benchmark_name}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nBenchmark results saved to: {filename}")
    
    @pytest.mark.asyncio
    async def test_baseline_performance(self, temp_test_environment, performance_tracker, benchmark_results_dir):
        """Establish baseline performance metrics."""
        settings = Settings(max_iterations=2)
        customizer = ResumeCustomizer(settings)
        
        # Test cases with expected performance characteristics
        test_cases = [
            ("minimal", "minimal.md", "minimal_posting.md", 30),  # Simple, fast
            ("standard", "mid_level.md", "standard_swe.md", 45),  # Average
            ("complex", "senior_level.md", "ai_ml_role.md", 60),  # Complex, slower
        ]
        
        results = {}
        
        for label, resume_file, job_file, expected_max_time in test_cases:
            resume_path = temp_test_environment["resumes"][resume_file]
            job_path = temp_test_environment["jobs"][job_file]
            output_path = Path(temp_test_environment["output_dir"]) / f"baseline_{label}.md"
            
            # Measure performance
            performance_tracker.start()
            start_time = time.time()
            
            # Track memory before
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            end_time = time.time()
            performance_tracker.stop()
            
            # Track memory after
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = memory_after - memory_before
            
            duration = end_time - start_time
            
            results[label] = {
                "duration_seconds": duration,
                "memory_delta_mb": memory_delta,
                "input_size": len(Path(resume_path).read_text()) + len(Path(job_path).read_text()),
                "output_size": len(output_path.read_text()),
                "passed": duration <= expected_max_time
            }
            
            # Assert performance is reasonable
            assert duration <= expected_max_time, \
                f"{label} case took {duration:.2f}s, expected <= {expected_max_time}s"
            
            print(f"\n{label.upper()} Performance:")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Memory delta: {memory_delta:.2f} MB")
            print(f"  Output size: {results[label]['output_size']} chars")
        
        # Save results
        self.save_benchmark_results(results, "baseline_performance", benchmark_results_dir)
    
    @pytest.mark.asyncio
    async def test_iteration_scaling(self, temp_test_environment, benchmark_results_dir):
        """Test how performance scales with iteration count."""
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        
        results = {}
        
        for iterations in [1, 2, 3, 5]:
            settings = Settings(max_iterations=iterations)
            customizer = ResumeCustomizer(settings)
            
            output_path = Path(temp_test_environment["output_dir"]) / f"iteration_scale_{iterations}.md"
            
            start_time = time.time()
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            duration = time.time() - start_time
            
            results[f"{iterations}_iterations"] = {
                "duration_seconds": duration,
                "per_iteration_avg": duration / iterations,
                "output_size": len(output_path.read_text())
            }
            
            print(f"\n{iterations} iterations: {duration:.2f}s total, "
                  f"{duration/iterations:.2f}s per iteration")
        
        # Check scaling is reasonable (not perfectly linear due to overhead)
        assert results["2_iterations"]["duration_seconds"] < results["1_iterations"]["duration_seconds"] * 2.5
        assert results["3_iterations"]["duration_seconds"] < results["1_iterations"]["duration_seconds"] * 3.5
        
        self.save_benchmark_results(results, "iteration_scaling", benchmark_results_dir)
    
    @pytest.mark.asyncio
    async def test_input_size_scaling(self, test_data_manager, benchmark_results_dir):
        """Test how performance scales with input size."""
        results = {}
        
        # Create resumes of different sizes
        sizes = [
            ("tiny", 50),    # ~50 words
            ("small", 200),  # ~200 words
            ("medium", 500), # ~500 words
            ("large", 1000), # ~1000 words
            ("huge", 2000)   # ~2000 words
        ]
        
        settings = Settings(max_iterations=1)
        customizer = ResumeCustomizer(settings)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Looking for a software engineer with Python experience")
            
            for label, word_count in sizes:
                # Generate resume of specific size
                resume_content = f"# Test Resume {label}\n\n"
                resume_content += "## Experience\n"
                
                words_per_line = 10
                for i in range(word_count // words_per_line):
                    resume_content += f"- Worked on project {i} with " + " ".join(
                        ["technology"] * (words_per_line - 5)
                    ) + "\n"
                
                resume_path = Path(tmpdir) / f"resume_{label}.md"
                resume_path.write_text(resume_content)
                
                output_path = Path(tmpdir) / f"output_{label}.md"
                
                start_time = time.time()
                
                await customizer.customize(
                    resume_path=str(resume_path),
                    job_description_path=str(job_path),
                    output_path=str(output_path)
                )
                
                duration = time.time() - start_time
                
                results[label] = {
                    "word_count": word_count,
                    "input_size": len(resume_content),
                    "duration_seconds": duration,
                    "throughput_words_per_second": word_count / duration,
                    "output_size": len(output_path.read_text())
                }
                
                print(f"\n{label.upper()} ({word_count} words): {duration:.2f}s, "
                      f"{word_count/duration:.1f} words/sec")
        
        # Performance should scale sub-linearly
        tiny_throughput = results["tiny"]["throughput_words_per_second"]
        huge_throughput = results["huge"]["throughput_words_per_second"]
        
        # Larger inputs should have better throughput (economies of scale)
        assert huge_throughput > tiny_throughput * 0.5, \
            "Performance should not degrade too much with size"
        
        self.save_benchmark_results(results, "input_size_scaling", benchmark_results_dir)
    
    @pytest.mark.asyncio
    async def test_concurrent_performance(self, temp_test_environment, benchmark_results_dir):
        """Test performance with concurrent customizations."""
        settings = Settings(max_iterations=1)
        
        resume_path = temp_test_environment["resumes"]["minimal.md"]
        job_path = temp_test_environment["jobs"]["minimal_posting.md"]
        
        results = {}
        
        # Test different concurrency levels
        for concurrency in [1, 2, 3, 5]:
            customizers = [ResumeCustomizer(settings) for _ in range(concurrency)]
            
            tasks = []
            for i, customizer in enumerate(customizers):
                output_path = Path(temp_test_environment["output_dir"]) / f"concurrent_{concurrency}_{i}.md"
                
                task = customizer.customize(
                    resume_path=resume_path,
                    job_description_path=job_path,
                    output_path=str(output_path)
                )
                tasks.append(task)
            
            start_time = time.time()
            await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            results[f"concurrency_{concurrency}"] = {
                "total_duration_seconds": total_time,
                "avg_per_task_seconds": total_time / concurrency,
                "throughput_tasks_per_second": concurrency / total_time
            }
            
            print(f"\nConcurrency {concurrency}: {total_time:.2f}s total, "
                  f"{total_time/concurrency:.2f}s per task")
        
        # Should show some benefit from concurrency
        single_throughput = results["concurrency_1"]["throughput_tasks_per_second"]
        multi_throughput = results["concurrency_3"]["throughput_tasks_per_second"]
        
        assert multi_throughput > single_throughput * 1.5, \
            "Should see throughput improvement with concurrency"
        
        self.save_benchmark_results(results, "concurrent_performance", benchmark_results_dir)
    
    @pytest.mark.asyncio
    async def test_memory_usage_profile(self, temp_test_environment, benchmark_results_dir):
        """Profile memory usage during customization."""
        settings = Settings(max_iterations=2)
        customizer = ResumeCustomizer(settings)
        
        resume_path = temp_test_environment["resumes"]["senior_level.md"]
        job_path = temp_test_environment["jobs"]["senior_role.md"]
        output_path = Path(temp_test_environment["output_dir"]) / "memory_profile.md"
        
        process = psutil.Process()
        memory_samples = []
        
        # Sample memory usage during execution
        async def monitor_memory():
            while True:
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append({
                    "timestamp": time.time(),
                    "memory_mb": memory_mb
                })
                await asyncio.sleep(0.1)
        
        # Start monitoring
        monitor_task = asyncio.create_task(monitor_memory())
        
        start_time = time.time()
        
        try:
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
        finally:
            monitor_task.cancel()
        
        end_time = time.time()
        
        # Analyze memory usage
        if memory_samples:
            memory_values = [s["memory_mb"] for s in memory_samples]
            
            results = {
                "duration_seconds": end_time - start_time,
                "memory_samples": len(memory_samples),
                "memory_min_mb": min(memory_values),
                "memory_max_mb": max(memory_values),
                "memory_avg_mb": statistics.mean(memory_values),
                "memory_stdev_mb": statistics.stdev(memory_values) if len(memory_values) > 1 else 0,
                "memory_delta_mb": max(memory_values) - min(memory_values)
            }
            
            print(f"\nMemory Profile:")
            print(f"  Min: {results['memory_min_mb']:.1f} MB")
            print(f"  Max: {results['memory_max_mb']:.1f} MB")
            print(f"  Avg: {results['memory_avg_mb']:.1f} MB")
            print(f"  Delta: {results['memory_delta_mb']:.1f} MB")
            
            # Memory usage should be reasonable
            assert results['memory_delta_mb'] < 500, "Memory usage should not spike excessively"
            
            self.save_benchmark_results(results, "memory_profile", benchmark_results_dir)
    
    @pytest.mark.asyncio
    async def test_stress_test(self, temp_test_environment, benchmark_results_dir):
        """Stress test with many rapid customizations."""
        settings = Settings(max_iterations=1)
        customizer = ResumeCustomizer(settings)
        
        resume_path = temp_test_environment["resumes"]["minimal.md"]
        job_path = temp_test_environment["jobs"]["minimal_posting.md"]
        
        num_requests = 10
        results = {
            "num_requests": num_requests,
            "durations": [],
            "successes": 0,
            "failures": 0
        }
        
        start_time = time.time()
        
        for i in range(num_requests):
            output_path = Path(temp_test_environment["output_dir"]) / f"stress_{i}.md"
            
            request_start = time.time()
            
            try:
                await customizer.customize(
                    resume_path=resume_path,
                    job_description_path=job_path,
                    output_path=str(output_path)
                )
                
                duration = time.time() - request_start
                results["durations"].append(duration)
                results["successes"] += 1
                
            except Exception as e:
                results["failures"] += 1
                print(f"Request {i} failed: {e}")
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        total_time = time.time() - start_time
        
        if results["durations"]:
            results.update({
                "total_duration_seconds": total_time,
                "avg_duration_seconds": statistics.mean(results["durations"]),
                "min_duration_seconds": min(results["durations"]),
                "max_duration_seconds": max(results["durations"]),
                "throughput_requests_per_minute": (results["successes"] / total_time) * 60
            })
        
        print(f"\nStress Test Results:")
        print(f"  Successes: {results['successes']}/{num_requests}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {results.get('throughput_requests_per_minute', 0):.1f} req/min")
        
        # Should handle stress reasonably well
        assert results["successes"] >= num_requests * 0.8, \
            "Should succeed in at least 80% of requests"
        
        self.save_benchmark_results(results, "stress_test", benchmark_results_dir)
    
    def test_benchmark_summary(self, benchmark_results_dir):
        """Generate summary of all benchmark results."""
        # Find all benchmark files
        benchmark_files = list(benchmark_results_dir.glob("*.json"))
        
        if not benchmark_files:
            pytest.skip("No benchmark results found")
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "benchmarks": {}
        }
        
        for file in benchmark_files:
            with open(file) as f:
                data = json.load(f)
                
            benchmark_name = file.stem.split('_20')[0]  # Remove timestamp
            summary["benchmarks"][benchmark_name] = data
        
        # Save summary
        summary_file = benchmark_results_dir / "benchmark_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nBenchmark summary saved to: {summary_file}")
        print(f"Total benchmarks: {len(summary['benchmarks'])}")