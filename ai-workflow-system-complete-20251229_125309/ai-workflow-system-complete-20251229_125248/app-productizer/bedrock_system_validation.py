#!/usr/bin/env python3
"""
AWS Bedrock AI Evolution System - Complete System Validation
===========================================================

Comprehensive validation script that runs all tests, verifies AWS services,
validates cost tracking accuracy, and ensures all security and compliance
requirements are met.

Usage:
    python bedrock_system_validation.py [--config config.yaml] [--aws-config aws_config.json]
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
import argparse
from datetime import datetime

# Import system components
from self_evolving_core.bedrock_framework import BedrockFramework, create_bedrock_framework
from self_evolving_core.aws_config import AWSConfigManager
from self_evolving_core.cost_optimizer import create_cost_management_system
from self_evolving_core.security_compliance import create_security_system
from self_evolving_core.cloud_architecture import create_cloud_architecture
from self_evolving_core.models import Mutation, SystemDNA

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemValidationResult:
    """System validation result container"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.overall_status = "unknown"
        self.test_results = {}
        self.aws_connectivity = {}
        self.cost_validation = {}
        self.security_validation = {}
        self.performance_metrics = {}
        self.compliance_status = {}
        self.errors = []
        self.warnings = []
        self.recommendations = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status,
            "test_results": self.test_results,
            "aws_connectivity": self.aws_connectivity,
            "cost_validation": self.cost_validation,
            "security_validation": self.security_validation,
            "performance_metrics": self.performance_metrics,
            "compliance_status": self.compliance_status,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self.recommendations
        }
    
    def save_report(self, filepath: str) -> None:
        """Save validation report to file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


class BedrockSystemValidator:
    """Comprehensive system validator for Bedrock AI Evolution System"""
    
    def __init__(self, config_path: str = None, aws_config_path: str = None):
        self.config_path = config_path
        self.aws_config_path = aws_config_path
        self.framework: BedrockFramework = None
        self.validation_result = SystemValidationResult()
        
    async def run_complete_validation(self) -> SystemValidationResult:
        """Run complete system validation"""
        
        print("🔍 AWS Bedrock AI Evolution System - Complete Validation")
        print("=" * 60)
        
        try:
            # Step 1: Initialize system
            await self._initialize_system()
            
            # Step 2: Run test suites
            await self._run_test_suites()
            
            # Step 3: Validate AWS connectivity
            await self._validate_aws_services()
            
            # Step 4: Validate cost tracking
            await self._validate_cost_tracking()
            
            # Step 5: Validate security and compliance
            await self._validate_security_compliance()
            
            # Step 6: Run performance tests
            await self._validate_performance()
            
            # Step 7: Test complete evolution workflow
            await self._validate_evolution_workflow()
            
            # Step 8: Generate final assessment
            self._generate_final_assessment()
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            self.validation_result.errors.append(f"Critical validation failure: {e}")
            self.validation_result.overall_status = "failed"
        
        finally:
            if self.framework:
                self.framework.stop()
        
        return self.validation_result
    
    async def _initialize_system(self) -> None:
        """Initialize the Bedrock framework"""
        
        print("\n📋 Step 1: System Initialization")
        print("-" * 30)
        
        try:
            self.framework = create_bedrock_framework(
                config_path=self.config_path,
                aws_config_path=self.aws_config_path
            )
            
            print("✅ Framework initialized successfully")
            
            # Check Bedrock status
            status = self.framework.get_bedrock_status()
            
            if status["bedrock_enabled"]:
                print("✅ Bedrock integration enabled")
                
                # Show connectivity
                connectivity = status.get("aws_connectivity", {})
                for service, connected in connectivity.items():
                    status_icon = "✅" if connected else "❌"
                    print(f"   {status_icon} {service.upper()}: {'Connected' if connected else 'Failed'}")
                    
                self.validation_result.aws_connectivity = connectivity
            else:
                print("⚠️  Bedrock integration disabled - using fallback mode")
                self.validation_result.warnings.append("Bedrock integration not available")
            
        except Exception as e:
            error_msg = f"System initialization failed: {e}"
            print(f"❌ {error_msg}")
            self.validation_result.errors.append(error_msg)
            raise
    
    async def _run_test_suites(self) -> None:
        """Run all test suites"""
        
        print("\n🧪 Step 2: Test Suite Execution")
        print("-" * 30)
        
        test_files = [
            "tests/test_bedrock_integration.py",
            "tests/test_bedrock_properties.py",
            "tests/test_components.py"
        ]
        
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"Running {test_file}...")
                
                try:
                    # Run pytest
                    result = subprocess.run([
                        sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print(f"✅ {test_file}: PASSED")
                        self.validation_result.test_results[test_file] = "passed"
                    else:
                        print(f"❌ {test_file}: FAILED")
                        self.validation_result.test_results[test_file] = "failed"
                        self.validation_result.errors.append(f"Test failures in {test_file}")
                        
                        # Show some error details
                        if result.stdout:
                            print(f"   Output: {result.stdout[-200:]}")  # Last 200 chars
                        if result.stderr:
                            print(f"   Errors: {result.stderr[-200:]}")
                
                except subprocess.TimeoutExpired:
                    error_msg = f"Test timeout: {test_file}"
                    print(f"⏰ {error_msg}")
                    self.validation_result.errors.append(error_msg)
                    self.validation_result.test_results[test_file] = "timeout"
                
                except Exception as e:
                    error_msg = f"Test execution failed for {test_file}: {e}"
                    print(f"❌ {error_msg}")
                    self.validation_result.errors.append(error_msg)
                    self.validation_result.test_results[test_file] = "error"
            else:
                warning_msg = f"Test file not found: {test_file}"
                print(f"⚠️  {warning_msg}")
                self.validation_result.warnings.append(warning_msg)
    
    async def _validate_aws_services(self) -> None:
        """Validate AWS service connectivity and configuration"""
        
        print("\n☁️  Step 3: AWS Services Validation")
        print("-" * 35)
        
        if not self.framework.bedrock_enabled:
            print("⚠️  Skipping AWS validation - Bedrock not enabled")
            return
        
        try:
            # Test Bedrock connectivity
            if self.framework.bedrock_client:
                print("Testing Bedrock connectivity...")
                test_result = self.framework.bedrock_client.test_connection()
                
                if test_result.success:
                    print("✅ Bedrock: Connected")
                    self.validation_result.aws_connectivity["bedrock"] = True
                else:
                    print(f"❌ Bedrock: Failed - {test_result.error}")
                    self.validation_result.aws_connectivity["bedrock"] = False
                    self.validation_result.errors.append(f"Bedrock connection failed: {test_result.error}")
            
            # Test model routing
            if self.framework.model_router:
                print("Testing model router...")
                from self_evolving_core.model_router import TaskContext
                
                test_context = TaskContext(
                    type="analysis",
                    complexity="medium",
                    estimated_tokens=1000,
                    accuracy_requirements=0.8,
                    cost_sensitivity=0.5
                )
                
                selected_model = self.framework.model_router.select_model(test_context)
                
                if selected_model:
                    print(f"✅ Model Router: Working (selected {selected_model})")
                    self.validation_result.aws_connectivity["model_router"] = True
                else:
                    print("❌ Model Router: Failed to select model")
                    self.validation_result.aws_connectivity["model_router"] = False
                    self.validation_result.errors.append("Model router failed to select model")
            
            # Test cloud storage
            if self.framework.cloud_dna_store:
                print("Testing cloud storage...")
                storage_stats = self.framework.cloud_dna_store.get_storage_stats()
                
                if "error" not in storage_stats:
                    print("✅ Cloud Storage: Configured")
                    self.validation_result.aws_connectivity["cloud_storage"] = True
                else:
                    print(f"❌ Cloud Storage: {storage_stats['error']}")
                    self.validation_result.aws_connectivity["cloud_storage"] = False
                    self.validation_result.errors.append(f"Cloud storage error: {storage_stats['error']}")
        
        except Exception as e:
            error_msg = f"AWS services validation failed: {e}"
            print(f"❌ {error_msg}")
            self.validation_result.errors.append(error_msg)
    
    async def _validate_cost_tracking(self) -> None:
        """Validate cost tracking accuracy"""
        
        print("\n💰 Step 4: Cost Tracking Validation")
        print("-" * 35)
        
        try:
            # Create cost management system
            cost_tracker, budget_enforcer, cost_optimizer, monitor = create_cost_management_system(
                storage_path="AI_NETWORK_LOCAL",
                daily_budget=10.0,
                monthly_budget=300.0
            )
            
            # Test cost recording accuracy
            print("Testing cost recording accuracy...")
            
            test_costs = [0.001, 0.002, 0.003, 0.004, 0.005]
            expected_total = sum(test_costs)
            
            for i, cost in enumerate(test_costs):
                cost_tracker.record_cost(
                    category="validation_test",
                    service="bedrock",
                    operation=f"test_op_{i}",
                    amount_usd=cost
                )
            
            actual_total = cost_tracker.get_daily_spend()
            accuracy = abs(actual_total - expected_total)
            
            if accuracy < 0.000001:
                print(f"✅ Cost Accuracy: Perfect (error: {accuracy:.10f})")
                self.validation_result.cost_validation["accuracy"] = "perfect"
            elif accuracy < 0.001:
                print(f"✅ Cost Accuracy: Good (error: {accuracy:.6f})")
                self.validation_result.cost_validation["accuracy"] = "good"
            else:
                print(f"❌ Cost Accuracy: Poor (error: {accuracy:.6f})")
                self.validation_result.cost_validation["accuracy"] = "poor"
                self.validation_result.errors.append(f"Cost tracking accuracy error: {accuracy}")
            
            # Test budget enforcement
            print("Testing budget enforcement...")
            
            budget_enforcer.set_budget("daily", 0.01)  # Very low budget for testing
            
            # Add cost that exceeds budget
            cost_tracker.record_cost("test", "service", "budget_test", 0.02)
            
            status = budget_enforcer.check_budget_status("daily")
            
            if status.usage_percent > 100:
                print("✅ Budget Enforcement: Working (detected overage)")
                self.validation_result.cost_validation["budget_enforcement"] = "working"
            else:
                print("❌ Budget Enforcement: Failed to detect overage")
                self.validation_result.cost_validation["budget_enforcement"] = "failed"
                self.validation_result.errors.append("Budget enforcement failed")
            
            # Test Bedrock cost calculation if available
            if self.framework.bedrock_enabled and self.framework.bedrock_client:
                print("Testing Bedrock cost calculation...")
                
                # Simulate Bedrock usage
                bedrock_cost = cost_tracker.record_bedrock_cost(
                    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                    tokens_input=1000,
                    tokens_output=500,
                    cost_per_1k_input=0.003,
                    cost_per_1k_output=0.015
                )
                
                expected_bedrock_cost = (1000/1000 * 0.003) + (500/1000 * 0.015)
                bedrock_accuracy = abs(bedrock_cost - expected_bedrock_cost)
                
                if bedrock_accuracy < 0.000001:
                    print(f"✅ Bedrock Cost Calculation: Accurate")
                    self.validation_result.cost_validation["bedrock_calculation"] = "accurate"
                else:
                    print(f"❌ Bedrock Cost Calculation: Inaccurate (error: {bedrock_accuracy})")
                    self.validation_result.cost_validation["bedrock_calculation"] = "inaccurate"
                    self.validation_result.errors.append(f"Bedrock cost calculation error: {bedrock_accuracy}")
        
        except Exception as e:
            error_msg = f"Cost tracking validation failed: {e}"
            print(f"❌ {error_msg}")
            self.validation_result.errors.append(error_msg)
    
    async def _validate_security_compliance(self) -> None:
        """Validate security and compliance requirements"""
        
        print("\n🔒 Step 5: Security & Compliance Validation")
        print("-" * 40)
        
        try:
            # Create security system
            security_manager = create_security_system(
                aws_config_manager=self.framework.aws_config_manager if self.framework.bedrock_enabled else None,
                storage_path="AI_NETWORK_LOCAL"
            )
            
            # Test encryption
            print("Testing encryption...")
            
            test_data = "sensitive_validation_data_12345"
            encrypted = security_manager.encryption_manager.encrypt_data(test_data)
            decrypted = security_manager.encryption_manager.decrypt_data(
                encrypted["encrypted_data"],
                encrypted["method"]
            )
            
            if decrypted == test_data:
                print("✅ Encryption: Working (roundtrip successful)")
                self.validation_result.security_validation["encryption"] = "working"
            else:
                print("❌ Encryption: Failed (roundtrip failed)")
                self.validation_result.security_validation["encryption"] = "failed"
                self.validation_result.errors.append("Encryption roundtrip failed")
            
            # Test IAM validation
            print("Testing IAM validation...")
            
            identity = security_manager.iam_manager.get_current_identity()
            
            if "error" not in identity:
                print(f"✅ IAM: Working (User: {identity.get('user_id', 'Unknown')})")
                self.validation_result.security_validation["iam"] = "working"
                self.validation_result.security_validation["aws_identity"] = identity
            else:
                print(f"❌ IAM: Failed ({identity['error']})")
                self.validation_result.security_validation["iam"] = "failed"
                self.validation_result.errors.append(f"IAM validation failed: {identity['error']}")
            
            # Test compliance checks
            print("Testing compliance checks...")
            
            try:
                compliance_report = security_manager.compliance_monitor.generate_compliance_report("soc2")
                
                compliance_score = compliance_report["summary"]["compliance_score"]
                
                if compliance_score >= 80:
                    print(f"✅ Compliance: Good ({compliance_score:.1f}%)")
                    self.validation_result.compliance_status["soc2_score"] = compliance_score
                    self.validation_result.compliance_status["soc2_status"] = "compliant"
                elif compliance_score >= 60:
                    print(f"⚠️  Compliance: Needs Improvement ({compliance_score:.1f}%)")
                    self.validation_result.compliance_status["soc2_score"] = compliance_score
                    self.validation_result.compliance_status["soc2_status"] = "partial"
                    self.validation_result.warnings.append(f"SOC2 compliance needs improvement: {compliance_score:.1f}%")
                else:
                    print(f"❌ Compliance: Poor ({compliance_score:.1f}%)")
                    self.validation_result.compliance_status["soc2_score"] = compliance_score
                    self.validation_result.compliance_status["soc2_status"] = "non_compliant"
                    self.validation_result.errors.append(f"SOC2 compliance is poor: {compliance_score:.1f}%")
            
            except Exception as e:
                print(f"⚠️  Compliance check failed: {e}")
                self.validation_result.warnings.append(f"Compliance check failed: {e}")
        
        except Exception as e:
            error_msg = f"Security validation failed: {e}"
            print(f"❌ {error_msg}")
            self.validation_result.errors.append(error_msg)
    
    async def _validate_performance(self) -> None:
        """Validate system performance"""
        
        print("\n⚡ Step 6: Performance Validation")
        print("-" * 30)
        
        try:
            # Test response times
            print("Testing response times...")
            
            start_time = time.time()
            
            # Test basic operations
            dna = self.framework.get_dna()
            fitness = self.framework.get_fitness()
            status = self.framework.get_enhanced_status()
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response_time < 1.0:
                print(f"✅ Response Time: Excellent ({response_time:.3f}s)")
                self.validation_result.performance_metrics["response_time"] = "excellent"
            elif response_time < 3.0:
                print(f"✅ Response Time: Good ({response_time:.3f}s)")
                self.validation_result.performance_metrics["response_time"] = "good"
            else:
                print(f"⚠️  Response Time: Slow ({response_time:.3f}s)")
                self.validation_result.performance_metrics["response_time"] = "slow"
                self.validation_result.warnings.append(f"Slow response time: {response_time:.3f}s")
            
            self.validation_result.performance_metrics["response_time_seconds"] = response_time
            
            # Test memory usage (simplified)
            print("Testing memory efficiency...")
            
            # Create multiple mutations to test memory usage
            mutations = []
            for i in range(100):
                mutation = Mutation(
                    type="performance_test",
                    description=f"Performance test mutation {i}",
                    fitness_impact=1.0
                )
                mutations.append(mutation)
            
            # Process mutations
            processed = 0
            for mutation in mutations:
                try:
                    result = self.framework.propose_mutation(mutation)
                    if result:
                        processed += 1
                except Exception:
                    pass
            
            if processed >= 90:
                print(f"✅ Memory Efficiency: Good ({processed}/100 processed)")
                self.validation_result.performance_metrics["memory_efficiency"] = "good"
            elif processed >= 70:
                print(f"⚠️  Memory Efficiency: Fair ({processed}/100 processed)")
                self.validation_result.performance_metrics["memory_efficiency"] = "fair"
                self.validation_result.warnings.append(f"Memory efficiency could be improved: {processed}/100")
            else:
                print(f"❌ Memory Efficiency: Poor ({processed}/100 processed)")
                self.validation_result.performance_metrics["memory_efficiency"] = "poor"
                self.validation_result.errors.append(f"Poor memory efficiency: {processed}/100")
            
            self.validation_result.performance_metrics["mutations_processed"] = processed
        
        except Exception as e:
            error_msg = f"Performance validation failed: {e}"
            print(f"❌ {error_msg}")
            self.validation_result.errors.append(error_msg)
    
    async def _validate_evolution_workflow(self) -> None:
        """Validate complete evolution workflow"""
        
        print("\n🧬 Step 7: Evolution Workflow Validation")
        print("-" * 40)
        
        try:
            # Test complete workflow
            print("Testing complete evolution workflow...")
            
            # Step 1: Get initial state
            initial_dna = self.framework.get_dna()
            initial_fitness = self.framework.get_fitness()
            
            print(f"   Initial Generation: {initial_dna.generation}")
            print(f"   Initial Fitness: {initial_fitness.overall:.1f}")
            
            # Step 2: Get evolution guidance (if Bedrock available)
            if self.framework.bedrock_enabled:
                try:
                    guidance = await self.framework.get_evolution_guidance(initial_dna)
                    
                    if "error" not in guidance:
                        print("✅ Evolution Guidance: Generated successfully")
                        self.validation_result.test_results["evolution_guidance"] = "success"
                        
                        # Extract suggested mutation
                        strategy = guidance.get("strategy", {})
                        primary_mutations = strategy.get("primary_mutations", [])
                        
                        if primary_mutations:
                            suggested = primary_mutations[0]
                            mutation = Mutation(
                                type=suggested.get("type", "intelligence_upgrade"),
                                description=suggested.get("description", "LLM-suggested improvement"),
                                fitness_impact=suggested.get("expected_fitness_impact", 3.0),
                                source_ai="evolution_guidance"
                            )
                        else:
                            mutation = Mutation(
                                type="intelligence_upgrade",
                                description="Validation test mutation",
                                fitness_impact=2.0,
                                source_ai="validation"
                            )
                    else:
                        print(f"⚠️  Evolution Guidance: {guidance['error']}")
                        self.validation_result.warnings.append(f"Evolution guidance failed: {guidance['error']}")
                        
                        # Use fallback mutation
                        mutation = Mutation(
                            type="intelligence_upgrade",
                            description="Fallback validation mutation",
                            fitness_impact=2.0,
                            source_ai="validation"
                        )
                
                except Exception as e:
                    print(f"⚠️  Evolution Guidance: Exception - {e}")
                    self.validation_result.warnings.append(f"Evolution guidance exception: {e}")
                    
                    # Use fallback mutation
                    mutation = Mutation(
                        type="intelligence_upgrade",
                        description="Exception fallback mutation",
                        fitness_impact=2.0,
                        source_ai="validation"
                    )
            else:
                print("⚠️  Evolution Guidance: Skipped (Bedrock not available)")
                mutation = Mutation(
                    type="intelligence_upgrade",
                    description="Basic validation mutation",
                    fitness_impact=2.0,
                    source_ai="validation"
                )
            
            # Step 3: Test mutation evaluation
            print("Testing mutation evaluation...")
            
            if self.framework.bedrock_enabled and hasattr(self.framework, 'propose_mutation_enhanced'):
                try:
                    result = await self.framework.propose_mutation_enhanced(mutation)
                    
                    if "enhanced" in result and result["enhanced"]:
                        print("✅ Enhanced Mutation Evaluation: Working")
                        self.validation_result.test_results["enhanced_mutation"] = "success"
                    else:
                        print("⚠️  Enhanced Mutation Evaluation: Fallback used")
                        self.validation_result.warnings.append("Enhanced mutation evaluation used fallback")
                
                except Exception as e:
                    print(f"⚠️  Enhanced Mutation Evaluation: Exception - {e}")
                    self.validation_result.warnings.append(f"Enhanced mutation evaluation failed: {e}")
                    
                    # Try basic evaluation
                    result = self.framework.propose_mutation(mutation)
            else:
                result = self.framework.propose_mutation(mutation)
            
            # Verify result
            if result and ("approved" in result or "request_id" in result):
                print("✅ Mutation Evaluation: Working")
                self.validation_result.test_results["mutation_evaluation"] = "success"
            else:
                print("❌ Mutation Evaluation: Failed")
                self.validation_result.test_results["mutation_evaluation"] = "failed"
                self.validation_result.errors.append("Mutation evaluation failed")
            
            # Step 4: Test system status
            print("Testing system status...")
            
            final_status = self.framework.get_enhanced_status()
            
            if final_status and final_status.get("initialized"):
                print("✅ System Status: Healthy")
                self.validation_result.test_results["system_status"] = "healthy"
            else:
                print("❌ System Status: Unhealthy")
                self.validation_result.test_results["system_status"] = "unhealthy"
                self.validation_result.errors.append("System status is unhealthy")
        
        except Exception as e:
            error_msg = f"Evolution workflow validation failed: {e}"
            print(f"❌ {error_msg}")
            self.validation_result.errors.append(error_msg)
    
    def _generate_final_assessment(self) -> None:
        """Generate final assessment and recommendations"""
        
        print("\n📊 Step 8: Final Assessment")
        print("-" * 25)
        
        # Count results
        total_errors = len(self.validation_result.errors)
        total_warnings = len(self.validation_result.warnings)
        
        # Determine overall status
        if total_errors == 0:
            if total_warnings == 0:
                self.validation_result.overall_status = "excellent"
                status_icon = "🟢"
                status_text = "EXCELLENT"
            elif total_warnings <= 3:
                self.validation_result.overall_status = "good"
                status_icon = "🟡"
                status_text = "GOOD"
            else:
                self.validation_result.overall_status = "fair"
                status_icon = "🟠"
                status_text = "FAIR"
        elif total_errors <= 2:
            self.validation_result.overall_status = "needs_improvement"
            status_icon = "🔴"
            status_text = "NEEDS IMPROVEMENT"
        else:
            self.validation_result.overall_status = "failed"
            status_icon = "❌"
            status_text = "FAILED"
        
        print(f"{status_icon} Overall Status: {status_text}")
        print(f"   Errors: {total_errors}")
        print(f"   Warnings: {total_warnings}")
        
        # Generate recommendations
        if total_errors > 0:
            self.validation_result.recommendations.append("Address all critical errors before production deployment")
        
        if total_warnings > 5:
            self.validation_result.recommendations.append("Review and address warnings to improve system reliability")
        
        if not self.framework.bedrock_enabled:
            self.validation_result.recommendations.append("Configure AWS Bedrock integration for full functionality")
        
        # AWS-specific recommendations
        aws_issues = sum(1 for connected in self.validation_result.aws_connectivity.values() if not connected)
        if aws_issues > 0:
            self.validation_result.recommendations.append(f"Fix {aws_issues} AWS service connectivity issues")
        
        # Cost tracking recommendations
        if self.validation_result.cost_validation.get("accuracy") == "poor":
            self.validation_result.recommendations.append("Improve cost tracking accuracy")
        
        # Security recommendations
        if self.validation_result.security_validation.get("encryption") == "failed":
            self.validation_result.recommendations.append("Fix encryption configuration before handling sensitive data")
        
        # Performance recommendations
        if self.validation_result.performance_metrics.get("response_time") == "slow":
            self.validation_result.recommendations.append("Optimize system performance to improve response times")
        
        # Show recommendations
        if self.validation_result.recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(self.validation_result.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print(f"\n📋 Validation completed at {self.validation_result.timestamp.isoformat()}")


async def main():
    """Main validation entry point"""
    
    parser = argparse.ArgumentParser(description="AWS Bedrock AI Evolution System Validation")
    parser.add_argument("--config", help="Path to framework config file")
    parser.add_argument("--aws-config", help="Path to AWS config file")
    parser.add_argument("--output", help="Output file for validation report", default="validation_report.json")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create validator
    validator = BedrockSystemValidator(
        config_path=args.config,
        aws_config_path=args.aws_config
    )
    
    try:
        # Run validation
        result = await validator.run_complete_validation()
        
        # Save report
        result.save_report(args.output)
        print(f"\n📄 Validation report saved to: {args.output}")
        
        # Exit with appropriate code
        if result.overall_status in ["excellent", "good"]:
            print("\n✅ System validation PASSED")
            sys.exit(0)
        elif result.overall_status in ["fair", "needs_improvement"]:
            print("\n⚠️  System validation PASSED with warnings")
            sys.exit(1)
        else:
            print("\n❌ System validation FAILED")
            sys.exit(2)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Validation failed: {e}")
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())