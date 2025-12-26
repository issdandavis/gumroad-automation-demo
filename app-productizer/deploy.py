#!/usr/bin/env python3
"""
Deployment script for App Productizer
"""

import subprocess
import sys
import os
import json

def main():
    """Deploy the App Productizer infrastructure"""
    
    print("🚀 App Productizer Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    install_dependencies()
    
    # Configure AWS CDK
    print("\n⚙️ Configuring AWS CDK...")
    configure_cdk()
    
    # Deploy infrastructure
    print("\n🏗️ Deploying infrastructure...")
    deploy_infrastructure()
    
    # Show next steps
    print("\n✅ Deployment completed!")
    show_next_steps()

def check_prerequisites():
    """Check if all prerequisites are met"""
    
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print("✅ Python version OK")
    
    # Check AWS CLI
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AWS CLI installed")
        else:
            print("❌ AWS CLI not found. Please install AWS CLI")
            return False
    except FileNotFoundError:
        print("❌ AWS CLI not found. Please install AWS CLI")
        return False
    
    # Check AWS credentials
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AWS credentials configured")
        else:
            print("❌ AWS credentials not configured. Run 'aws configure'")
            return False
    except Exception:
        print("❌ AWS credentials not configured. Run 'aws configure'")
        return False
    
    # Check Node.js (for CDK)
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Node.js installed")
        else:
            print("❌ Node.js not found. Please install Node.js")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        sys.exit(1)

def configure_cdk():
    """Configure AWS CDK"""
    
    # Install CDK CLI if not present
    try:
        result = subprocess.run(['cdk', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Installing AWS CDK CLI...")
            subprocess.run(['npm', 'install', '-g', 'aws-cdk'], check=True)
    except FileNotFoundError:
        print("Installing AWS CDK CLI...")
        subprocess.run(['npm', 'install', '-g', 'aws-cdk'], check=True)
    
    # Bootstrap CDK (if needed)
    try:
        print("Bootstrapping CDK...")
        subprocess.run(['cdk', 'bootstrap'], check=True)
        print("✅ CDK configured")
    except subprocess.CalledProcessError:
        print("⚠️ CDK bootstrap failed (may already be bootstrapped)")

def deploy_infrastructure():
    """Deploy the CDK infrastructure"""
    
    try:
        # Synthesize first to check for errors
        print("Synthesizing CDK app...")
        subprocess.run(['cdk', 'synth'], check=True)
        
        # Deploy
        print("Deploying infrastructure...")
        subprocess.run(['cdk', 'deploy', '--require-approval', 'never'], check=True)
        
        print("✅ Infrastructure deployed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

def show_next_steps():
    """Show next steps after deployment"""
    
    print("\n🎉 App Productizer is now deployed!")
    print("\n📋 Next Steps:")
    print("1. Configure your app settings in app.py")
    print("2. Add your API keys (Perplexity, Notion, Zapier)")
    print("3. Update GitHub repository URLs")
    print("4. Test the pipeline with a sample app")
    print("5. Start productizing your apps!")
    
    print("\n🔗 Useful Commands:")
    print("- View stack outputs: cdk outputs")
    print("- Update infrastructure: cdk deploy")
    print("- Destroy infrastructure: cdk destroy")
    
    print("\n📚 Documentation:")
    print("- README.md: Complete setup guide")
    print("- AWS Console: Check deployed resources")
    print("- CloudWatch: Monitor Lambda functions")

if __name__ == '__main__':
    main()