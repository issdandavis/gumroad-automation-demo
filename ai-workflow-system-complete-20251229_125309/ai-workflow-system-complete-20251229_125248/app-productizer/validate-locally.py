#!/usr/bin/env python3
"""
Local Validation Script
Tests core functionality without AWS deployment
"""

import sys
import os
import json
from datetime import datetime

# Add lambda directories to path for testing
sys.path.append('lambda/doc_generator')
sys.path.append('lambda/qa_checker')
sys.path.append('lambda/gumroad_manager')

def test_documentation_generation():
    """Test documentation generation locally"""
    print("📝 Testing Documentation Generation...")
    
    try:
        from doc_generator import get_app_config, generate_fallback_documentation, create_professional_readme
        
        # Test with AI Workflow Architect
        app_config = get_app_config('ai_workflow_architect')
        
        if not app_config:
            print("❌ Failed to get app config")
            return False
        
        print(f"✅ App config loaded: {app_config['name']}")
        
        # Test documentation generation
        doc_result = generate_fallback_documentation(app_config)
        
        if not doc_result or len(doc_result.get('generated_content', '')) < 100:
            print("❌ Documentation generation failed")
            return False
        
        print("✅ Documentation generated successfully")
        
        # Test README creation
        readme = create_professional_readme('ai_workflow_architect', doc_result, app_config)
        
        if not readme or len(readme) < 500:
            print("❌ README creation failed")
            return False
        
        print("✅ Professional README created")
        
        # Save sample output
        with open('sample_readme.md', 'w') as f:
            f.write(readme)
        print("📄 Sample README saved to sample_readme.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
        return False

def test_quality_assessment():
    """Test quality assessment locally"""
    print("\n🔍 Testing Quality Assessment...")
    
    try:
        from qa_checker import check_file_structure, check_documentation, check_security, generate_quality_report
        
        # Test with current directory as sample
        test_path = "."
        
        # Test file structure check
        structure_result = check_file_structure(test_path)
        print(f"✅ File structure check: {structure_result['score']}/100")
        
        # Test documentation check
        doc_result = check_documentation(test_path)
        print(f"✅ Documentation check: {doc_result['score']}/100")
        
        # Test security check
        security_result = check_security(test_path)
        print(f"✅ Security check: {security_result['score']}/100")
        
        # Generate sample quality report
        qa_results = {
            'app_id': 'test_app',
            'overall_score': (structure_result['score'] + doc_result['score'] + security_result['score']) / 3,
            'checks': {
                'file_structure': structure_result,
                'documentation': doc_result,
                'security': security_result
            }
        }
        
        report = generate_quality_report(qa_results)
        
        # Save sample report
        with open('sample_quality_report.md', 'w') as f:
            f.write(report)
        print("📄 Sample quality report saved to sample_quality_report.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Quality assessment test failed: {e}")
        return False

def test_product_packaging():
    """Test product packaging locally"""
    print("\n📦 Testing Product Packaging...")
    
    try:
        from gumroad_manager import get_app_config, generate_product_listing, generate_commercial_license
        
        # Test with AI Workflow Architect
        app_config = get_app_config('ai_workflow_architect')
        documentation_url = "https://example.com/docs"
        
        # Test product listing generation
        product_data = generate_product_listing('ai_workflow_architect', app_config, documentation_url)
        
        if not product_data or not product_data.get('title'):
            print("❌ Product listing generation failed")
            return False
        
        print(f"✅ Product listing created: {product_data['title']}")
        print(f"   Price: ${product_data['price']}")
        print(f"   Category: {product_data['category']}")
        
        # Test license generation
        license_content = generate_commercial_license(app_config['name'])
        
        if not license_content or len(license_content) < 500:
            print("❌ License generation failed")
            return False
        
        print("✅ Commercial license generated")
        
        # Save sample outputs
        with open('sample_product_listing.json', 'w') as f:
            json.dump(product_data, f, indent=2)
        
        with open('sample_license.txt', 'w') as f:
            f.write(license_content)
        
        print("📄 Sample product listing saved to sample_product_listing.json")
        print("📄 Sample license saved to sample_license.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Product packaging test failed: {e}")
        return False

def test_pricing_logic():
    """Test pricing and positioning logic"""
    print("\n💰 Testing Pricing Logic...")
    
    try:
        from gumroad_manager import get_app_config
        
        apps = ['ai_workflow_architect', 'gumroad_automation', 'chat_archive']
        expected_prices = [199, 79, 39]
        
        for app_id, expected_price in zip(apps, expected_prices):
            config = get_app_config(app_id)
            actual_price = config.get('price', 0)
            
            if actual_price != expected_price:
                print(f"❌ Pricing mismatch for {app_id}: expected ${expected_price}, got ${actual_price}")
                return False
            
            print(f"✅ {config['name']}: ${actual_price} ({config['price_tier']} tier)")
        
        return True
        
    except Exception as e:
        print(f"❌ Pricing test failed: {e}")
        return False

def generate_validation_report(results):
    """Generate validation report"""
    print("\n📊 Validation Report")
    print("=" * 50)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Overall Score: {score:.1f}% ({passed_tests}/{total_tests} tests passed)")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Assessment:")
    if score >= 90:
        print("🟢 EXCELLENT: Core functionality works well")
        print("   Ready for AWS deployment and testing")
    elif score >= 75:
        print("🟡 GOOD: Most functionality works")
        print("   Minor issues to fix before deployment")
    elif score >= 50:
        print("🟠 FAIR: Significant issues found")
        print("   Major fixes needed before deployment")
    else:
        print("🔴 POOR: Core functionality broken")
        print("   Extensive development needed")
    
    print(f"\n💡 Realistic Expectations:")
    if score >= 75:
        print("   - System has potential but needs real-world testing")
        print("   - Start with $0 revenue goal and focus on validation")
        print("   - Get feedback from real users before any sales")
        print("   - Expect 2-4 weeks of refinement after deployment")
    else:
        print("   - System not ready for any revenue generation")
        print("   - Focus on fixing core functionality first")
        print("   - Don't deploy to AWS until local tests pass")
    
    # Save validation results
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'score': score,
        'results': results,
        'files_generated': [
            'sample_readme.md',
            'sample_quality_report.md', 
            'sample_product_listing.json',
            'sample_license.txt'
        ]
    }
    
    with open('validation_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Validation report saved to validation_report.json")

def main():
    """Run local validation tests"""
    print("🧪 App Productizer - Local Validation")
    print("=" * 50)
    print("Testing core functionality without AWS deployment...")
    
    results = {}
    
    # Run tests
    results['documentation_generation'] = test_documentation_generation()
    results['quality_assessment'] = test_quality_assessment()
    results['product_packaging'] = test_product_packaging()
    results['pricing_logic'] = test_pricing_logic()
    
    # Generate report
    generate_validation_report(results)
    
    print(f"\n🔍 Sample files generated for review:")
    print("   - sample_readme.md (professional documentation)")
    print("   - sample_quality_report.md (quality assessment)")
    print("   - sample_product_listing.json (Gumroad listing)")
    print("   - sample_license.txt (commercial license)")
    
    print(f"\n📋 Next Steps:")
    print("   1. Review generated sample files")
    print("   2. Check if quality meets your standards")
    print("   3. If satisfied, proceed with AWS deployment")
    print("   4. If not satisfied, adjust the code and re-test")

if __name__ == '__main__':
    main()