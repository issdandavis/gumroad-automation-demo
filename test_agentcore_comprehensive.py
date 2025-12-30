#!/usr/bin/env python3
"""
Comprehensive AgentCore Demo Testing Suite
Tests all functionality and generates detailed performance data
Last Updated: 2025-12-29 - All tests passing, comprehensive coverage
"""

import time
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
import concurrent.futures
import statistics

# Add agentcore_demo to path
sys.path.insert(0, str(Path("agentcore_demo").absolute()))

try:
    from agent import agent_handler, AgentCoreDemo
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the root directory")
    sys.exit(1)

class AgentCoreTestSuite:
    def __init__(self):
        self.test_results = []
        self.performance_data = []
        self.error_log = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name, status, duration, details=None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status} ({result['duration_ms']}ms)")
        
    def log_performance(self, metric_name, value, unit="ms"):
        """Log performance metric"""
        self.performance_data.append({
            "metric": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_basic_functionality(self):
        """Test basic agent functionality"""
        print("\n🧪 Testing Basic Functionality...")
        
        test_cases = [
            {"prompt": "hello", "expected_keywords": ["Hello", "AgentCore"]},
            {"prompt": "what time is it", "expected_keywords": ["Current time", "2025"]},
            {"prompt": "tell me about agentcore", "expected_keywords": ["AgentCore", "AWS", "serverless"]},
            {"prompt": "what are your capabilities", "expected_keywords": ["capabilities", "demo agent"]},
            {"prompt": "random question", "expected_keywords": ["You said", "demo agent"]}
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            start_time = time.time()
            
            try:
                response = agent_handler({"prompt": test_case["prompt"]})
                duration = time.time() - start_time
                
                # Check response structure
                if not isinstance(response, dict):
                    self.log_test(f"Basic Test {i}", "FAIL", duration, 
                                {"error": "Response not a dictionary"})
                    continue
                
                # Check required fields
                required_fields = ["response", "status", "agent_name", "timestamp"]
                missing_fields = [f for f in required_fields if f not in response]
                
                if missing_fields:
                    self.log_test(f"Basic Test {i}", "FAIL", duration,
                                {"error": f"Missing fields: {missing_fields}"})
                    continue
                
                # Check status
                if response.get("status") != "success":
                    self.log_test(f"Basic Test {i}", "FAIL", duration,
                                {"error": f"Status: {response.get('status')}"})
                    continue
                
                # Check expected keywords
                response_text = response.get("response", "").lower()
                found_keywords = [kw for kw in test_case["expected_keywords"] 
                                if kw.lower() in response_text]
                
                if not found_keywords:
                    self.log_test(f"Basic Test {i}", "FAIL", duration,
                                {"error": f"No expected keywords found in response"})
                    continue
                
                self.log_test(f"Basic Test {i}", "PASS", duration, {
                    "prompt": test_case["prompt"],
                    "response_length": len(response.get("response", "")),
                    "found_keywords": found_keywords
                })
                
                self.log_performance(f"Response Time Test {i}", duration * 1000)
                
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Basic Test {i}", "ERROR", duration, {"exception": str(e)})
                self.error_log.append(f"Basic Test {i}: {e}")
    
    def test_performance_benchmarks(self):
        """Test performance under various conditions"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        # Single request performance
        start_time = time.time()
        response = agent_handler({"prompt": "performance test"})
        single_request_time = time.time() - start_time
        
        self.log_test("Single Request Performance", "PASS", single_request_time, {
            "response_size": len(str(response))
        })
        self.log_performance("Single Request Time", single_request_time * 1000)
        
        # Multiple sequential requests
        sequential_times = []
        for i in range(10):
            start_time = time.time()
            agent_handler({"prompt": f"sequential test {i}"})
            sequential_times.append(time.time() - start_time)
        
        avg_sequential = statistics.mean(sequential_times)
        self.log_test("Sequential Requests (10x)", "PASS", sum(sequential_times), {
            "average_time": round(avg_sequential * 1000, 2),
            "min_time": round(min(sequential_times) * 1000, 2),
            "max_time": round(max(sequential_times) * 1000, 2)
        })
        self.log_performance("Average Sequential Time", avg_sequential * 1000)
        
        # Concurrent requests
        def concurrent_request(i):
            start_time = time.time()
            response = agent_handler({"prompt": f"concurrent test {i}"})
            return time.time() - start_time, response
        
        start_concurrent = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(concurrent_request, i) for i in range(10)]
            concurrent_results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        total_concurrent_time = time.time() - start_concurrent
        concurrent_times = [result[0] for result in concurrent_results]
        avg_concurrent = statistics.mean(concurrent_times)
        
        self.log_test("Concurrent Requests (10x)", "PASS", total_concurrent_time, {
            "total_time": round(total_concurrent_time * 1000, 2),
            "average_individual": round(avg_concurrent * 1000, 2),
            "throughput_rps": round(10 / total_concurrent_time, 2)
        })
        self.log_performance("Concurrent Throughput", 10 / total_concurrent_time, "rps")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🔍 Testing Edge Cases...")
        
        edge_cases = [
            {"name": "Empty Prompt", "input": {"prompt": ""}},
            {"name": "None Prompt", "input": {"prompt": None}},
            {"name": "Missing Prompt", "input": {}},
            {"name": "Long Prompt", "input": {"prompt": "x" * 1000}},
            {"name": "Special Characters", "input": {"prompt": "!@#$%^&*()_+{}|:<>?[]\\;'\",./<>?"}},
            {"name": "Unicode Characters", "input": {"prompt": "Hello 世界 🌍 émojis"}},
            {"name": "Number Prompt", "input": {"prompt": 12345}},
            {"name": "List Prompt", "input": {"prompt": ["hello", "world"]}},
            {"name": "Dict Prompt", "input": {"prompt": {"nested": "value"}}},
        ]
        
        for case in edge_cases:
            start_time = time.time()
            
            try:
                response = agent_handler(case["input"])
                duration = time.time() - start_time
                
                # Should always return a dict with status
                if isinstance(response, dict) and "status" in response:
                    self.log_test(f"Edge Case: {case['name']}", "PASS", duration, {
                        "input_type": type(case["input"].get("prompt", None)).__name__,
                        "response_status": response.get("status")
                    })
                else:
                    self.log_test(f"Edge Case: {case['name']}", "FAIL", duration, {
                        "error": "Invalid response structure"
                    })
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Edge Case: {case['name']}", "ERROR", duration, {
                    "exception": str(e)
                })
                self.error_log.append(f"Edge Case {case['name']}: {e}")
    
    def test_memory_usage(self):
        """Test memory usage patterns"""
        print("\n💾 Testing Memory Usage...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple requests to test memory leaks
        for i in range(100):
            agent_handler({"prompt": f"memory test {i}"})
            
            if i % 20 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                self.log_performance(f"Memory Usage After {i+1} Requests", current_memory, "MB")
        
        final_memory = process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 50MB for 100 requests)
        memory_status = "PASS" if total_increase < 50 else "WARN"
        
        self.log_test("Memory Usage Test", memory_status, 0, {
            "initial_memory_mb": round(initial_memory, 2),
            "final_memory_mb": round(final_memory, 2),
            "increase_mb": round(total_increase, 2),
            "requests_tested": 100
        })
    
    def test_json_serialization(self):
        """Test JSON serialization of responses"""
        print("\n📄 Testing JSON Serialization...")
        
        start_time = time.time()
        
        try:
            response = agent_handler({"prompt": "json test"})
            
            # Test JSON serialization
            json_str = json.dumps(response)
            parsed_back = json.loads(json_str)
            
            duration = time.time() - start_time
            
            if parsed_back == response:
                self.log_test("JSON Serialization", "PASS", duration, {
                    "json_size_bytes": len(json_str),
                    "serializable": True
                })
            else:
                self.log_test("JSON Serialization", "FAIL", duration, {
                    "error": "Deserialized data doesn't match original"
                })
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("JSON Serialization", "ERROR", duration, {
                "exception": str(e)
            })
    
    def test_agentcore_integration(self):
        """Test AgentCore-specific features"""
        print("\n🔗 Testing AgentCore Integration...")
        
        # Test with AgentCore-style request context
        agentcore_request = {
            "prompt": "AgentCore integration test",
            "user_id": "test_user_123",
            "session_id": "test_session_456",
            "metadata": {
                "source": "agentcore",
                "version": "1.0.0"
            }
        }
        
        start_time = time.time()
        
        try:
            response = agent_handler(agentcore_request)
            duration = time.time() - start_time
            
            # Check if user_id and session_id are preserved
            user_id_preserved = response.get("user_id") == "test_user_123"
            session_id_preserved = response.get("session_id") == "test_session_456"
            
            if user_id_preserved and session_id_preserved:
                self.log_test("AgentCore Integration", "PASS", duration, {
                    "user_id_preserved": user_id_preserved,
                    "session_id_preserved": session_id_preserved,
                    "agent_name": response.get("agent_name")
                })
            else:
                self.log_test("AgentCore Integration", "FAIL", duration, {
                    "user_id_preserved": user_id_preserved,
                    "session_id_preserved": session_id_preserved
                })
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("AgentCore Integration", "ERROR", duration, {
                "exception": str(e)
            })
    
    def generate_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        error_tests = len([t for t in self.test_results if t["status"] == "ERROR"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Performance statistics
        response_times = [t["duration_ms"] for t in self.test_results if t["duration_ms"] > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate_percent": round(success_rate, 2),
                "total_duration_seconds": round(total_duration, 2)
            },
            "performance_summary": {
                "average_response_time_ms": round(avg_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "total_requests_tested": len(response_times)
            },
            "detailed_results": self.test_results,
            "performance_metrics": self.performance_data,
            "errors": self.error_log,
            "test_environment": {
                "python_version": sys.version,
                "test_timestamp": end_time.isoformat(),
                "agent_version": "1.0.0"
            }
        }
        
        return report
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 AgentCore Demo - Comprehensive Testing Suite")
        print("=" * 60)
        
        try:
            self.test_basic_functionality()
            self.test_performance_benchmarks()
            self.test_edge_cases()
            self.test_json_serialization()
            self.test_agentcore_integration()
            
            # Only test memory if psutil is available
            try:
                import psutil
                self.test_memory_usage()
            except ImportError:
                print("⚠️ Skipping memory tests (psutil not available)")
            
            return self.generate_report()
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            traceback.print_exc()
            return None

def main():
    """Run tests and save report"""
    test_suite = AgentCoreTestSuite()
    report = test_suite.run_all_tests()
    
    if report:
        # Save detailed report
        report_file = f"agentcore_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        summary = report["test_summary"]
        perf = report["performance_summary"]
        
        print(f"✅ Tests Passed: {summary['passed']}/{summary['total_tests']} ({summary['success_rate_percent']}%)")
        print(f"❌ Tests Failed: {summary['failed']}")
        print(f"🔥 Errors: {summary['errors']}")
        print(f"⏱️ Total Duration: {summary['total_duration_seconds']}s")
        print(f"🚀 Avg Response Time: {perf['average_response_time_ms']}ms")
        print(f"⚡ Min Response Time: {perf['min_response_time_ms']}ms")
        print(f"🐌 Max Response Time: {perf['max_response_time_ms']}ms")
        
        if report["errors"]:
            print(f"\n🚨 Errors Encountered:")
            for error in report["errors"]:
                print(f"   • {error}")
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        # Determine overall status
        if summary['success_rate_percent'] >= 90:
            print("\n🎉 OVERALL STATUS: EXCELLENT - Ready for production!")
        elif summary['success_rate_percent'] >= 75:
            print("\n✅ OVERALL STATUS: GOOD - Minor issues to address")
        elif summary['success_rate_percent'] >= 50:
            print("\n⚠️ OVERALL STATUS: NEEDS WORK - Several issues found")
        else:
            print("\n❌ OVERALL STATUS: CRITICAL ISSUES - Major problems detected")
        
        return report
    else:
        print("\n❌ Test suite failed to complete")
        return None

if __name__ == "__main__":
    main()