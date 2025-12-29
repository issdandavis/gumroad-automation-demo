"""
Quality Assurance Checker Lambda
Validates apps are production-ready and sellable
"""

import json
import boto3
import os
import zipfile
import tempfile
import subprocess
import requests
from datetime import datetime
from typing import Dict, Any, List

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Run comprehensive quality checks on an app
    """
    try:
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
            
        build_id = body.get('build_id')
        app_id = body.get('app_id')
        
        if not build_id and not app_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'build_id or app_id is required'})
            }
        
        # Download app package from S3
        app_bucket = os.environ['APP_BUCKET']
        package_path = download_app_package(app_bucket, build_id or app_id)
        
        # Run quality checks
        qa_results = run_quality_checks(package_path, app_id or build_id)
        
        # Generate quality report
        report = generate_quality_report(qa_results)
        
        # Update status in DynamoDB
        update_app_status(app_id or build_id, 'quality_check_completed', {
            'qa_results': qa_results,
            'report': report,
            'checked_at': datetime.utcnow().isoformat()
        })
        
        # Trigger next step if quality checks pass
        if qa_results['overall_score'] >= 80:
            trigger_next_step(app_id or build_id, 'quality_passed')
        else:
            trigger_next_step(app_id or build_id, 'quality_failed')
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Quality check completed',
                'app_id': app_id or build_id,
                'overall_score': qa_results['overall_score'],
                'passed': qa_results['overall_score'] >= 80,
                'report': report
            })
        }
        
    except Exception as e:
        print(f"Error running quality checks: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def download_app_package(bucket: str, package_id: str) -> str:
    """Download app package from S3 and extract"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download zip file
        zip_path = os.path.join(temp_dir, 'app-package.zip')
        
        try:
            s3.download_file(bucket, f"{package_id}/app-package.zip", zip_path)
        except Exception as e:
            print(f"Error downloading package: {str(e)}")
            # Try alternative path
            s3.download_file(bucket, f"{package_id}.zip", zip_path)
        
        # Extract to temp directory
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        return extract_dir

def run_quality_checks(package_path: str, app_id: str) -> Dict[str, Any]:
    """Run comprehensive quality checks"""
    
    checks = {
        'file_structure': check_file_structure(package_path),
        'documentation': check_documentation(package_path),
        'configuration': check_configuration(package_path),
        'security': check_security(package_path),
        'dependencies': check_dependencies(package_path),
        'code_quality': check_code_quality(package_path),
        'deployment_ready': check_deployment_readiness(package_path)
    }
    
    # Calculate overall score
    scores = [check['score'] for check in checks.values()]
    overall_score = sum(scores) / len(scores)
    
    return {
        'app_id': app_id,
        'overall_score': overall_score,
        'checks': checks,
        'checked_at': datetime.utcnow().isoformat()
    }

def check_file_structure(package_path: str) -> Dict[str, Any]:
    """Check if app has proper file structure"""
    
    score = 0
    issues = []
    recommendations = []
    
    # Check for essential files
    essential_files = ['README.md', 'package.json', 'requirements.txt', '.env.example']
    found_files = []
    
    for root, dirs, files in os.walk(package_path):
        for file in files:
            if file in essential_files:
                found_files.append(file)
                score += 20
    
    # Check for proper directory structure
    expected_dirs = ['src', 'client', 'server', 'docs', 'tests']
    found_dirs = []
    
    for root, dirs, files in os.walk(package_path):
        for dir_name in dirs:
            if dir_name in expected_dirs:
                found_dirs.append(dir_name)
                score += 10
    
    # Check for unwanted files
    unwanted_patterns = ['.git', 'node_modules', '__pycache__', '.DS_Store', '*.log']
    unwanted_found = []
    
    for root, dirs, files in os.walk(package_path):
        for item in dirs + files:
            for pattern in unwanted_patterns:
                if pattern.replace('*', '') in item:
                    unwanted_found.append(item)
                    score -= 5
    
    if not found_files:
        issues.append("No essential files found (README.md, package.json, etc.)")
        recommendations.append("Add proper documentation and configuration files")
    
    if unwanted_found:
        issues.append(f"Unwanted files/directories found: {', '.join(unwanted_found[:5])}")
        recommendations.append("Clean up development files before packaging")
    
    return {
        'score': max(0, min(100, score)),
        'issues': issues,
        'recommendations': recommendations,
        'details': {
            'essential_files_found': found_files,
            'directories_found': found_dirs,
            'unwanted_items': unwanted_found[:10]
        }
    }

def check_documentation(package_path: str) -> Dict[str, Any]:
    """Check documentation quality"""
    
    score = 0
    issues = []
    recommendations = []
    
    readme_path = os.path.join(package_path, 'README.md')
    
    if os.path.exists(readme_path):
        score += 30
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check README content quality
        required_sections = ['installation', 'usage', 'features', 'license']
        found_sections = []
        
        content_lower = content.lower()
        for section in required_sections:
            if section in content_lower:
                found_sections.append(section)
                score += 15
        
        # Check for code examples
        if '```' in content or '`' in content:
            score += 10
        else:
            recommendations.append("Add code examples to README")
        
        # Check length (should be substantial)
        if len(content) > 500:
            score += 10
        else:
            issues.append("README is too short")
            recommendations.append("Expand README with more detailed information")
            
        missing_sections = set(required_sections) - set(found_sections)
        if missing_sections:
            issues.append(f"Missing README sections: {', '.join(missing_sections)}")
            recommendations.append("Add missing documentation sections")
    else:
        issues.append("No README.md file found")
        recommendations.append("Create comprehensive README.md file")
    
    return {
        'score': max(0, min(100, score)),
        'issues': issues,
        'recommendations': recommendations,
        'details': {
            'readme_exists': os.path.exists(readme_path),
            'sections_found': found_sections if os.path.exists(readme_path) else []
        }
    }

def check_configuration(package_path: str) -> Dict[str, Any]:
    """Check configuration files"""
    
    score = 0
    issues = []
    recommendations = []
    
    # Check for environment configuration
    env_example = os.path.join(package_path, '.env.example')
    if os.path.exists(env_example):
        score += 25
    else:
        issues.append("No .env.example file found")
        recommendations.append("Add .env.example with required environment variables")
    
    # Check for package.json (Node.js projects)
    package_json = os.path.join(package_path, 'package.json')
    if os.path.exists(package_json):
        score += 25
        
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                
            # Check for essential fields
            essential_fields = ['name', 'version', 'description', 'scripts']
            for field in essential_fields:
                if field in package_data:
                    score += 5
                else:
                    issues.append(f"Missing {field} in package.json")
                    
        except Exception as e:
            issues.append("Invalid package.json format")
    
    # Check for requirements.txt (Python projects)
    requirements_txt = os.path.join(package_path, 'requirements.txt')
    if os.path.exists(requirements_txt):
        score += 25
        
        with open(requirements_txt, 'r') as f:
            requirements = f.read().strip()
            
        if not requirements:
            issues.append("requirements.txt is empty")
        else:
            score += 10
    
    # Check for Docker configuration
    dockerfile = os.path.join(package_path, 'Dockerfile')
    docker_compose = os.path.join(package_path, 'docker-compose.yml')
    
    if os.path.exists(dockerfile) or os.path.exists(docker_compose):
        score += 15
    else:
        recommendations.append("Consider adding Docker configuration for easier deployment")
    
    return {
        'score': max(0, min(100, score)),
        'issues': issues,
        'recommendations': recommendations,
        'details': {
            'env_example_exists': os.path.exists(env_example),
            'package_json_exists': os.path.exists(package_json),
            'requirements_txt_exists': os.path.exists(requirements_txt),
            'docker_config_exists': os.path.exists(dockerfile) or os.path.exists(docker_compose)
        }
    }

def check_security(package_path: str) -> Dict[str, Any]:
    """Check for security issues"""
    
    score = 100  # Start with perfect score, deduct for issues
    issues = []
    recommendations = []
    
    # Check for exposed secrets
    secret_patterns = [
        'api_key', 'secret_key', 'password', 'token', 'private_key',
        'aws_access_key', 'database_url'
    ]
    
    exposed_secrets = []
    
    for root, dirs, files in os.walk(package_path):
        # Skip certain directories
        if any(skip_dir in root for skip_dir in ['.git', 'node_modules', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.json', '.yml', '.yaml', '.env')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                    for pattern in secret_patterns:
                        if f'{pattern}=' in content or f'"{pattern}"' in content:
                            exposed_secrets.append(f"{file}: {pattern}")
                            score -= 10
                            
                except Exception:
                    continue
    
    if exposed_secrets:
        issues.append(f"Potential exposed secrets: {', '.join(exposed_secrets[:3])}")
        recommendations.append("Remove hardcoded secrets and use environment variables")
    
    # Check for .env file (should not be included)
    env_file = os.path.join(package_path, '.env')
    if os.path.exists(env_file):
        issues.append(".env file included in package")
        recommendations.append("Remove .env file and use .env.example instead")
        score -= 20
    
    # Check for proper .gitignore
    gitignore_path = os.path.join(package_path, '.gitignore')
    if os.path.exists(gitignore_path):
        score += 10
        
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            
        important_ignores = ['.env', 'node_modules', '__pycache__', '*.log']
        missing_ignores = []
        
        for ignore_pattern in important_ignores:
            if ignore_pattern not in gitignore_content:
                missing_ignores.append(ignore_pattern)
                
        if missing_ignores:
            recommendations.append(f"Add to .gitignore: {', '.join(missing_ignores)}")
    else:
        recommendations.append("Add .gitignore file")
    
    return {
        'score': max(0, min(100, score)),
        'issues': issues,
        'recommendations': recommendations,
        'details': {
            'exposed_secrets_count': len(exposed_secrets),
            'env_file_included': os.path.exists(env_file),
            'gitignore_exists': os.path.exists(gitignore_path)
        }
    }

def check_dependencies(package_path: str) -> Dict[str, Any]:
    """Check dependency management"""
    
    score = 0
    issues = []
    recommendations = []
    
    # Check Node.js dependencies
    package_json = os.path.join(package_path, 'package.json')
    if os.path.exists(package_json):
        score += 30
        
        # Check for package-lock.json
        package_lock = os.path.join(package_path, 'package-lock.json')
        if os.path.exists(package_lock):
            score += 20
        else:
            recommendations.append("Include package-lock.json for reproducible builds")
    
    # Check Python dependencies
    requirements_txt = os.path.join(package_path, 'requirements.txt')
    if os.path.exists(requirements_txt):
        score += 30
        
        with open(requirements_txt, 'r') as f:
            requirements = f.read().strip().split('\n')
            
        # Check for version pinning
        pinned_count = sum(1 for req in requirements if '==' in req)
        if pinned_count > len(requirements) * 0.8:
            score += 20
        else:
            recommendations.append("Pin dependency versions for reproducible builds")
    
    # Check for security vulnerabilities (basic check)
    vulnerable_packages = ['requests<2.20.0', 'flask<1.0', 'django<2.2']
    
    return {
        'score': max(0, min(100, score)),
        'issues': issues,
        'recommendations': recommendations,
        'details': {
            'package_json_exists': os.path.exists(package_json),
            'requirements_txt_exists': os.path.exists(requirements_txt)
        }
    }

def check_code_quality(package_path: str) -> Dict[str, Any]:
    """Basic code quality checks"""
    
    score = 70  # Start with decent score
    issues = []
    recommendations = []
    
    # Count files and estimate complexity
    code_files = []
    total_lines = 0
    
    for root, dirs, files in os.walk(package_path):
        if any(skip_dir in root for skip_dir in ['.git', 'node_modules', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        code_files.append((file, lines))
                except Exception:
                    continue
    
    if code_files:
        avg_file_size = total_lines / len(code_files)
        
        # Check for reasonable file sizes
        if avg_file_size < 500:
            score += 15
        elif avg_file_size > 1000:
            recommendations.append("Consider breaking down large files")
            score -= 10
    
    # Check for test files
    test_files = []
    for root, dirs, files in os.walk(package_path):
        for file in files:
            if 'test' in file.lower() or file.startswith('test_'):
                test_files.append(file)
    
    if test_files:
        score += 15
    else:
        recommendations.append("Add test files to improve code quality")
    
    return {
        'score': max(0, min(100, score)),
        'issues': issues,
        'recommendations': recommendations,
        'details': {
            'code_files_count': len(code_files),
            'total_lines': total_lines,
            'test_files_count': len(test_files)
        }
    }

def check_deployment_readiness(package_path: str) -> Dict[str, Any]:
    """Check if app is ready for deployment"""
    
    score = 0
    issues = []
    recommendations = []
    
    # Check for build scripts
    package_json = os.path.join(package_path, 'package.json')
    if os.path.exists(package_json):
        with open(package_json, 'r') as f:
            package_data = json.load(f)
            
        scripts = package_data.get('scripts', {})
        
        if 'build' in scripts:
            score += 20
        else:
            recommendations.append("Add build script to package.json")
            
        if 'start' in scripts:
            score += 20
        else:
            recommendations.append("Add start script to package.json")
    
    # Check for deployment configuration
    deployment_files = ['Dockerfile', 'docker-compose.yml', 'vercel.json', 'netlify.toml']
    found_deployment = []
    
    for file in deployment_files:
        if os.path.exists(os.path.join(package_path, file)):
            found_deployment.append(file)
            score += 15
    
    if not found_deployment:
        recommendations.append("Add deployment configuration (Dockerfile, vercel.json, etc.)")
    
    # Check for environment configuration
    env_example = os.path.join(package_path, '.env.example')
    if os.path.exists(env_example):
        score += 20
    else:
        issues.append("No .env.example for deployment configuration")
    
    # Check for production optimizations
    if os.path.exists(os.path.join(package_path, 'dist')) or os.path.exists(os.path.join(package_path, 'build')):
        score += 20
    else:
        recommendations.append("Include built/compiled assets for production")
    
    return {
        'score': max(0, min(100, score)),
        'issues': issues,
        'recommendations': recommendations,
        'details': {
            'deployment_files_found': found_deployment,
            'env_example_exists': os.path.exists(env_example)
        }
    }

def generate_quality_report(qa_results: Dict[str, Any]) -> str:
    """Generate human-readable quality report"""
    
    overall_score = qa_results['overall_score']
    
    if overall_score >= 90:
        grade = "A"
        status = "Excellent - Ready for premium pricing"
    elif overall_score >= 80:
        grade = "B"
        status = "Good - Ready for sale with minor improvements"
    elif overall_score >= 70:
        grade = "C"
        status = "Fair - Needs improvements before sale"
    else:
        grade = "D"
        status = "Poor - Significant work needed"
    
    report = f"""
# Quality Assurance Report

**Overall Score:** {overall_score:.1f}/100 (Grade: {grade})
**Status:** {status}

## Summary by Category

"""
    
    for category, results in qa_results['checks'].items():
        report += f"### {category.replace('_', ' ').title()}\n"
        report += f"**Score:** {results['score']}/100\n\n"
        
        if results['issues']:
            report += "**Issues:**\n"
            for issue in results['issues']:
                report += f"- {issue}\n"
            report += "\n"
        
        if results['recommendations']:
            report += "**Recommendations:**\n"
            for rec in results['recommendations']:
                report += f"- {rec}\n"
            report += "\n"
    
    report += f"""
## Next Steps

"""
    
    if overall_score >= 80:
        report += """
✅ **Ready for Sale!** Your app meets quality standards for commercial distribution.

**Recommended Actions:**
1. Generate professional documentation
2. Create Gumroad product listing
3. Set up customer support
4. Launch marketing campaign
"""
    else:
        report += """
⚠️ **Improvements Needed** before your app is ready for sale.

**Priority Actions:**
1. Address critical issues listed above
2. Improve documentation and configuration
3. Run quality check again
4. Consider professional code review
"""
    
    return report

def update_app_status(app_id: str, status: str, metadata: Dict[str, Any]) -> None:
    """Update app status in DynamoDB"""
    
    table = dynamodb.Table(os.environ['APP_TABLE'])
    
    table.put_item(
        Item={
            'app_id': app_id,
            'timestamp': datetime.utcnow().isoformat(),
            'status': status,
            'metadata': metadata
        }
    )

def trigger_next_step(app_id: str, result: str) -> None:
    """Trigger next step in the pipeline"""
    
    # This would trigger the next Lambda function or workflow
    # For now, we'll just log the result
    print(f"Quality check result for {app_id}: {result}")
    
    # You could trigger documentation generation, deployment, etc.
    if result == 'quality_passed':
        # Trigger documentation generation
        pass
    else:
        # Send notification about issues
        pass