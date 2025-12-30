#!/usr/bin/env python3
"""
Package Validation Script
Validates that the AgentCore Demo package is ready for commercial distribution
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class PackageValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check(self, condition, success_msg, error_msg):
        """Run a validation check"""
        self.total_checks += 1
        if condition:
            print(f"✅ {success_msg}")
            self.success_count += 1
            return True
        else:
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def warn(self, condition, warning_msg):
        """Run a warning check"""
        if not condition:
            print(f"⚠️  {warning_msg}")
            self.warnings.append(warning_msg)
    
    def validate_file_structure(self):
        """Validate required files exist"""
        print("\n📁 Validating File Structure...")
        
        required_files = [
            "agent.py",
            "requirements.txt",
            "setup.py",
            "README.md",
            "LICENSE",
            "DEPLOYMENT_GUIDE.md",
            "COMMERCIAL_PACKAGE.md",
            ".env.example",
            "tests/__init__.py",
            "tests/test_agent.py"
        ]
        
        for file_path in required_files:
            exists = Path(file_path).exists()
            self.check(
                exists,
                f"Required file exists: {file_path}",
                f"Missing required file: {file_path}"
            )
    
    def validate_python_syntax(self):
        """Validate Python files have correct syntax"""
        print("\n🐍 Validating Python Syntax...")
        
        python_files = ["agent.py", "setup.py", "tests/test_agent.py", "validate_package.py"]
        
        for file_path in python_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_path, 'exec')
                    self.check(
                        True,
                        f"Valid Python syntax: {file_path}",
                        f"Syntax error in: {file_path}"
                    )
                except SyntaxError as e:
                    self.check(
                        False,
                        f"Valid Python syntax: {file_path}",
                        f"Syntax error in {file_path}: {e}"
                    )
    
    def validate_imports(self):
        """Validate that required imports work"""
        print("\n📦 Validating Imports...")
        
        try:
            from agent import agent_handler, AgentCoreDemo
            self.check(
                True,
                "Agent imports work correctly",
                "Failed to import agent components"
            )
        except ImportError as e:
            self.check(
                False,
                "Agent imports work correctly",
                f"Import error: {e}"
            )
    
    def validate_agent_functionality(self):
        """Test basic agent functionality"""
        print("\n🤖 Validating Agent Functionality...")
        
        try:
            from agent import agent_handler
            
            # Test basic request
            response = agent_handler({"prompt": "hello"})
            
            self.check(
                isinstance(response, dict),
                "Agent returns dictionary response",
                "Agent does not return dictionary"
            )
            
            self.check(
                "response" in response,
                "Response contains 'response' field",
                "Response missing 'response' field"
            )
            
            self.check(
                "status" in response,
                "Response contains 'status' field",
                "Response missing 'status' field"
            )
            
            self.check(
                response.get("status") == "success",
                "Agent returns success status",
                f"Agent returned status: {response.get('status')}"
            )
            
        except Exception as e:
            self.check(
                False,
                "Agent functionality test passed",
                f"Agent functionality error: {e}"
            )
    
    def validate_tests(self):
        """Run the test suite"""
        print("\n🧪 Running Test Suite...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=".")
            
            self.check(
                result.returncode == 0,
                "All tests pass",
                f"Tests failed: {result.stdout}\n{result.stderr}"
            )
            
        except Exception as e:
            self.check(
                False,
                "Test suite runs successfully",
                f"Error running tests: {e}"
            )
    
    def validate_dependencies(self):
        """Validate requirements.txt is valid"""
        print("\n📋 Validating Dependencies...")
        
        try:
            with open("requirements.txt", "r") as f:
                requirements = f.read().strip().split("\n")
            
            required_deps = [
                "bedrock-agentcore",
                "boto3",
                "pytest"
            ]
            
            for dep in required_deps:
                found = any(dep in req for req in requirements if req.strip())
                self.check(
                    found,
                    f"Required dependency found: {dep}",
                    f"Missing required dependency: {dep}"
                )
                
        except Exception as e:
            self.check(
                False,
                "Requirements file is valid",
                f"Error reading requirements: {e}"
            )
    
    def validate_documentation(self):
        """Validate documentation completeness"""
        print("\n📚 Validating Documentation...")
        
        # Check README has key sections
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                readme_content = f.read()
            
            required_sections = [
                "Installation",
                "Usage",
                "Deployment",
                "Features"
            ]
            
            for section in required_sections:
                found = section.lower() in readme_content.lower()
                self.check(
                    found,
                    f"README contains {section} section",
                    f"README missing {section} section"
                )
                
        except Exception as e:
            self.check(
                False,
                "README documentation is complete",
                f"Error reading README: {e}"
            )
    
    def validate_commercial_readiness(self):
        """Validate commercial package readiness"""
        print("\n💼 Validating Commercial Readiness...")
        
        # Check license exists
        license_exists = Path("LICENSE").exists()
        self.check(
            license_exists,
            "License file exists",
            "Missing LICENSE file"
        )
        
        # Check commercial package documentation
        commercial_doc_exists = Path("COMMERCIAL_PACKAGE.md").exists()
        self.check(
            commercial_doc_exists,
            "Commercial package documentation exists",
            "Missing COMMERCIAL_PACKAGE.md"
        )
        
        # Check deployment guide
        deployment_guide_exists = Path("DEPLOYMENT_GUIDE.md").exists()
        self.check(
            deployment_guide_exists,
            "Deployment guide exists",
            "Missing DEPLOYMENT_GUIDE.md"
        )
    
    def run_all_validations(self):
        """Run all validation checks"""
        print("🔍 AgentCore Demo Package Validation")
        print("=" * 50)
        
        self.validate_file_structure()
        self.validate_python_syntax()
        self.validate_imports()
        self.validate_agent_functionality()
        self.validate_dependencies()
        self.validate_documentation()
        self.validate_commercial_readiness()
        self.validate_tests()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        print(f"✅ Successful checks: {self.success_count}/{self.total_checks}")
        
        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
            print("\n🚨 PACKAGE NOT READY FOR DISTRIBUTION")
            return False
        else:
            print("\n🎉 PACKAGE READY FOR COMMERCIAL DISTRIBUTION!")
            print("\n📦 Next Steps:")
            print("   1. Create distribution package")
            print("   2. Set up payment processing")
            print("   3. Create marketing materials")
            print("   4. Launch on marketplace")
            return True

if __name__ == "__main__":
    validator = PackageValidator()
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)